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


def _setup_skill_tree(tmp_path, graph):
    """Mirror the minimal repo tree the validator now needs (kb/ + modules/ + schema)."""
    import shutil
    kb_dir = tmp_path / "kb"
    kb_dir.mkdir()
    for n in graph["nodes"]:
        for f in n.get("kb_files", []):
            (kb_dir / f).touch()
    # Validator's check 7/8 read module frontmatter; copy real modules so the
    # enum coverage check sees real producers/consumers.
    shutil.copytree(REPO / "modules", tmp_path / "modules")
    (tmp_path / "graph.schema.json").write_text((REPO / "graph.schema.json").read_text())
    (tmp_path / "graph.json").write_text(json.dumps(graph))


def test_validator_accepts_well_formed_graph(tmp_path):
    """The actual graph.json should pass once KB files + modules exist."""
    graph = json.loads(GOOD_GRAPH.read_text())
    _setup_skill_tree(tmp_path, graph)
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode == 0, f"Expected success, got: {result.stderr}"


def test_validator_rejects_missing_target(tmp_path):
    """Edge with target=Nbogus should fail edge resolution check."""
    graph = json.loads(GOOD_GRAPH.read_text())
    graph["edges"][0]["target"] = "Nbogus"
    _setup_skill_tree(tmp_path, graph)
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "Edge resolution" in result.stderr or "Connectivity" in result.stderr


def test_validator_rejects_invalid_signal_field(tmp_path):
    """Edge with signal_field not in enum should fail."""
    graph = json.loads(GOOD_GRAPH.read_text())
    graph["edges"][1]["signal_field"] = "bogus_signal"
    _setup_skill_tree(tmp_path, graph)
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
    _setup_skill_tree(tmp_path, graph)
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "DAG check" in result.stderr


def test_validator_rejects_stale_dependency_signal(tmp_path):
    """Check 8: a module dependency that references a non-enum signal_field
    should fail. Simulates the B3 partial-fix regression where N12 still
    pointed at `verification_report` after the rename to `first_pass_verified`."""
    graph = json.loads(GOOD_GRAPH.read_text())
    _setup_skill_tree(tmp_path, graph)
    # Patch a copied module to inject a stale dependency
    n12 = tmp_path / "modules" / "N12-expand.md"
    text = n12.read_text().replace(
        '- "(N11, first_pass_verified)"',
        '- "(N11, verification_report)"',
    )
    n12.write_text(text)
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "verification_report" in result.stderr


def test_validator_rejects_dead_enum_entry(tmp_path):
    """Check 7: an enum entry with no producer/consumer should fail.
    Simulates the orphan `gate:S11_artifact_gap` entry that Pass 1 removed."""
    graph = json.loads(GOOD_GRAPH.read_text())
    graph["signal_field_enum"].append("dead_signal_xyz")
    _setup_skill_tree(tmp_path, graph)
    result = run_validator(tmp_path / "graph.json")
    assert result.returncode != 0
    assert "dead_signal_xyz" in result.stderr
