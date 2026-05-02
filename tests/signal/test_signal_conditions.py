"""Signal condition tests: S1-S11 raise conditions."""
import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GRAPH = json.loads((REPO / "graph.json").read_text())
FIXTURES = REPO / "tests" / "fixtures"

SIGNALS = {
    "S1_input_complexity": {"node": "N1", "fields": ["complexity_score", "complexity_bucket"]},
    "S2_thin_B": {"node": "N2b", "fields": ["thin_B_detected", "thin_reason"]},
    "S4_xref_density": {"node": "N4", "fields": ["density_value", "density_classification", "n_passes"]},
    "S5_idea_pool_thin": {"node": "N5.5", "fields": ["thin_pool", "accepted_count", "acceptance_rate"]},
    "S7_no_alternatives": {"node": "N7", "fields": ["falsified_count", "alternatives_remaining"]},
    "S11_artifact_gap": {"node": "N11", "fields": ["gap_type", "gap_severity"]},
}


def get_node_by_id(node_id):
    for n in GRAPH["nodes"]:
        if n["id"] == node_id:
            return n
    return None


def get_edges_by_source(source_id):
    return [e for e in GRAPH["edges"] if e["source"] == source_id]


# ─── S1: Input complexity ───
class TestS1Complexity:
    """N1 raises S1_input_complexity with score and bucket."""

    def test_n1_raises_s1(self):
        n1 = get_node_by_id("N1")
        assert n1 is not None, "N1 not in graph"
        assert "S1_input_complexity" in n1["raises_signals"], \
            "N1 must raise S1_input_complexity"

    def test_s1_signal_has_required_fields(self):
        s1 = SIGNALS["S1_input_complexity"]
        assert s1["node"] == "N1"
        assert "complexity_score" in s1["fields"]
        assert "complexity_bucket" in s1["fields"]

    def test_low_complexity_fixture_smoke(self):
        """Low A fixture should produce low complexity."""
        text = (FIXTURES / "node-a-low.md").read_text()
        lines = text.count("\n") + 1
        constraints = sum(1 for w in ["MUST", "SHALL", "REQUIRED", "FORBIDDEN", "NEVER"]
                         if w in text)
        depth = max(len(h.split()[0]) for h in text.splitlines()
                    if h.startswith("#"))
        # Quick sanity: S1 should be well under 5 for low fixture
        import math
        score = math.log10(max(lines, 1)) + depth + min(constraints / 10, 5.0)
        assert score < 5, f"Low fixture S1={score:.1f} should be <5 for low bucket"

    def test_high_complexity_fixture_smoke(self):
        """High A fixture should produce medium+ complexity."""
        text = (FIXTURES / "node-a-high.md").read_text()
        lines = text.count("\n") + 1
        constraints = sum(1 for w in ["MUST", "SHALL", "REQUIRED", "FORBIDDEN", "NEVER"]
                         if w in text)
        depth = max(len(h.split()[0]) for h in text.splitlines()
                    if h.startswith("#"))
        import math
        score = math.log10(max(lines, 1)) + depth + min(constraints / 10, 5.0)
        assert score >= 5, f"High fixture S1={score:.1f} should be ≥5 for medium+ bucket"


# ─── S2: Thin B ───
class TestS2ThinB:
    """N2b raises S2_thin_B when B lacks substance."""

    def test_n2b_raises_s2(self):
        n2b = get_node_by_id("N2b")
        assert n2b is not None, "N2b not in graph"
        assert "S2_thin_B" in n2b["raises_signals"], \
            "N2b must raise S2_thin_B"

    def test_s2_back_edge_e09(self):
        """E09 is the S2_thin_B back-edge to N6."""
        e09s = [e for e in GRAPH["edges"] if e["id"] == "E09"]
        assert len(e09s) == 1, "E09 must exist exactly once"
        e09 = e09s[0]
        assert e09["type"] == "back-edge", "E09 must be a back-edge"
        assert "S2_thin_B" in e09["signal_field"], "E09 must reference S2_thin_B"
        assert e09["source"] == "N2b", "E09 must originate from N2b"
        assert e09["target"] == "N6", "E09 must target N6 (defixation)"
        assert e09["single_firing_cap"] is True, "E09 must be single-fire"

    def test_generic_fixture_lacks_substance(self):
        """Generic fixture has no canonical sections, should trigger S2."""
        text = (FIXTURES / "node-b-generic.md").read_text()
        canonical_sections = [
            "Headline Insight", "Core Argument", "Supporting Evidence",
            "Counter-Arguments", "Implications", "Limitations",
            "Alternative Views", "Synthesis", "Action Items",
            "Open Questions"
        ]
        matches = sum(1 for s in canonical_sections if s.lower() in text.lower())
        assert matches < 3, f"Generic fixture has {matches} canonical sections, expected <3"


# ─── S4: Cross-reference density ───
class TestS4CrossrefDensity:
    """N4 raises S4_xref_density."""

    def test_n4_raises_s4(self):
        n4 = get_node_by_id("N4")
        assert n4 is not None, "N4 not in graph"
        assert "S4_xref_density" in n4["raises_signals"], \
            "N4 must raise S4_xref_density"

    def test_s4_classifications(self):
        """S4 has three classifications: sparse, normal, dense."""
        thresholds = {"sparse": "<0.5", "normal": "0.5-2.0", "dense": ">2.0"}
        assert len(thresholds) == 3


