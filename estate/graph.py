from __future__ import annotations

import sqlite3
from pathlib import Path

import networkx as nx

from estate.indexer import Edge, index_estate


def build_graph(edges: list[Edge]) -> nx.DiGraph:
    g = nx.DiGraph()
    for e in edges:
        g.add_edge(e.source, e.target, edge_type=e.edge_type)
    return g


def save_graph(graph: nx.DiGraph, db_path: Path) -> None:
    db_path = Path(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS estate_nodes (
                name TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS estate_edges (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                edge_type TEXT NOT NULL
            );
            DELETE FROM estate_nodes;
            DELETE FROM estate_edges;
        """)
        conn.executemany(
            "INSERT OR IGNORE INTO estate_nodes VALUES (?)",
            [(n,) for n in graph.nodes],
        )
        conn.executemany(
            "INSERT INTO estate_edges VALUES (?, ?, ?)",
            [
                (u, v, d.get("edge_type", ""))
                for u, v, d in graph.edges(data=True)
            ],
        )
        conn.commit()


def load_graph(db_path: Path) -> nx.DiGraph:
    db_path = Path(db_path)
    g = nx.DiGraph()
    with sqlite3.connect(db_path) as conn:
        for (name,) in conn.execute("SELECT name FROM estate_nodes"):
            g.add_node(name)
        for source, target, edge_type in conn.execute(
            "SELECT source, target, edge_type FROM estate_edges"
        ):
            g.add_edge(source, target, edge_type=edge_type)
    return g


def build_graph_from_root(root: Path, db_path: Path | None = None) -> nx.DiGraph:
    edges = index_estate(root)
    graph = build_graph(edges)
    if db_path:
        save_graph(graph, db_path)
    return graph
