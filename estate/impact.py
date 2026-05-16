from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx


@dataclass
class ImpactResult:
    program: str
    direct_callers: list[str] = field(default_factory=list)
    transitive_callers: list[str] = field(default_factory=list)
    copybook_siblings: list[str] = field(default_factory=list)
    vsam_co_accessors: list[str] = field(default_factory=list)
    batch_jobs_at_risk: list[str] = field(default_factory=list)
    affected_systems: list[str] = field(default_factory=list)
    blast_radius_score: int = 0


def compute_impact(program_name: str, graph: nx.DiGraph) -> ImpactResult:
    name = program_name.upper()
    result = ImpactResult(program=name)

    if name not in graph:
        return result

    reversed_graph = graph.reverse()

    # Direct callers: nodes with a direct edge TO this program
    result.direct_callers = [
        n for n in reversed_graph.successors(name)
        if graph[n][name].get("edge_type") in {"CALLS", "JCL_EXEC"}
    ]

    # Transitive callers: all reachable nodes in the reversed graph (BFS)
    all_upstream = set(nx.bfs_tree(reversed_graph, name).nodes) - {name}
    result.transitive_callers = [
        n for n in all_upstream if n not in result.direct_callers
    ]

    # Batch jobs at risk: JCL jobs in the transitive impact set
    all_affected_upstream = all_upstream | set(result.direct_callers)
    result.batch_jobs_at_risk = [
        n for n in all_affected_upstream
        if any(
            graph[n][s].get("edge_type") == "JCL_EXEC"
            for s in graph.successors(n)
            if graph.has_edge(n, s)
        )
    ]

    # Copybooks this program uses
    my_copybooks = {
        v for u, v, d in graph.out_edges(name, data=True)
        if d.get("edge_type") == "COPIES"
    }

    # Copybook siblings: programs sharing any copybook we use
    if my_copybooks:
        copybook_siblings: set[str] = set()
        for cb in my_copybooks:
            if cb in graph:
                for sibling in reversed_graph.successors(cb):
                    if sibling != name and graph[sibling][cb].get("edge_type") == "COPIES":
                        copybook_siblings.add(sibling)
        result.copybook_siblings = list(copybook_siblings)

    # VSAM datasets this program accesses
    my_vsam = {
        v for u, v, d in graph.out_edges(name, data=True)
        if d.get("edge_type") == "VSAM_REF"
    }

    # VSAM co-accessors: other programs reading/writing the same datasets
    if my_vsam:
        vsam_co: set[str] = set()
        for ds in my_vsam:
            if ds in graph:
                for accessor in reversed_graph.successors(ds):
                    if accessor != name:
                        vsam_co.add(accessor)
        result.vsam_co_accessors = list(vsam_co)

    # affected_systems: union of all, deduplicated
    affected: set[str] = set()
    affected.update(result.direct_callers)
    affected.update(result.transitive_callers)
    affected.update(result.copybook_siblings)
    affected.update(result.vsam_co_accessors)
    result.affected_systems = sorted(affected)

    # Blast radius score: capped at 100
    score = (
        len(result.direct_callers) * 10
        + len(result.transitive_callers) * 3
        + len(result.copybook_siblings) * 5
        + len(result.vsam_co_accessors) * 4
    )
    result.blast_radius_score = min(100, score)

    return result
