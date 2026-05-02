# Advanced Cognitive Pipeline Design

A complex document with deep nesting, many constraints, and extensive cross-referencing for high-complexity testing.

## 1. Architecture Overview

### 1.1 Design Principles

The system adheres to these principles:

#### 1.1.1 Correctness First

Correctness MUST be verifiable at every stage. Every transformation SHALL produce auditable output.

#### 1.1.2 Performance Bounds

Performance MUST degrade gracefully under load. The system SHALL NOT exceed memory budgets under any documented workload.

### 1.2 Topology

The topology is a directed acyclic graph with back-edges for iterative refinement (§2.3).

## 2. Node Specifications

### 2.1 Input Nodes

Input nodes are the ingestion layer. §2.1 refers to the requirements in §3.

#### 2.1.1 Intake Decomposition

The intake decomposer MUST:
- Parse all markdown headers via regex
- Record structural depth per §4.2.3
- Compute complexity using the formula in §5.1
- Write verbatim inputs to the session directory

#### 2.1.2 Validation

The validator SHALL run six checks (PRC1): DAG validation, edge resolution, signal field validity, connectivity, KB existence verification, and JSON Schema conformance. Any check failure MUST halt the pipeline.

### 2.2 Analysis Nodes

Analysis nodes examine the input structure.

#### 2.2.1 Structural Survey

For each major section, the surveyor MUST catalog:
- Section role (claim, evidence, constraint, bridge, meta)
- Nesting depth and line count
- Apparent domain from header keywords

The surveyor SHALL NOT modify source content. Analyses are append-only per §6.1.

#### 2.2.2 Gap Detection

Gap detection identifies what the document does NOT address. Three gap types exist:
- Acknowledged gaps (explicitly out of scope)
- Implicit gaps (topics named but not developed)
- Structural gaps (missing sections that would complete the argument)

### 2.3 Synthesis Nodes

Synthesis nodes combine analysis results into actionable output.

#### 2.3.1 Cross-Referencing

The cross-referencer builds a map connecting every Node B finding to its corresponding Node A section. Connections are scored 1-5 on relevance.

#### 2.3.2 Enhancement

Enhancements MUST preserve the original text's voice and organizing principle. Every enhancement SHALL trace back to a specific solution ID.

## 3. Constraints Catalog

### 3.1 Hard Constraints

The following constraints are absolute:

1. The system MUST NOT write to any directory outside the session directory.
2. The system MUST NOT perform runtime web searches or MCP queries.
3. The output path MUST differ from the input path (HG-1).
4. Every accepted solution MUST have been through the full hybrid protocol (HG-3).

### 3.2 Soft Constraints

1. The system SHOULD complete STANDARD runs within 22 minutes wall-clock.
2. Spawn budgets SHOULD NOT exceed 6 dispatches in STANDARD mode.
3. Back-edges SHALL NOT fire more than once per session.

## 4. Signal System

### 4.1 Signal Types

Signals flow through the graph as structured metadata. Each signal has a declared type, raising node, and triggering condition.

### 4.2 Signal Propagation

#### 4.2.1 Forward Signals

Forward signals accompany required edges. Downstream nodes read them from SIGNAL_STATE.

#### 4.2.2 Gate Signals

Gate signals control conditional edges. A gate condition evaluates SIGNAL_STATE entries and determines whether an edge fires.

### 4.3 Signal Lifecycle

Signals are raised once, never retracted. The SIGNAL_STATE dict is append-only. Keys are (node_id, signal_field) pairs.

## 5. Complexity Metrics

### 5.1 Formula

The S1 complexity formula is:
```
score = log10(line_count) + structural_depth + min(constraint_count / 10, 5.0)
```

Where:
- `line_count` counts all lines in Node A (minimum 1 to avoid log10(0))
- `structural_depth` is the maximum markdown header nesting depth, extracted by regex `^(#+)\s+\S`
- `constraint_count` is the total occurrences of MUST/MUST NOT/SHALL/REQUIRED/FORBIDDEN/NEVER

### 5.2 Buckets

- `score < 5` → low complexity
- `5 ≤ score < 9` → medium complexity
- `score ≥ 9` → high complexity

### 5.3 Effects

Complexity bucket determines:
- N5's ideas-per-pass (low=8, medium=12, high=16)
- N8's iteration count (high triggers 2 iterations even in STANDARD mode)

## 6. Operational Rules

### 6.1 Append-Only Principle

All analysis output is append-only. Nodes SHALL NOT modify stage files written by other nodes. Corrections take the form of new findings referencing the original, not edits to the original text.

### 6.2 Session Integrity

A session is defined by its session.json. The session ID format is `<YYYY-MM-DD>-<sha256_8char_prefix>`. The session directory MUST contain `input-a.md` and (when provided) `input-b.md` before any node executes.

### 6.3 Replay Support

The `--resume` flag reads `session.json` and restores SIGNAL_STATE from `graph-trace.json`. The orchestrator continues from the first unexecuted node in topological order.

The `--retry-failed` flag re-executes only nodes whose stage files have `status != "complete"`, preserving all completed outputs.
