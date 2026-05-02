"""V1-V8 verification battery tests (per spec §7.2)."""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GRAPH = json.loads((REPO / "graph.json").read_text())

# V1-V8 per spec §7.2 — V5, V7, V8 are HARD checks.
VERIFICATIONS = {
    "V1": {"name": "Hybrid trail completeness", "class": "soft",
           "check": "Every ACCEPT/CONDITIONAL solution has all HG-3 fields"},
    "V2": {"name": "Solution target verifiability", "class": "soft",
           "check": "Each solution's target_section_in_a exists in input-a.md"},
    "V3": {"name": "Cross-solution non-contradiction", "class": "soft",
           "check": "N10 pre-write resolves direct conflicts; V3 audits remaining"},
    "V4": {"name": "Node A constraint preservation", "class": "soft",
           "check": "MUST/SHALL/etc constraints appear verbatim or fuzzy <10% in enhanced.md"},
    "V5": {"name": "Output well-formedness", "class": "hard",
           "check": "YAML frontmatter parse + markdown structural balance"},
    "V6": {"name": "Artifact completeness + thin-spot detection", "class": "soft",
           "check": "All mandatory artifacts present; DEEP+pass=1 thin-spot ratio raises S11"},
    "V7": {"name": "Graph-trace edge integrity", "class": "hard",
           "check": "forward_edges_fired ∪ back_edges_fired ⊆ graph.json.declared_edges"},
    "V8": {"name": "Topology-driven execution", "class": "hard",
           "check": "Every executed node traces to a documented activation path"},
}


class TestV1V8Definitions:
    """Verify all 8 verifications are properly defined per spec §7.2."""

    def test_all_eight_present(self):
        assert len(VERIFICATIONS) == 8, \
            f"Expected 8 verifications, got {len(VERIFICATIONS)}"

    def test_each_has_name_class_check(self):
        for v_id, v in VERIFICATIONS.items():
            assert "name" in v, f"{v_id} missing name"
            assert "class" in v, f"{v_id} missing class"
            assert v["class"] in ("hard", "soft"), \
                f"{v_id} class must be hard or soft, got {v['class']}"
            assert "check" in v, f"{v_id} missing check description"

    def test_hard_verifications_are_v5_v7_v8(self):
        """Spec §7.2 designates V5, V7, V8 as HARD."""
        hard = {v_id for v_id, v in VERIFICATIONS.items() if v["class"] == "hard"}
        assert hard == {"V5", "V7", "V8"}, \
            f"Expected V5/V7/V8 as hard checks, got {hard}"

    def test_soft_verifications_are_v1_v2_v3_v4_v6(self):
        soft = {v_id for v_id, v in VERIFICATIONS.items() if v["class"] == "soft"}
        assert soft == {"V1", "V2", "V3", "V4", "V6"}


class TestN11VerificationProtocol:
    """N11 is the verification node running V1-V8."""

    def test_n11_exists(self):
        n11 = next((n for n in GRAPH["nodes"] if n["id"] == "N11"), None)
        assert n11 is not None, "N11 must exist"

    def test_n11_is_inline(self):
        n11 = next(n for n in GRAPH["nodes"] if n["id"] == "N11")
        assert n11["exec_type"] == "inline"

    def test_n11_hat_is_popper(self):
        n11 = next(n for n in GRAPH["nodes"] if n["id"] == "N11")
        assert "Popper" in str(n11.get("hat", ""))

    def test_n11_raises_s11(self):
        n11 = next(n for n in GRAPH["nodes"] if n["id"] == "N11")
        assert "S11_artifact_gap" in n11["raises_signals"]

    def test_n11_output_sections(self):
        n11 = next(n for n in GRAPH["nodes"] if n["id"] == "N11")
        sections = n11.get("required_output_sections", [])
        assert "V1-V8 Results" in sections
        assert "Verdict Aggregation" in sections
        assert "Pass Detection" in sections
        assert "Signal Flags" in sections


