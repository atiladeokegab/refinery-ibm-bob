from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP(
    "Refinery",
    instructions=(
        "Refinery maps blast radius across a mainframe estate. "
        "Call estate_index to build the dependency graph, then estate_impact "
        "to get the full blast radius for any COBOL program."
    ),
)


@mcp.tool()
def estate_index(root_dir: str) -> dict:
    """Index a mainframe estate directory and return graph statistics.

    Args:
        root_dir: Absolute path to the root of the mainframe codebase.
    """
    from estate.indexer import index_estate
    from estate.graph import build_graph

    edges = index_estate(Path(root_dir))
    graph = build_graph(edges)
    return {
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "root_dir": root_dir,
    }


@mcp.tool()
def estate_impact(program: str, root_dir: str) -> dict:
    """Compute the full blast radius for a COBOL program within a mainframe estate.

    Args:
        program: Program name without extension, e.g. INTEREST-CALC
        root_dir: Absolute path to the root of the mainframe codebase.
    """
    from estate.indexer import index_estate
    from estate.graph import build_graph
    from estate.impact import compute_impact

    edges = index_estate(Path(root_dir))
    graph = build_graph(edges)
    result = compute_impact(program, graph)
    return {
        "program": result.program,
        "blast_radius_score": result.blast_radius_score,
        "affected_systems": result.affected_systems,
        "direct_callers": result.direct_callers,
        "copybook_siblings": result.copybook_siblings,
        "vsam_co_accessors": result.vsam_co_accessors,
        "batch_jobs_at_risk": result.batch_jobs_at_risk,
    }


if __name__ == "__main__":
    mcp.run()