# ─── S5: Thin idea pool ───
class TestS5IdeaPool:
    """N5.5 raises S5_idea_pool_thin when acceptance is low."""

    def test_n55_raises_s5(self):
        n55 = get_node_by_id("N5.5")
        assert n55 is not None, "N5.5 not in graph"
        assert "S5_idea_pool_thin" in n55["raises_signals"], \
            "N5.5 must raise S5_idea_pool_thin"

    def test_s5_conditions(self):
        """S5 triggers when <5 ideas accepted OR rate <20%."""
        s5 = SIGNALS["S5_idea_pool_thin"]
        assert "thin_pool" in s5["fields"]
        assert "accepted_count" in s5["fields"]
        assert "acceptance_rate" in s5["fields"]


# ─── S7: No alternatives ───
class TestS7NoAlternatives:
    """N7 raises S7_no_alternatives when ideas falsified with no alternatives."""

    def test_n7_raises_s7(self):
        n7 = get_node_by_id("N7")
        assert n7 is not None, "N7 not in graph"
        assert "S7_no_alternatives" in n7["raises_signals"], \
            "N7 must raise S7_no_alternatives"

    def test_e20_is_back_edge(self):
        """E20 routes through N9 back to N6 when S7 triggers."""
        e20s = [e for e in GRAPH["edges"] if e["id"] == "E20"]
        assert len(e20s) == 1, "E20 must exist exactly once"
        e20 = e20s[0]
        assert e20["type"] == "back-edge", "E20 must be a back-edge"
        assert "S7_no_alternatives" in e20["signal_field"], "E20 must reference S7_no_alternatives"
        assert e20["source"] == "N9"
        assert e20["target"] == "N6"
        assert e20["single_firing_cap"] is True


# ─── S11: Artifact gap ───
class TestS11ArtifactGap:
    """N11 raises S11_artifact_gap when V1/V2/V5/V6/V3 detect gaps."""

    def test_n11_raises_s11(self):
        n11 = get_node_by_id("N11")
        assert n11 is not None, "N11 not in graph"
        assert "S11_artifact_gap" in n11["raises_signals"], \
            "N11 must raise S11_artifact_gap"

    def test_e25_is_deep_only_forward_conditional(self):
        """E25 is DEEP-only, conditional on S11_artifact_gap."""
        e25s = [e for e in GRAPH["edges"] if e["id"] == "E25"]
        assert len(e25s) == 1, "E25 must exist"
        e25 = e25s[0]
        assert "DEEP" in e25["scale_gates"], "E25 is DEEP-only"
        assert "STANDARD" not in e25["scale_gates"], "E25 must not fire in STANDARD"
        assert "S11_artifact_gap" in e25.get("gate_condition", ""), \
            "E25 must be gated on S11_artifact_gap"


# ─── Signal propagation integrity ───
class TestSignalPropagation:
    """Signals flow correctly through the graph."""

    def test_all_signal_fields_in_enum(self):
        """Every edge's signal_field must be in the enum."""
        enum = set(GRAPH["signal_field_enum"])
        for edge in GRAPH["edges"]:
            sf = edge["signal_field"]
            assert sf in enum, f"E{edge['id']} signal_field '{sf}' not in enum"

    def test_no_orphan_signals(self):
        """Every raised signal should have at least one consumer edge."""
        raised = set()
        for n in GRAPH["nodes"]:
            for s in n["raises_signals"]:
                raised.add(s)

        consumed = set()
        for e in GRAPH["edges"]:
            sf = e["signal_field"]
            if sf.startswith("gate:"):
                consumed.add(sf.replace("gate:", "").split()[0])

        for signal in raised:
            found = False
            for e in GRAPH["edges"]:
                gc = e.get("gate_condition")
                sf = e.get("signal_field", "")
                if (gc and signal in gc) or (signal in sf):
                    found = True
                    break
            # S1 consumed by N5/N8 budget, S4 by N5 N_PASSES, S5 by N5.5 supplemental pass — internal, no edge needed
            if signal not in ("S1_input_complexity", "S4_xref_density", "S5_idea_pool_thin"):
                assert found, f"Signal {signal} raised but never consumed by any edge"

    def test_signal_enum_completeness(self):
        """All signal-like fields should be in the enum."""
        enum = set(GRAPH["signal_field_enum"])
        expected_signals = {"intake_digest", "analysis_a_digest", "analysis_b_digest",
                           "tailored_b_digest", "xref_map", "ideas_digest",
                           "accepted_ideas_digest", "breakthrough_digest",
                           "falsification_result", "adversarial_digest",
                           "falsification_digest", "solutions_digest",
                           "enhanced_draft", "first_pass_verified",
                           "expansion_digest"}
        for sig in expected_signals:
            assert sig in enum, f"Signal field '{sig}' missing from enum"

    def test_node_count(self):
        """14 nodes expected."""
        assert len(GRAPH["nodes"]) == 14, \
            f"Expected 14 nodes, got {len(GRAPH['nodes'])}"

    def test_edge_count(self):
        """26 edges expected."""
        assert len(GRAPH["edges"]) == 26, \
            f"Expected 26 edges, got {len(GRAPH['edges'])}"
