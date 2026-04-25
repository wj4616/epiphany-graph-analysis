#!/usr/bin/env python3
"""
validate-graph.py — epiphany-graph-analysis v1.0.0

Mechanizes PRC1 validation plus KB-file existence checks and graph.json schema
validation against `graph.schema.json`.

Usage:
    python3 validate-graph.py [graph_file] [--scale {MINIMAL|STANDARD|DEEP}]

If graph_file is omitted, defaults to ../graph.json relative to this script.
Exit 0 = all checks pass. Exit 1 = at least one check failed.

--scale runs PRC1.1–PRC1.4 against the scale-filtered active subgraph
(matching the orchestrator's STEP 0.2 filter). Without --scale, checks run
on the full unfiltered graph (legacy behavior). For CI, run all three scale
combinations: MINIMAL, STANDARD, DEEP.

Checks:
  PRC1.1  DAG check (topological sort over non-back-edge, non-forward-conditional subgraph)
  PRC1.2  Edge resolution (every edge source/target resolves)
  PRC1.3  Signal-field validity (digest names + gate literals + em-dash sentinel)
  PRC1.4  Connectivity (N1 reachable to output via active subgraph)
  I3      KB-file existence (every node's kb_files resolves under kb/)
  L4      Graph schema validation (basic structural checks; full JSON schema
          validation if `jsonschema` package is installed and graph.schema.json
          is present)

Back-edges excluded from DAG check: E06 (N2→N6, S2_thin_B),
E16 (N9→N6, S7_no_alternatives), E20 (N12→N10, expansion).
Forward-conditional edges excluded from DAG (they may not fire): E04, E19.

Designed to be re-runnable safely; no side effects beyond stdout.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path

# Declared digest names for epiphany-graph-analysis.
# These are the valid signal_field values for edges (aside from gate literals
# and the em-dash sentinel).
DECLARED_DIGESTS = {
    "intake_digest",
    "analysis_digest",
    "tailored_B1",
    "xref_map",
    "ideas_digest",
    "breakthrough_digest",
    "falsification_result",
    "adversarial_digest",
    "falsification_digest",
    "solutions_digest",
    "enhanced_draft",
    "first_pass_verified",
    "verification_report",
    "expansion_digest",
}

# Back-edge IDs: excluded from DAG topological sort and cycle detection.
# These carry explicit enqueue semantics rather than standard ready-set activation.
BACK_EDGE_IDS = {"E06", "E16", "E20"}

# Forward-conditional edge IDs: excluded from DAG (they may not fire
# depending on gate_condition evaluation at runtime).
FORWARD_CONDITIONAL_IDS = {"E04", "E19"}

VALID_SCALES = {"MINIMAL", "STANDARD", "DEEP"}
VALID_EDGE_TYPES = {
    "required",
    "optional",
    "back-edge",
    "forward-conditional",
    "gate-open",
    "terminal",
}
VALID_EXEC_TYPES = {"inline", "spawn"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(msg)


def load_graph(graph_path: Path) -> dict:
    if not graph_path.exists():
        fail(f"graph.json not found: {graph_path}")
        sys.exit(1)
    with open(graph_path) as f:
        return json.load(f)


def check_schema(graph: dict, errors: list[str]) -> None:
    """L4: structural / type checks. Falls back to jsonschema if available."""
    if not isinstance(graph, dict):
        errors.append("graph.json must be a JSON object")
        return
    if "nodes" not in graph or not isinstance(graph["nodes"], list):
        errors.append("graph.nodes missing or not a list")
        return
    if "edges" not in graph or not isinstance(graph["edges"], list):
        errors.append("graph.edges missing or not a list")
        return

    seen_node_ids: set[str] = set()
    for i, n in enumerate(graph["nodes"]):
        if "id" not in n:
            errors.append(f"nodes[{i}] missing 'id'")
            continue
        if n["id"] in seen_node_ids:
            errors.append(f"duplicate node id: {n['id']}")
        seen_node_ids.add(n["id"])
        if n.get("exec_type") not in VALID_EXEC_TYPES:
            errors.append(f"node {n['id']}: exec_type must be one of {VALID_EXEC_TYPES}")
        for sg in n.get("scale_gates", []):
            if sg not in VALID_SCALES:
                errors.append(f"node {n['id']}: invalid scale_gate '{sg}'")
        if "output_file" not in n:
            errors.append(f"node {n['id']}: missing output_file")
        if not isinstance(n.get("required_output_sections", []), list):
            errors.append(f"node {n['id']}: required_output_sections must be a list")

    seen_edge_ids: set[str] = set()
    for i, e in enumerate(graph["edges"]):
        if "id" not in e:
            errors.append(f"edges[{i}] missing 'id'")
            continue
        if e["id"] in seen_edge_ids:
            errors.append(f"duplicate edge id: {e['id']}")
        seen_edge_ids.add(e["id"])
        if e.get("type") not in VALID_EDGE_TYPES:
            errors.append(f"edge {e['id']}: type must be one of {VALID_EDGE_TYPES}")
        for sg in e.get("scale_gates", []):
            if sg not in VALID_SCALES:
                errors.append(f"edge {e['id']}: invalid scale_gate '{sg}'")

    # Optional: full schema validation if jsonschema is installed
    schema_path = Path(__file__).resolve().parent.parent / "graph.schema.json"
    if schema_path.exists():
        try:
            import jsonschema  # type: ignore
            with open(schema_path) as f:
                schema = json.load(f)
            try:
                jsonschema.validate(graph, schema)
            except jsonschema.ValidationError as exc:
                errors.append(
                    f"jsonschema validation failed: {exc.message} (path: {list(exc.path)})"
                )
        except ImportError:
            # jsonschema not installed — structural checks above are still applied.
            pass


def check_edge_resolution(graph: dict, errors: list[str]) -> None:
    """PRC1.2: every edge's source/target resolves to a declared node or
    'input' / 'output' sentinel."""
    node_ids = {n["id"] for n in graph["nodes"]}
    valid_sources = node_ids | {"input"}
    valid_targets = node_ids | {"output"}
    for e in graph["edges"]:
        if e["source"] not in valid_sources:
            errors.append(f"edge {e['id']}: source '{e['source']}' is not a declared node")
        if e["target"] not in valid_targets:
            errors.append(f"edge {e['id']}: target '{e['target']}' is not a declared node")


def check_signal_fields(graph: dict, errors: list[str]) -> None:
    """PRC1.3: every signal_field is a declared digest name, a gate literal,
    or the em-dash sentinel."""
    for e in graph["edges"]:
        sf = e.get("signal_field", "")
        if sf == "—" or sf == "":
            continue
        if sf.startswith("gate:"):
            continue
        if sf not in DECLARED_DIGESTS:
            errors.append(
                f"edge {e['id']}: signal_field '{sf}' is not a declared digest name "
                f"(declared: {sorted(DECLARED_DIGESTS)})"
            )


def check_dag(graph: dict, errors: list[str]) -> None:
    """PRC1.1: topological sort over the non-back-edge, non-forward-conditional
    subgraph must visit every active node.

    Back-edges (E06, E16, E20) are excluded because they require explicit enqueue.
    Forward-conditional edges (E04, E19) are excluded because they may not fire.
    The remaining subgraph must be a DAG."""
    node_ids = {n["id"] for n in graph["nodes"]}
    excluded = BACK_EDGE_IDS | FORWARD_CONDITIONAL_IDS
    incoming: dict[str, set[str]] = {nid: set() for nid in node_ids}

    for e in graph["edges"]:
        if e["id"] in excluded:
            continue
        if e.get("type") in ("back-edge", "forward-conditional"):
            continue
        src, tgt = e["source"], e["target"]
        if src in node_ids and tgt in node_ids:
            incoming[tgt].add(src)

    # Kahn's algorithm
    ready = deque(nid for nid, preds in incoming.items() if not preds)
    visited: list[str] = []
    while ready:
        nid = ready.popleft()
        visited.append(nid)
        for other, preds in incoming.items():
            if nid in preds:
                preds.discard(nid)
                if not preds and other not in visited and other not in ready:
                    ready.append(other)

    unvisited = node_ids - set(visited)
    if unvisited:
        errors.append(
            f"DAG check failed — cycle or orphan suspected. Unvisited nodes: {sorted(unvisited)}"
        )


def check_connectivity(graph: dict, errors: list[str]) -> None:
    """PRC1.4: with all edge types INCLUDED for connectivity, every node must be
    reachable from N1. Also require a path to the 'output' sentinel (via N10's
    terminal edge E21)."""
    node_ids = {n["id"] for n in graph["nodes"]}
    if "N1" not in node_ids:
        errors.append("connectivity check skipped — N1 missing from graph")
        return

    adj: dict[str, set[str]] = defaultdict(set)
    has_output_edge = False
    for e in graph["edges"]:
        if e["source"] in node_ids and e["target"] in node_ids:
            adj[e["source"]].add(e["target"])
        elif e["source"] in node_ids and e["target"] == "output":
            adj[e["source"]].add("__output__")
            has_output_edge = True

    # BFS from N1
    visited = {"N1"}
    queue = deque(["N1"])
    while queue:
        cur = queue.popleft()
        for nxt in adj.get(cur, set()):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)

    unreachable = node_ids - visited
    if unreachable:
        errors.append(
            f"connectivity check: nodes unreachable from N1: {sorted(unreachable)}"
        )
    if not has_output_edge:
        errors.append(
            "connectivity check: no edge with target='output' present in active subgraph"
        )
    elif "__output__" not in visited:
        errors.append(
            "connectivity check: no path from N1 to 'output' sentinel"
        )


def filter_active_subgraph(graph: dict, scale: str | None) -> dict:
    """Produce a scale-filtered active subgraph mirroring SKILL.md STEP 0.2.
    Returns a NEW graph dict with only active nodes/edges."""
    if scale is None:
        return graph

    def node_active(n: dict) -> bool:
        gates = n.get("scale_gates", [])
        return scale in gates

    active_nodes = [n for n in graph["nodes"] if node_active(n)]
    active_node_ids = {n["id"] for n in active_nodes}

    def edge_active(e: dict) -> bool:
        gates = e.get("scale_gates", [])
        if scale not in gates:
            return False
        # Source/target must resolve in active subgraph (or be sentinel)
        if e["source"] != "input" and e["source"] not in active_node_ids:
            return False
        if e["target"] != "output" and e["target"] not in active_node_ids:
            return False
        return True

    active_edges = [e for e in graph["edges"] if edge_active(e)]

    return {
        **graph,
        "nodes": active_nodes,
        "edges": active_edges,
    }


def check_kb_files(graph: dict, errors: list[str], skill_dir: Path) -> None:
    """I3: every kb_file referenced by every node must exist on disk AND be
    non-trivially non-empty (>=10 non-blank lines). Orphan KB files (present
    but not referenced) are logged as informational only."""
    kb_base = skill_dir / "kb"
    if not kb_base.exists():
        errors.append(f"kb/ directory not found at {kb_base}")
        return
    referenced: set[str] = set()
    for n in graph["nodes"]:
        for kbf in n.get("kb_files", []):
            referenced.add(kbf)
            target = kb_base / kbf
            if not target.exists():
                errors.append(
                    f"node {n['id']}: kb_file '{kbf}' not found at {target}"
                )
                continue
            try:
                with open(target) as fh:
                    nonblank = sum(1 for line in fh if line.strip())
                if nonblank < 10:
                    errors.append(
                        f"node {n['id']}: kb_file '{kbf}' has only {nonblank} non-blank "
                        f"line(s) (expected >=10) — may be empty or a placeholder"
                    )
            except OSError as exc:
                errors.append(f"node {n['id']}: kb_file '{kbf}' unreadable: {exc}")

    # Inverse check (informational — orphan KB files)
    actual = {p.name for p in kb_base.iterdir() if p.is_file() and p.suffix == ".md"}
    orphaned = actual - referenced
    if orphaned:
        info(f"NOTE: kb/ files not referenced by any node: {sorted(orphaned)}")


def parse_args(argv: list[str]) -> tuple[Path | None, str | None]:
    """Returns (graph_path, scale)."""
    graph_path: Path | None = None
    scale: str | None = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--scale":
            i += 1
            if i >= len(argv):
                fail("--scale requires an argument: MINIMAL | STANDARD | DEEP")
                sys.exit(2)
            v = argv[i].upper()
            if v not in {"MINIMAL", "STANDARD", "DEEP"}:
                fail(f"--scale must be one of MINIMAL|STANDARD|DEEP (got '{v}')")
                sys.exit(2)
            scale = v
        elif a.startswith("--"):
            fail(f"Unknown flag: {a}")
            sys.exit(2)
        else:
            graph_path = Path(a).expanduser().resolve()
        i += 1
    return graph_path, scale


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent

    graph_path, scale = parse_args(sys.argv[1:])
    if graph_path is None:
        graph_path = (skill_dir / "graph.json").resolve()

    label = f"Validating: {graph_path}"
    if scale:
        label += f"  [scale={scale}]"
    info(label)

    full_graph = load_graph(graph_path)

    errors: list[str] = []
    # Schema check always runs on the unfiltered graph.
    check_schema(full_graph, errors)
    if errors:
        for e in errors:
            fail(e)
        return 1

    # KB existence is graph-wide; filtering doesn't apply.
    check_kb_files(full_graph, errors, skill_dir)

    # PRC1 checks run on the active subgraph if --scale was provided.
    graph = filter_active_subgraph(full_graph, scale)

    check_edge_resolution(graph, errors)
    check_signal_fields(graph, errors)
    check_dag(graph, errors)
    check_connectivity(graph, errors)

    if errors:
        for e in errors:
            fail(e)
        info(f"\nFAIL: {len(errors)} check(s) failed.")
        return 1

    info("PASS: all PRC1 + KB-existence checks succeeded.")
    info(f"  nodes (active): {len(graph['nodes'])}/{len(full_graph['nodes'])}")
    info(f"  edges (active): {len(graph['edges'])}/{len(full_graph['edges'])}")
    info(
        f"  KB files referenced: "
        f"{sum(len(n.get('kb_files', [])) for n in full_graph['nodes'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
