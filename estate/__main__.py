from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_index(args: argparse.Namespace) -> None:
    from estate.indexer import index_estate
    from estate.graph import build_graph, save_graph

    root = Path(args.root)
    if not root.exists():
        print(f"error: root directory not found: {root}", file=sys.stderr)
        sys.exit(2)

    db = Path(args.db)
    edges = index_estate(root)
    graph = build_graph(edges)
    save_graph(graph, db)

    print(f"Indexed {len(graph.nodes)} nodes, {len(graph.edges)} edges -> {db}")


def cmd_impact(args: argparse.Namespace) -> None:
    from estate.graph import load_graph
    from estate.impact import compute_impact

    db = Path(args.db)
    if not db.exists():
        print(f"error: graph DB not found: {db} -- run 'python -m estate index' first", file=sys.stderr)
        sys.exit(2)

    graph = load_graph(db)
    result = compute_impact(args.program, graph)

    print(f"Program      : {result.program}")
    print(f"Blast Radius : {result.blast_radius_score}/100")
    print(f"Systems      : {len(result.affected_systems)} affected")
    print()
    if result.direct_callers:
        print(f"Direct callers ({len(result.direct_callers)}):")
        for s in result.direct_callers:
            print(f"  {s}")
    if result.copybook_siblings:
        print(f"Copybook siblings ({len(result.copybook_siblings)}):")
        for s in result.copybook_siblings:
            print(f"  {s}")
    if result.vsam_co_accessors:
        print(f"VSAM co-accessors ({len(result.vsam_co_accessors)}):")
        for s in result.vsam_co_accessors:
            print(f"  {s}")
    if result.batch_jobs_at_risk:
        print(f"Batch jobs at risk ({len(result.batch_jobs_at_risk)}):")
        for s in result.batch_jobs_at_risk:
            print(f"  {s}")


def cmd_show(args: argparse.Namespace) -> None:
    from estate.graph import load_graph

    db = Path(args.db)
    if not db.exists():
        print(f"error: graph DB not found: {db}", file=sys.stderr)
        sys.exit(2)

    graph = load_graph(db)
    print(f"Nodes: {len(graph.nodes)}")
    print(f"Edges: {len(graph.edges)}")
    print()
    for src, tgt, data in sorted(graph.edges(data=True)):
        print(f"  {src} --[{data.get('edge_type', '?')}]--> {tgt}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m estate", description="Refinery estate graph tools")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Scan a directory and build the estate graph")
    p_index.add_argument("--root", required=True, help="Root directory to scan")
    p_index.add_argument("--db", default="estate.db", help="Output SQLite database path")

    p_impact = sub.add_parser("impact", help="Compute blast radius for a program")
    p_impact.add_argument("program", help="Program name (e.g. INTEREST-CALC)")
    p_impact.add_argument("--db", default="estate.db", help="Estate graph database path")

    p_show = sub.add_parser("show", help="Show all edges in the estate graph")
    p_show.add_argument("--db", default="estate.db", help="Estate graph database path")

    args = parser.parse_args()
    {"index": cmd_index, "impact": cmd_impact, "show": cmd_show}[args.command](args)


if __name__ == "__main__":
    main()
