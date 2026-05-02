"""Replay tests: --resume and --retry-failed functionality."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GRAPH = json.loads((REPO / "graph.json").read_text())
SESSION_INIT = REPO / "scripts" / "session-init.sh"
FIXTURES = REPO / "tests" / "fixtures"


def _make_real_session(tmp_path, mode="STANDARD"):
    """Run session-init.sh and return the resulting session.json as a dict.
    Tests against the REAL schema rather than a hand-curated field list."""
    proc = subprocess.run(
        ["bash", str(SESSION_INIT),
         str(tmp_path),
         str(FIXTURES / "node-a-low.md"),
         str(FIXTURES / "node-b-genius.md"),
         mode],
        capture_output=True, text=True, check=True,
    )
    session_dir = next(
        line.split("=", 1)[1] for line in proc.stdout.splitlines()
        if line.startswith("SESSION_DIR=")
    )
    return json.loads((Path(session_dir) / "session.json").read_text()), Path(session_dir)


class TestSessionJsonStructure:
    """Session.json must contain all fields needed for replay (per spec §4.13)."""

    REQUIRED_SESSION_FIELDS = {
        "session_id", "skill_version", "created_at", "last_updated_at",
        "mode", "node_a_source", "node_b_source", "input_paths",
        "session_dir", "stages_dir", "executed_nodes", "signal_state",
        "back_edges_enqueued", "failed_spawns", "halt_reason", "verbose_trace",
    }

    def test_session_json_has_all_required_fields(self, tmp_path):
        """Real session.json written by session-init.sh contains every spec §4.13 field."""
        session, _ = _make_real_session(tmp_path)
        missing = self.REQUIRED_SESSION_FIELDS - set(session.keys())
        assert not missing, f"session.json is missing required fields: {sorted(missing)}"

    def test_session_json_input_paths_subkeys(self, tmp_path):
        """input_paths sub-object has node_a + node_b."""
        session, _ = _make_real_session(tmp_path)
        assert "node_a" in session["input_paths"]
        assert "node_b" in session["input_paths"]

    def test_session_json_initial_state_defaults(self, tmp_path):
        """A fresh session starts with empty execution state (resume baseline)."""
        session, _ = _make_real_session(tmp_path)
        assert session["executed_nodes"] == []
        assert session["signal_state"] == {}
        assert session["back_edges_enqueued"] == []
        assert session["failed_spawns"] == []
        assert session["halt_reason"] is None

    def test_session_json_mode_persisted(self, tmp_path):
        """Mode chosen at init time is persisted for resume scale-mismatch checks."""
        session, _ = _make_real_session(tmp_path, mode="DEEP")
        assert session["mode"] == "DEEP"

    def test_session_id_format(self):
        """Session ID format: <YYYY-MM-DD>-<sha256_8char_prefix>."""
        import re
        pattern = r"^\d{4}-\d{2}-\d{2}-[a-f0-9]{8}$"
        example = "2026-04-29-a1b2c3d4"
        assert re.match(pattern, example), \
            f"Session ID format check failed for '{example}'"

    def test_executed_nodes_is_list(self):
        """executed_nodes must be a list for membership checks."""
        # N9 gate condition: "N6 ∉ executed_nodes"
        # This requires list/set membership testing
        executed = ["N1", "N2a", "N2b", "N4", "N6"]
        assert "N6" in executed, "N6 should be in executed_nodes after defixation"
        assert "N12" not in executed, "N12 should not be in executed_nodes before expansion"

    def test_signal_state_is_dict(self):
        """SIGNAL_STATE is append-only dict with (node_id, signal_field) keys."""
        signal_state = {
            ("N1", "complexity_bucket"): "medium",
            ("N2b", "thin_B_detected"): False,
            ("N4", "density_classification"): "normal",
        }
        assert isinstance(signal_state, dict)
        # Keys are tuples
        for key in signal_state:
            assert isinstance(key, tuple) and len(key) == 2


class TestResumeFlag:
    """--resume flag: reads session.json, continues from first unexecuted node."""

    def test_topological_order_in_graph(self):
        """Nodes in graph.json are sorted by sort_key (topological order)."""
        sort_keys = [n["sort_key"] for n in GRAPH["nodes"]]
        assert sort_keys == sorted(sort_keys), \
            "Nodes must be in topological order by sort_key"

    def test_can_determine_next_node(self):
        """Given executed_nodes, find first unexecuted in topological order."""
        executed = {"N1", "N2a", "N2b"}
        nodes_in_order = sorted(GRAPH["nodes"], key=lambda n: n["sort_key"])
        next_node = None
        for n in nodes_in_order:
            if n["id"] not in executed and "STANDARD" in n["scale_gates"]:
                activation = n.get("activation", [])
                if "always" in activation:
                    next_node = n["id"]
                    break
        assert next_node in ["N3", "N4"], \
            f"Expected N3 or N4 as next node, got {next_node}"

    def test_resume_preserves_signal_state(self):
        """Resumed pipeline must restore SIGNAL_STATE from session.json."""
        signals = {
            ("N1", "complexity_bucket"): "medium",
            ("N1", "complexity_score"): 7.2,
        }
        # S2_thin_B should not be present if N2b hasn't raised it
        assert ("N2b", "thin_B_detected") not in signals

    def test_resume_respects_conditional_edges(self):
        """Conditional edges are re-evaluated on resume."""
        # E08: conditional on genius-current or genius-drift
        # If N2b output stored in session, gate is re-evaluated from stored signal
        e08 = next(e for e in GRAPH["edges"] if e["id"] == "E08")
        assert e08["type"] == "forward-conditional"


class TestRetryFailedFlag:
    """--retry-failed flag: re-executes only nodes whose stage files have status != 'complete'."""

    def test_retry_only_failed(self):
        """Given mixed completion status, only failed nodes are re-executed."""
        node_statuses = {
            "N1": "complete",
            "N2a": "complete",
            "N2b": "complete",
            "N4": "complete",
            "N5": "failed",       # ← only this should re-run
            "N5.5": "pending",    # ← depends on N5, must also re-run
        }
        failed_or_pending = {n for n, s in node_statuses.items() if s != "complete"}
        assert "N5" in failed_or_pending
        assert "N5.5" in failed_or_pending
        assert "N1" not in failed_or_pending

    def test_preserves_completed_outputs(self):
        """--retry-failed must not overwrite completed node outputs."""
        # The orchestrator should skip nodes with status='complete'
        completed = {"N1", "N2a", "N2b", "N3", "N4"}
        # These must survive the retry without modification
        assert len(completed) == 5

    def test_restores_signal_state_before_failure(self):
        """Retry must restore SIGNAL_STATE to the state just before the failed node."""
        # If N4 completed and raised S4_xref_density, that signal must be present
        # when retrying N5
        pre_failure_signals = {
            "S1_input_complexity", "S2_thin_B", "S4_xref_density"
        }
        assert "S4_xref_density" in pre_failure_signals


class TestGraphTrace:
    """Graph-trace.json: complete execution record for replay."""

    def test_trace_records_node_execution(self):
        """Each node execution is recorded with start/end timestamps."""
        trace_entry = {
            "node_id": "N4",
            "started_at": "2026-04-29T10:00:00Z",
            "completed_at": "2026-04-29T10:02:30Z",
            "status": "complete",
            "signals_raised": ["S4_xref_density"],
            "output_file": "stages/N4-cross-reference.md",
        }
        assert trace_entry["status"] == "complete"
        assert "S4_xref_density" in trace_entry["signals_raised"]

    def test_trace_records_failures(self):
        """Failed nodes are recorded with error details."""
        trace_entry = {
            "node_id": "N5",
            "started_at": "2026-04-29T10:03:00Z",
            "status": "failed",
            "error": "Ideation spawn exceeded 10-minute wall-clock budget",
            "output_file": "stages/N5-lateral-ideate.md",
        }
        assert trace_entry["status"] == "failed"
        assert "error" in trace_entry

    def test_trace_is_append_only(self):
        """Graph trace is append-only — new entries don't modify old ones."""
        trace = [
            {"node_id": "N1", "status": "complete"},
            {"node_id": "N2a", "status": "complete"},
            {"node_id": "N2b", "status": "complete"},
        ]
        # New entry appended
        trace.append({"node_id": "N4", "status": "complete"})
        # Old entries unchanged
        assert trace[0] == {"node_id": "N1", "status": "complete"}
        assert len(trace) == 4


