#!/usr/bin/env python3
"""PRC1 validator for graph.json. Implements 6 checks per spec §3.5.

Usage: python3 validate-graph.py [<graph.json path>]
Exit 0 on success; non-zero on first failure with explanatory error.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict


def load_graph(path):
    with open(path) as f:
        return json.load(f)


def check_dag(graph, scale="STANDARD"):
    """Check 1: DAG (excluding back-edges) topologically sortable."""
    active_nodes = {n["id"] for n in graph["nodes"] if scale in n["scale_gates"]}
    forward_edges = [(e["source"], e["target"]) for e in graph["edges"]
                     if e["type"] != "back-edge"
                     and scale in e["scale_gates"]
                     and e["source"] in active_nodes | {"input"}
                     and e["target"] in active_nodes | {"output"}]
    in_degree = defaultdict(int)
    succ = defaultdict(list)
    nodes = active_nodes | {"input", "output"}
    for s, t in forward_edges:
        succ[s].append(t)
        in_degree[t] += 1
    queue = [n for n in nodes if in_degree[n] == 0]
    visited = []
    while queue:
        n = queue.pop(0)
        visited.append(n)
        for t in succ[n]:
            in_degree[t] -= 1
            if in_degree[t] == 0:
                queue.append(t)
    if len(visited) != len(nodes):
        unvisited = nodes - set(visited)
        return False, f"DAG check failed: cycle involves {unvisited}"
    return True, None


def check_edge_resolution(graph, scale="STANDARD"):
    """Check 2: every active edge's source/target resolves to a declared active node ID."""
    active_node_ids = {n["id"] for n in graph["nodes"] if scale in n["scale_gates"]} | {"input", "output"}
    for e in graph["edges"]:
        if scale not in e["scale_gates"]:
            continue
        if e["source"] not in active_node_ids:
            return False, f"Edge {e['id']}: source '{e['source']}' not in active nodes"
        if e["target"] not in active_node_ids:
            return False, f"Edge {e['id']}: target '{e['target']}' not in active nodes"
    return True, None


def check_signal_field_validity(graph, scale="STANDARD"):
    """Check 3: every active edge's signal_field is in the declared enum."""
    enum = set(graph["signal_field_enum"])
    for e in graph["edges"]:
        if scale not in e["scale_gates"]:
            continue
        if e["signal_field"] not in enum:
            return False, f"Edge {e['id']}: signal_field '{e['signal_field']}' not in declared enum"
    return True, None


def check_connectivity(graph, scale="STANDARD"):
    """Check 4: active subgraph (back-edges INCLUDED) is connected with N1 source, output sink."""
    active_node_ids = {n["id"] for n in graph["nodes"] if scale in n["scale_gates"]} | {"input", "output"}
    adj = defaultdict(set)
    for e in graph["edges"]:
        if scale not in e["scale_gates"]:
            continue
        if e["source"] in active_node_ids and e["target"] in active_node_ids:
            adj[e["source"]].add(e["target"])
            adj[e["target"]].add(e["source"])  # for connectivity, treat as undirected
    visited = set()
    stack = ["input"]
    while stack:
        n = stack.pop()
        if n in visited:
            continue
        visited.add(n)
        stack.extend(adj[n])
    missing = active_node_ids - visited
    if missing:
        return False, f"Connectivity check failed: unreachable from input: {missing}"
    return True, None


def check_kb_files(graph, skill_path):
    """Check 5: every node's referenced KB file exists in skill_path/kb/."""
    kb_dir = Path(skill_path) / "kb"
    for n in graph["nodes"]:
        for kb in n.get("kb_files", []):
            if not (kb_dir / kb).exists():
                return False, f"Node {n['id']}: KB file '{kb}' not found at {kb_dir}"
    return True, None


def _parse_module_frontmatter(path):
    """Parse a YAML frontmatter block at the top of a markdown file.
    Returns dict; empty dict if absent or unparseable. No yaml dep — minimal parse."""
    try:
        text = path.read_text()
    except Exception:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    try:
        import yaml
        return yaml.safe_load(block) or {}
    except Exception:
        return {}


def _collect_module_signal_io(skill_path):
    """Returns (producers, consumers) — sets of signal_field names produced /
    consumed by any module's frontmatter (output_signal_fields,
    input_dependencies, optional_inputs)."""
    producers, consumers = set(), set()
    mod_dir = Path(skill_path) / "modules"
    for f in sorted(mod_dir.glob("*.md")):
        fm = _parse_module_frontmatter(f)
        for sf in fm.get("output_signal_fields", []) or []:
            producers.add(sf)
        for dep in (fm.get("input_dependencies", []) or []) + (fm.get("optional_inputs", []) or []):
            inner = dep.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in inner.split(",", 1)]
            if len(parts) == 2:
                consumers.add(parts[1])
    return producers, consumers