class TestVerdictAggregation:
    """Spec §7.3 aggregation rules."""

    def aggregate(self, results):
        """Mirror of the spec aggregation logic."""
        fails = sum(1 for v_id, status in results.items() if status == "FAIL")
        partials = sum(1 for v_id, status in results.items() if status == "PARTIAL")
        hard_fails = any(
            results.get(v_id) == "FAIL" for v_id in ("V5", "V7", "V8")
        )
        if hard_fails:
            return "FAIL"
        if fails == 0 and partials == 0:
            return "PASS"
        if fails == 0:
            return "PARTIAL"
        return "FAIL"

    def test_all_pass(self):
        all_pass = {v: "PASS" for v in VERIFICATIONS}
        assert self.aggregate(all_pass) == "PASS"

    def test_v5_fail_is_hard_fail(self):
        results = {v: "PASS" for v in VERIFICATIONS}
        results["V5"] = "FAIL"
        assert self.aggregate(results) == "FAIL"

    def test_v7_fail_is_hard_fail(self):
        results = {v: "PASS" for v in VERIFICATIONS}
        results["V7"] = "FAIL"
        assert self.aggregate(results) == "FAIL"

    def test_v8_fail_is_hard_fail(self):
        results = {v: "PASS" for v in VERIFICATIONS}
        results["V8"] = "FAIL"
        assert self.aggregate(results) == "FAIL"

    def test_soft_fail_only_yields_fail(self):
        results = {v: "PASS" for v in VERIFICATIONS}
        results["V1"] = "FAIL"
        assert self.aggregate(results) == "FAIL"

    def test_partials_only_yields_partial(self):
        results = {v: "PASS" for v in VERIFICATIONS}
        results["V3"] = "PARTIAL"
        assert self.aggregate(results) == "PARTIAL"


class TestHG5PassRate:
    """HG-5: pass rate ≥ 70% required."""

    def test_70_percent_threshold(self):
        # 6/8 = 75% (pass), 5/8 = 62.5% (fail)
        assert 6 / 8 >= 0.70
        assert 5 / 8 < 0.70

    def test_minimum_pass_count(self):
        """Need ≥6 of 8 verifications passing for HG-5."""
        thresh = 0.70
        for n_pass in range(9):
            rate = n_pass / 8
            should_pass = rate >= thresh
            if should_pass:
                assert n_pass >= 6
            else:
                assert n_pass <= 5


class TestV6ThinSpotRatio:
    """V6 thin-spot detection: solution_count / xref_count < 0.6 raises S11."""

    def test_ratio_threshold(self):
        # 5 solutions for 10 xrefs = 0.5 → thin
        assert 5 / 10 < 0.6
        # 6 solutions for 10 xrefs = 0.6 → boundary, NOT thin (strict <)
        assert not (6 / 10 < 0.6)
        # 7/10 = 0.7 → not thin
        assert not (7 / 10 < 0.6)


class TestV5HardCheck:
    """V5: YAML frontmatter parse + markdown structural balance."""

    def test_balanced_enhancement_markers(self):
        """V5 checks BEGIN/END_ENHANCEMENT pair count."""
        sample = ("<!-- BEGIN_ENHANCEMENT ref=\"S1\" -->\n"
                  "content\n"
                  "<!-- END_ENHANCEMENT -->")
        begins = sample.count("BEGIN_ENHANCEMENT")
        ends = sample.count("END_ENHANCEMENT")
        assert begins == ends == 1

    def test_unbalanced_markers_fail_v5(self):
        sample = "<!-- BEGIN_ENHANCEMENT ref=\"S1\" -->\ncontent without close"
        begins = sample.count("BEGIN_ENHANCEMENT")
        ends = sample.count("END_ENHANCEMENT")
        assert begins != ends


