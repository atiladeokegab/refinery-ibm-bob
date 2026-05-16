from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Edge:
    source: str
    target: str
    edge_type: str  # CALLS | COPIES | VSAM_REF | JCL_EXEC | JCL_DD


def _stem(path: Path) -> str:
    return path.stem.upper()


def _index_cobol(path: Path) -> list[Edge]:
    source = path.read_text(encoding="utf-8", errors="ignore")
    name = _stem(path)
    edges: list[Edge] = []

    for target in re.findall(r"CALL\s+['\"]?([\w-]+)['\"]?", source, re.IGNORECASE):
        edges.append(Edge(name, target.upper(), "CALLS"))

    for target in re.findall(r"^\s*COPY\s+([\w-]+)", source, re.IGNORECASE | re.MULTILINE):
        edges.append(Edge(name, target.upper(), "COPIES"))

    for dataset in re.findall(r"ASSIGN\s+TO\s+([\w.]+)", source, re.IGNORECASE):
        edges.append(Edge(name, dataset.upper(), "VSAM_REF"))

    return edges


def _index_jcl(path: Path) -> list[Edge]:
    source = path.read_text(encoding="utf-8", errors="ignore")

    job_names = re.findall(r"^//(\w+)\s+JOB\b", source, re.IGNORECASE | re.MULTILINE)
    job_name = job_names[0].upper() if job_names else _stem(path)

    edges: list[Edge] = []

    for prog in re.findall(r"EXEC\s+PGM=([\w-]+)", source, re.IGNORECASE):
        edges.append(Edge(job_name, prog.upper(), "JCL_EXEC"))

    for dataset in re.findall(r"DSN=([\w.]+)", source, re.IGNORECASE):
        edges.append(Edge(job_name, dataset.upper(), "JCL_DD"))

    return edges


def index_estate(root: Path) -> list[Edge]:
    edges: list[Edge] = []
    for path in Path(root).rglob("*"):
        if path.suffix.lower() in (".cob", ".cbl"):
            edges.extend(_index_cobol(path))
        elif path.suffix.lower() == ".jcl":
            edges.extend(_index_jcl(path))
    return edges
