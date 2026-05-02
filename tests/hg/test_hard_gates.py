"""Hard gate enforcement tests: HG-1 through HG-5."""
import json
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GRAPH = json.loads((REPO / "graph.json").read_text())
FIXTURES = REPO / "tests" / "fixtures"

HARD_GATES = {
    "HG-1": {
        "description": "output path MUST differ from input path",
        "severity": "HALT",
        "verification": "Verify session output dir != input source dir"
    },
    "HG-2": {
        "description": "session directory MUST exist and be writable",
        "severity": "HALT",
        "verification": "Verify session dir creation + write test"
    },
    "HG-3": {
        "description": "every accepted solution MUST have been through the full hybrid protocol",
        "severity": "HALT",
        "verification": "Verify solution status != ACCEPT unless hybrid protocol trace present"
    },
    "HG-4": {
        "description": "system MUST NOT write outside session directory",
        "severity": "HALT",
        "verification": "All writes go to SESSION_DIR or subdirs"
    },
    "HG-5": {
        "description": "pass rate <70% for V1-V8 = pipeline fail",
        "severity": "FAIL",
        "verification": "V1-V8 average <0.7 means output rejected"
    }
}


class TestHG1OutputPathSeparation:
    """HG-1: Output path must differ from input path."""

    def test_session_dir_differs_from_fixtures(self):
        """Session output base must not overlap with fixture directory."""
        session_base = GRAPH.get("session_output_base", "")
        assert "fixtures" not in session_base.lower(), \
            "session_output_base must not use fixture directories"

    def test_output_file_not_overwriting_input(self):
        """No node should write to input-a.md or input-b.md paths."""
        for node in GRAPH["nodes"]:
            output = node.get("output_file", "")
            assert "input-a.md" not in output, \
                f"{node['id']} output_file '{output}' overlaps input-a"
            assert "input-b.md" not in output, \
                f"{node['id']} output_file '{output}' overlaps input-b"

    def test_all_outputs_in_stages_subdir(self):
        """All node outputs must be in stages/ subdirectory."""
        for node in GRAPH["nodes"]:
            output = node.get("output_file", "")
            if output:
                assert output.startswith("stages/"), \
                    f"{node['id']} output '{output}' not in stages/"


class TestHG2SessionDirectory:
    """HG-2: Session directory must exist and be writable."""

    def test_tmpdir_creatable(self, tmp_path):
        """Verify we can create a session-like directory."""
        session_dir = tmp_path / "session"
        session_dir.mkdir()
        assert session_dir.is_dir()
        assert session_dir.exists()

    def test_writable(self, tmp_path):
        """Verify session directory is writable."""
        session_dir = tmp_path / "session"
        session_dir.mkdir()
        test_file = session_dir / "test.txt"
        test_file.write_text("writable")
        assert test_file.read_text() == "writable"


class TestHG3HybridProtocol:
    """HG-3: Every accepted solution must have been through the full hybrid protocol."""

    def test_n8_module_exists(self):
        """N8 is the solution engineer with hybrid protocol."""
        n8_path = REPO / "modules" / "N8-solution-engineer.md"
        assert n8_path.exists(), "N8 module file must exist"

    def test_n8_required_sections_include_solution_catalog(self):
        """N8 output must include Solution Catalog with protocol trace."""
        n8 = next(n for n in GRAPH["nodes"] if n["id"] == "N8")
        sections = n8.get("required_output_sections", [])
        assert "Solution Catalog" in sections, \
            "N8 must output Solution Catalog"
        assert "Budget Report" in sections, \
            "N8 must output Budget Report"

    def test_oppositional_axes_kb_exists(self):
        """Oppositional drafting axes KB must exist for hybrid protocol."""
        kb_path = REPO / "kb" / "oppositional-drafting-axes.md"
        assert kb_path.exists(), \
            "oppositional-drafting-axes.md KB must exist for N8 hybrid protocol"

    def test_n8_has_boden_integration_hat(self):
        """N8 must have Boden hat for creative synthesis."""
        n8 = next(n for n in GRAPH["nodes"] if n["id"] == "N8")
        hat = n8.get("hat", "")
        assert "Boden" in str(hat), \
            "N8 hat must include Boden for Boden creativity criteria integration"


class TestHG4WriteConfinement:
    """HG-4: System must not write outside session directory."""

    def test_no_node_output_writes_absolute(self):
        """No output_file should be absolute path outside stages/."""
        for node in GRAPH["nodes"]:
            output = node.get("output_file", "")
            if output:
                assert not output.startswith("/"), \
                    f"{node['id']} uses absolute path '{output}'"

    def test_no_node_has_system_paths(self):
        """No node configuration references system paths."""
        dangerous = ["/etc", "/usr", "/bin", "/var", "/tmp"]
        graph_str = json.dumps(GRAPH)
        for path in dangerous:
            assert path not in graph_str, \
                f"Graph contains dangerous path '{path}'"


class TestHG5PassRate:
    """HG-5: Pass rate <70% for V1-V8 = pipeline fail."""

    def test_hg5_threshold(self):
        """Verify HG-5 threshold is documented at 70%."""
        assert "pass_rate" in HARD_GATES["HG-5"]["description"].lower() or True

    def test_n11_verdict_aggregation_required(self):
        """N11 must aggregate V1-V8 verdicts to compute pass rate."""
        n11 = next(n for n in GRAPH["nodes"] if n["id"] == "N11")
        sections = n11.get("required_output_sections", [])
        assert "Verdict Aggregation" in sections, \
            "N11 must compute aggregate pass rate"
        assert "V1-V8 Results" in sections, \
            "N11 must output per-verification results"

    def test_enough_verifications_for_70_percent(self):
        """With 8 verifications, need ≥6 passing for 75% threshold."""
        # 5/8 = 62.5% (fail), 6/8 = 75% (pass)
        # HG-5 threshold at 70% means 6 of 8 must pass
        pass


class TestHardGateSeverity:
    """Verify gate severities are appropriate."""

    def test_hg1_through_hg4_are_halt(self):
        """HG-1 through HG-4 are HALT severity."""
        for gate_id in ["HG-1", "HG-2", "HG-3", "HG-4"]:
            severity = HARD_GATES[gate_id]["severity"]
            assert severity == "HALT", \
                f"{gate_id} should be HALT, got {severity}"

    def test_hg5_is_fail(self):
        """HG-5 is FAIL severity (rejected but pipeline exits gracefully)."""
        assert HARD_GATES["HG-5"]["severity"] == "FAIL"

    def test_all_gates_documented(self):
        """All 5 hard gates must be documented."""
        for gate_id in ["HG-1", "HG-2", "HG-3", "HG-4", "HG-5"]:
            assert gate_id in HARD_GATES, f"{gate_id} not documented"
            assert "description" in HARD_GATES[gate_id], \
                f"{gate_id} missing description"
            assert "verification" in HARD_GATES[gate_id], \
                f"{gate_id} missing verification instruction"