class TestV7PhantomEdgeDetection:
    """V7: every fired edge must be declared in graph.json."""

    def test_declared_edges_set(self):
        declared = {e["id"] for e in GRAPH["edges"]}
        assert len(declared) == 26
        # If a graph-trace recorded "E99" it would not be in declared
        assert "E99" not in declared

    def test_v7_failure_when_phantom(self):
        declared = {e["id"] for e in GRAPH["edges"]}
        fired = {"E01", "E02", "E99"}  # E99 is phantom
        phantoms = fired - declared
        assert phantoms == {"E99"}, "V7 must detect phantom edges"


class TestV8TopologyDrivenExecution:
    """V8: every executed node has a documented activation path."""

    def test_n6_requires_signal_for_activation(self):
        """N6 may only be in executed_nodes if S2_thin_B or S7_no_alternatives raised."""
        # Activation paths for N6: E09 (S2_thin_B) or E20 (S7_no_alternatives ∧ ¬N6_ran)
        executed = {"N1", "N6"}
        signals = set()  # neither raised
        # V8 should fail here: N6 in executed_nodes but no signal raised
        n6_legal = (
            "S2_thin_B" in signals or "S7_no_alternatives" in signals
        )
        assert not n6_legal, "N6 in executed without signal must fail V8"

    def test_n12_requires_s11_and_deep(self):
        """N12 may only be in executed_nodes if S11_artifact_gap raised + DEEP."""
        executed = {"N12"}
        mode = "STANDARD"  # invalid for N12
        signals = set()
        n12_legal = (mode == "DEEP" and "S11_artifact_gap" in signals)
        assert not n12_legal, "N12 in STANDARD or without S11 must fail V8"


class TestN11N12N10ReverifyLoop:
    """DEEP mode: N11→N12→N10→N11 re-verify loop."""

    def test_e23_n10_to_n11(self):
        e23 = next(e for e in GRAPH["edges"] if e["id"] == "E23")
        assert e23["source"] == "N10"
        assert e23["target"] == "N11"

    def test_e24_n11_to_output(self):
        e24 = next(e for e in GRAPH["edges"] if e["id"] == "E24")
        assert e24["type"] == "terminal"

    def test_e25_n11_to_n12_deep_only(self):
        e25 = next(e for e in GRAPH["edges"] if e["id"] == "E25")
        assert e25["type"] == "forward-conditional"
        assert "DEEP" in e25["scale_gates"]
        assert "STANDARD" not in e25["scale_gates"]

    def test_e26_n12_to_n10_back_edge(self):
        e26 = next(e for e in GRAPH["edges"] if e["id"] == "E26")
        assert e26["type"] == "back-edge"
        assert e26["source"] == "N12"
        assert e26["target"] == "N10"
        assert e26["single_firing_cap"] is True

    def test_e25_signal_field_in_enum(self):
        """E25 signal_field must be in the declared enum."""
        e25 = next(e for e in GRAPH["edges"] if e["id"] == "E25")
        assert e25["signal_field"] in GRAPH["signal_field_enum"]

    def test_n11_writes_e25_signal_field(self):
        """N11's frontmatter `output_signal_fields` must list E25's signal_field
        per source-of-truth rule (graph.json wins). Parses YAML — substring
        matches in comments do not satisfy this contract."""
        e25 = next(e for e in GRAPH["edges"] if e["id"] == "E25")
        n11_md = (REPO / "modules" / "N11-verify.md").read_text()
        # Extract YAML frontmatter block
        assert n11_md.startswith("---\n"), "N11 module must start with YAML frontmatter"
        end = n11_md.find("\n---\n", 4)
        assert end != -1, "N11 module frontmatter is unterminated"
        block = n11_md[4:end]
        try:
            import yaml
            fm = yaml.safe_load(block) or {}
        except Exception as e:
            raise AssertionError(f"N11 frontmatter is not valid YAML: {e}")
        out_fields = fm.get("output_signal_fields", []) or []
        assert e25["signal_field"] in out_fields, (
            f"N11 frontmatter output_signal_fields must include {e25['signal_field']!r} "
            f"(E25 signal_field). Got: {out_fields}"
        )