def check_signal_field_coverage(graph, skill_path):
    """Check 7: every signal_field_enum entry has ≥1 producing source AND
    (for non-`—`) ≥1 consuming sink. Sources include edges and module
    output_signal_fields; sinks include edges and module input_dependencies/
    optional_inputs. Catches dead enum entries."""
    enum = set(graph["signal_field_enum"])
    producers, consumers = set(), set()
    for e in graph["edges"]:
        producers.add(e["signal_field"])
        consumers.add(e["signal_field"])
    for n in graph["nodes"]:
        for f in n.get("output_signal_fields", []):
            producers.add(f)
        for dep in n.get("input_dependencies", []) + n.get("optional_inputs", []):
            inner = dep.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in inner.split(",", 1)]
            if len(parts) == 2:
                consumers.add(parts[1])
    mod_producers, mod_consumers = _collect_module_signal_io(skill_path)
    producers |= mod_producers
    consumers |= mod_consumers
    missing_producer = enum - producers - {"—"}  # `—` (terminal/input edges) has no producer
    missing_consumer = enum - consumers - {"—"}
    if missing_producer:
        return False, f"signal_field_enum entries with no producer: {sorted(missing_producer)}"
    if missing_consumer:
        return False, f"signal_field_enum entries with no consumer: {sorted(missing_consumer)}"
    return True, None


def check_module_dependency_validity(graph, skill_path):
    """Check 8: every module's input_dependencies / optional_inputs reference
    a signal_field that exists in the enum. Catches stale-rename drift like
    a module still pointing at `verification_report` after rename."""
    enum = set(graph["signal_field_enum"])
    # Check graph.json node-level deps if present
    for n in graph["nodes"]:
        for dep in n.get("input_dependencies", []) + n.get("optional_inputs", []):
            inner = dep.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in inner.split(",", 1)]
            if len(parts) != 2:
                continue
            field = parts[1]
            if field not in enum:
                return False, (
                    f"Node {n['id']}: dependency '{dep}' references "
                    f"signal_field '{field}' not in signal_field_enum"
                )
    # Also check module frontmatter (true source of truth for module deps)
    mod_dir = Path(skill_path) / "modules"
    for f in sorted(mod_dir.glob("*.md")):
        fm = _parse_module_frontmatter(f)
        deps = (fm.get("input_dependencies", []) or []) + (fm.get("optional_inputs", []) or [])
        for dep in deps:
            inner = dep.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in inner.split(",", 1)]
            if len(parts) != 2:
                continue
            field = parts[1]
            if field not in enum:
                return False, (
                    f"Module {f.name}: dependency '{dep}' references "
                    f"signal_field '{field}' not in signal_field_enum"
                )
    return True, None


def main():
    graph_path = sys.argv[1] if len(sys.argv) > 1 else "graph.json"
    skill_path = Path(graph_path).parent
    graph = load_graph(graph_path)

    for scale in ["STANDARD", "DEEP"]:
        for check_name, check_fn in [
            (f"DAG check ({scale})", lambda: check_dag(graph, scale)),
            (f"Edge resolution ({scale})", lambda: check_edge_resolution(graph, scale)),
            (f"Signal field validity ({scale})", lambda: check_signal_field_validity(graph, scale)),
            (f"Connectivity ({scale})", lambda: check_connectivity(graph, scale)),
        ]:
            ok, err = check_fn()
            if not ok:
                print(f"FAILED: PRC1 — {check_name}: {err}", file=sys.stderr)
                return 1

    ok, err = check_kb_files(graph, skill_path)
    if not ok:
        print(f"FAILED: PRC1 — KB file existence: {err}", file=sys.stderr)
        return 1

    ok, err = check_signal_field_coverage(graph, skill_path)
    if not ok:
        print(f"FAILED: PRC1 — Signal field coverage: {err}", file=sys.stderr)
        return 1

    ok, err = check_module_dependency_validity(graph, skill_path)
    if not ok:
        print(f"FAILED: PRC1 — Module dependency validity: {err}", file=sys.stderr)
        return 1

    # Schema validation
    try:
        import jsonschema
        with open(Path(skill_path) / "graph.schema.json") as f:
            schema = json.load(f)
        jsonschema.validate(graph, schema)
    except Exception as e:
        print(f"FAILED: PRC1 — graph.schema.json validation: {e}", file=sys.stderr)
        return 1

    print(f"PRC1: all checks passed for {graph_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