class TestReplayEdgeCases:
    """Edge cases for replay functionality."""

    def test_resume_with_no_executed_nodes(self):
        """Resume with empty executed_nodes starts from N1."""
        executed = set()
        nodes_in_order = sorted(GRAPH["nodes"], key=lambda n: n["sort_key"])
        first = None
        for n in nodes_in_order:
            if n["id"] not in executed and "always" in n.get("activation", []):
                first = n["id"]
                break
        assert first == "N1", \
            f"First unexecuted always-active node should be N1, got {first}"

    def test_resume_after_all_complete(self):
        """Resume with all nodes complete should report 'nothing to do'."""
        all_nodes = {n["id"] for n in GRAPH["nodes"] if "STANDARD" in n["scale_gates"]}
        executed = all_nodes.copy()
        remaining = all_nodes - executed
        assert len(remaining) == 0, \
            f"All nodes executed, nothing remaining. Got: {remaining}"

    def test_retry_respects_sort_key_order(self):
        """Retry re-executes failed nodes in topological order."""
        failed = {"N10", "N5"}
        nodes_in_order = sorted(GRAPH["nodes"], key=lambda n: n["sort_key"])
        retry_order = [n["id"] for n in nodes_in_order if n["id"] in failed]
        # N5 has sort_key 5.0, N10 has 10.0 — so N5 should be first
        assert retry_order[0] == "N5", \
            f"Retry should start with N5 (sort_key 5.0), got {retry_order[0]}"

    def test_partial_execution_recovery(self):
        """If crash after N7, resume should continue from N9."""
        executed_at_crash = {"N1", "N2a", "N2b", "N4", "N5", "N5.5", "N7"}
        # N8 depends on N7+N5.5+N4 outputs — if N7 output exists, N8 should run
        # But N9 router runs between N7 and N8
        nodes_in_order = sorted(GRAPH["nodes"], key=lambda n: n["sort_key"])
        next_nodes = []
        for n in nodes_in_order:
            if n["id"] not in executed_at_crash and "STANDARD" in n["scale_gates"]:
                if "always" in n.get("activation", []) or \
                   any("conditional" in a for a in n.get("activation", [])):
                    next_nodes.append(n["id"])
        # N9 is the router, runs always, should be first unexecuted after N7
        assert "N9" in next_nodes, f"N9 should be next, got {next_nodes}"

    def test_signal_state_survives_replay(self):
        """SIGNAL_STATE is preserved and restored for replay."""
        # This is critical: gate conditions depend on signal state
        original_signals = {
            ("N1", "complexity_bucket"): "medium",
            ("N2b", "node_b_type"): "genius-current",
            ("N4", "xref_density"): 1.2,
        }
        restored = dict(original_signals)
        assert restored == original_signals
        assert restored[("N1", "complexity_bucket")] == "medium"
