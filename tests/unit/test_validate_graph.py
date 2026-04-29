"""Unit tests for validate-graph.py PRC1 checks."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "scripts" / "validate-graph.py"
GOOD_GRAPH = REPO / "graph.json"


def run_validator(graph_path):
    return subprocess.run(
        ["python3", str(VALIDATOR), str(graph_path)],
        capture_output=True, text=True
    )


def test_validator_accepts_well_formed_graph(tmp_path):
    """The actual graph.json should pass once KB files exist (KB stubbed in this test)."""
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    skill_dir = tmp_path
    # Copy schema and graph
    (skill_dir / "graph.schema.json").write_text((REPO / "graph.schema.json").read_text())
    graph = json.loads(GOOD_GRAPH.read_text())
    for n in graph["nodes"]:
        for f in n.get("kb_files", []):
            (kb_dir / f).touch()
    (skill_dir / "graph.json").write_text(json.dumps(graph))
    result = run_validator(skill_dir / "graph.json")
    assert result.returncode == 0, f"Expected success, got: {result.stderr}"


def test_validator_rejects_missing_target(tmp_path):
    """Edge with target=Nbogus should fail edge resolution check."""
    graph = json.loads(GOOD_GRAPH.read_text())
    graph["edges"][0]["target"] = "Nbogus"
    (tmp_path / "graph.json").write_text(json.dumps(graph))
    (tmp_path / "graph.schema.json").write_text((REPO / "graph.schema.json").read_text())
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "Edge resolution" in result.stderr or "Connectivity" in result.stderr


def test_validator_rejects_invalid_signal_field(tmp_path):
    """Edge with signal_field not in enum should fail."""
    graph = json.loads(GOOD_GRAPH.read_text())
    graph["edges"][1]["signal_field"] = "bogus_signal"
    (tmp_path / "graph.json").write_text(json.dumps(graph))
    (tmp_path / "graph.schema.json").write_text((REPO / "graph.schema.json").read_text())
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "Signal field" in result.stderr


def test_validator_rejects_cycle(tmp_path):
    """Adding a forward (non-back-edge) cycle should fail DAG check."""
    graph = json.loads(GOOD_GRAPH.read_text())
    # Add a cycle: N10 -> N1 (which would create a forward cycle)
    graph["edges"].append({
        "id": "E99", "source": "N10", "target": "N1",
        "type": "required", "signal_field": "intake_digest",
        "scale_gates": ["STANDARD", "DEEP"],
        "gate_condition": None, "single_firing_cap": False
    })
    (tmp_path / "graph.json").write_text(json.dumps(graph))
    (tmp_path / "graph.schema.json").write_text((REPO / "graph.schema.json").read_text())
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "DAG check" in result.stderr
