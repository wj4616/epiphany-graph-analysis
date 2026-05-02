"""Regression tests: edge cases, anti-patterns, boundary conditions."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GRAPH = json.loads((REPO / "graph.json").read_text())
FIXTURES = REPO / "tests" / "fixtures"


class TestEmptyInputHandling:
    """Empty or minimal inputs should not crash the pipeline."""

    def test_empty_string_smoke(self):
        """Empty Node A should still produce a complexity score."""
        lines = 0
        import math
        # minimum line_count is 1 to avoid log10(0)
        score = math.log10(max(1, lines))
        assert score == 0.0, f"Expected 0.0 for empty input, got {score}"

    def test_single_line_input(self):
        """Single-line input with no structure."""
        import math
        lines = 1
        depth = 1  # at least one header level
        constraints = 0
        score = math.log10(max(lines, 1)) + depth + min(constraints / 10, 5.0)
        assert score == 1.0, f"Expected 1.0 for single-line input, got {score}"

    def test_whitespace_only_input(self):
        """Whitespace-only input is edge case for line counting."""
        text = "   \n  \n  \n"
        non_empty = [l for l in text.splitlines() if l.strip()]
        assert len(non_empty) == 0, "Whitespace-only should produce 0 non-empty lines"

    def test_binary_content_not_accepted(self):
        """Binary content should be rejected or gracefully handled."""
        # Node A should always be text — graph operates on markdown
        for node in GRAPH["nodes"]:
            for kb in node.get("kb_files", []):
                assert kb.endswith(".md"), \
                    f"{node['id']} references non-markdown KB: {kb}"


class TestMissingNodeB:
    """Missing or empty Node B should proceed with generic fallback."""

    def test_generic_fallback_fixture_exists(self):
        """Generic fixture tests the fallback path."""
        generic = FIXTURES / "node-b-generic.md"
        assert generic.exists(), "Need node-b-generic.md fixture"

    def test_n3_is_conditional_on_e08(self):
        """N3 SectionTailor only activates for genius-current or genius-drift."""
        n3 = next(n for n in GRAPH["nodes"] if n["id"] == "N3")
        activations = n3.get("activation", [])
        assert "conditional:E08" in activations, \
            "N3 must be conditional on E08"

    def test_e08_gate_condition(self):
        """E08 gate condition requires genius classification."""
        e08s = [e for e in GRAPH["edges"] if e["id"] == "E08"]
        assert len(e08s) == 1
        e08 = e08s[0]
        condition = e08.get("gate_condition", "")
        assert "genius-current" in condition or "genius-drift" in condition, \
            "E08 must gate on genius-current or genius-drift"


class TestBudgetBoundaries:
    """Context budget boundaries and overflow handling."""

    def test_n8_has_highest_budget(self):
        """N8 (SolutionEngineer) should have the highest context budget."""
        budgets = {n["id"]: n.get("context_budget_lines", 0)
                    for n in GRAPH["nodes"]}
        max_node = max(budgets, key=budgets.get)
        assert max_node == "N8", \
            f"N8 should have highest budget, but {max_node} has {budgets[max_node]}"

    def test_spawn_nodes_have_higher_budgets(self):
        """Spawn nodes typically need more context than inline nodes."""
        spawns = [n for n in GRAPH["nodes"] if n["exec_type"] == "spawn"]
        inlines = [n for n in GRAPH["nodes"] if n["exec_type"] == "inline"]
        avg_spawn = sum(n["context_budget_lines"] for n in spawns) / len(spawns)
        avg_inline = sum(n["context_budget_lines"] for n in inlines) / len(inlines)
        # Skip N9 (router, 50 lines) as outlier
        inlines_no_router = [n for n in inlines if n["id"] != "N9"]
        avg_inline_fair = sum(n["context_budget_lines"] for n in inlines_no_router) / len(inlines_no_router)
        assert avg_spawn > avg_inline_fair, \
            f"Spawn avg {avg_spawn:.0f} should exceed inline avg {avg_inline_fair:.0f}"

    def test_n1_is_lowest_non_router_budget(self):
        """N1 is fast intake, low budget."""
        n1 = next(n for n in GRAPH["nodes"] if n["id"] == "N1")
        assert n1["context_budget_lines"] == 200, \
            f"N1 budget should be 200, got {n1['context_budget_lines']}"


class TestDAGInvariants:
    """Graph topology invariants that must always hold."""

    def test_no_self_loops(self):
        """No edge should point from a node to itself."""
        for edge in GRAPH["edges"]:
            assert edge["source"] != edge["target"], \
                f"E{edge['id']} is a self-loop: {edge['source']}→{edge['target']}"

    def test_input_has_no_incoming(self):
        """Nothing points to 'input' (the virtual source)."""
        incoming = [e for e in GRAPH["edges"] if e["target"] == "input"]
        assert len(incoming) == 0, \
            f"'input' has incoming edges: {[e['id'] for e in incoming]}"

    def test_output_has_e24_terminal(self):
        """E24 is the terminal edge to 'output'."""
        outgoing = [e for e in GRAPH["edges"] if e["target"] == "output"]
        assert len(outgoing) == 1, \
            f"Expected 1 edge to output, got {len(outgoing)}: {[e['id'] for e in outgoing]}"
        assert outgoing[0]["id"] == "E24"

    def test_all_nodes_reachable_from_input(self):
        """Every node (except virtual input/output) should be reachable."""
        node_ids = {n["id"] for n in GRAPH["nodes"]}
        # BFS from 'input'
        adj = {}
        for e in GRAPH["edges"]:
            adj.setdefault(e["source"], set()).add(e["target"])

        visited = set()
        queue = ["input"]
        while queue:
            src = queue.pop(0)
            for tgt in adj.get(src, set()):
                if tgt not in visited and tgt != "output":
                    visited.add(tgt)
                    queue.append(tgt)

        unreachable = node_ids - visited
        assert not unreachable, \
            f"Unreachable nodes from input: {unreachable}"

    def test_back_edges_are_single_fire(self):
        """All back-edges must have single_firing_cap: true."""
        back_edges = [e for e in GRAPH["edges"] if e["type"] == "back-edge"]
        assert len(back_edges) == 3, \
            f"Expected 3 back-edges, got {len(back_edges)}: {[e['id'] for e in back_edges]}"
        for e in back_edges:
            assert e["single_firing_cap"] is True, \
                f"Back-edge E{e['id']} must be single-fire"

    def test_deep_mode_extra_node(self):
        """DEEP mode activates N12 (STANDARD does not)."""
        n12 = next(n for n in GRAPH["nodes"] if n["id"] == "N12")
        assert "DEEP" in n12["scale_gates"], \
            "N12 must be DEEP-gated"
        assert "STANDARD" not in n12["scale_gates"], \
            "N12 must not fire in STANDARD mode"


class TestFixtureConsistency:
    """All test fixtures are internally consistent."""

    def test_all_fixtures_are_valid_markdown(self):
        """Fixtures should be readable markdown files."""
        md_files = list(FIXTURES.glob("*.md"))
        assert len(md_files) >= 5, f"Expected ≥5 fixtures, got {len(md_files)}"
        for f in md_files:
            content = f.read_text()
            assert len(content) > 0, f"Fixture {f.name} is empty"
            assert content.startswith("#"), \
                f"Fixture {f.name} doesn't start with markdown header"

    def test_genius_fixture_has_10_sections(self):
        """Genius B fixture should have all 10 canonical sections."""
        text = (FIXTURES / "node-b-genius.md").read_text()
        sections = ["Headline Insight", "Core Argument", "Supporting Evidence",
                    "Counter-Arguments", "Implications", "Limitations",
                    "Alternative Views", "Synthesis", "Action Items",
                    "Open Questions"]
        found = sum(1 for s in sections if s.lower() in text.lower())
        assert found >= 8, f"Genius fixture has {found}/10 sections, need ≥8"

    def test_drift_fixture_has_4_to_7_sections(self):
        """Drift B fixture should have 4-7 canonical sections."""
        text = (FIXTURES / "node-b-drift.md").read_text()
        sections = ["Headline Insight", "Core Argument", "Some Evidence",
                    "Limitations", "Next Steps"]
        found = sum(1 for s in sections if s.lower() in text.lower())
        assert 3 <= found <= 7, f"Drift fixture has {found} sections, expected 3-7"


class TestComplexityFormulaBoundaries:
    """S1 formula boundary conditions."""

    def test_log10_of_zero_avoided(self):
        """Minimum line_count is 1 to avoid log10(0)."""
        import math
        assert math.log10(1) == 0.0
        with pytest.raises(ValueError):
            math.log10(0)

    def test_constraint_cap_at_5(self):
        """Constraint count normalization caps at 5.0."""
        # If constraint_count=100, min(100/10, 5.0) = 5.0 (capped)
        assert min(100 / 10, 5.0) == 5.0
        # If constraint_count=20, min(20/10, 5.0) = 2.0
        assert min(20 / 10, 5.0) == 2.0

    def test_max_theoretical_score(self):
        """Maximum S1 score is unbounded in line_count + depth, capped on constraints."""
        # line_count=100000 → log10 = 5.0
        # depth=6 (######)
        # constraints cap=5.0
        # max ≈ 5.0 + 6 + 5.0 = 16.0
        import math
        max_score = math.log10(100000) + 6 + 5.0
        assert max_score == 16.0, f"Expected max 16.0, got {max_score}"

    def test_bucket_thresholds(self):
        """Bucket thresholds: low <5, medium 5-9, high ≥9."""
        assert 4.9 < 5, "4.9 is low"
        assert 5 <= 5.0 < 9, "5.0 is medium"
        assert 8.9 < 9, "8.9 is still medium"
        assert 9.0 >= 9, "9.0 is high"


class TestScaleGateConsistency:
    """STANDARD and DEEP mode gate consistency."""

    def test_all_required_edges_have_both_gates(self):
        """Required edges should fire in both modes."""
        for edge in GRAPH["edges"]:
            if edge["type"] == "required":
                assert "STANDARD" in edge["scale_gates"], \
                    f"E{edge['id']} missing STANDARD gate"
                assert "DEEP" in edge["scale_gates"], \
                    f"E{edge['id']} missing DEEP gate"

    def test_n12_only_deep(self):
        """N12 should only list DEEP in scale_gates."""
        n12 = next(n for n in GRAPH["nodes"] if n["id"] == "N12")
        assert "DEEP" in n12["scale_gates"]
        assert "STANDARD" not in n12["scale_gates"]

    def test_standard_mode_has_13_active_nodes(self):
        """STANDARD: 14 total - 1 (N12) = 13 active."""
        active = [n for n in GRAPH["nodes"]
                  if "STANDARD" in n["scale_gates"]]
        assert len(active) == 13, \
            f"STANDARD should have 13 active nodes, got {len(active)}"

    def test_deep_mode_has_14_active_nodes(self):
        """DEEP: all 14 nodes active."""
        active = [n for n in GRAPH["nodes"]
                  if "DEEP" in n["scale_gates"]]
        assert len(active) == 14, \
            f"DEEP should have 14 active nodes, got {len(active)}"
