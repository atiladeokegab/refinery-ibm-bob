from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from audit.engine import AuditResult

_DEFAULT_DB = Path("portal.db")


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_id      TEXT NOT NULL,
            date        TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            client_ref  TEXT,
            program     TEXT NOT NULL,
            modified    TEXT NOT NULL,
            verdict     TEXT NOT NULL,
            risk_score  INTEGER NOT NULL,
            reduction_pct REAL NOT NULL,
            bob_headline  TEXT,
            pdf_path    TEXT,
            sha256      TEXT,
            runner_type TEXT
        )
    """)
    conn.commit()
    # Migration: add new columns if not present (SQLite lacks IF NOT EXISTS for ALTER TABLE)
    for col, col_def in [
        ("blast_radius_score", "INTEGER DEFAULT 0"),
        ("affected_systems_json", "TEXT DEFAULT '[]'"),
        ("signed_by", "TEXT"),
        ("signed_at", "TEXT"),
        ("signed_reason", "TEXT"),
        ("correction_count", "INTEGER DEFAULT 0"),
        ("rejected_by", "TEXT"),
        ("rejected_at", "TEXT"),
        ("rejection_reason", "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE audit_records ADD COLUMN {col} {col_def}")
            conn.commit()
        except Exception:
            pass
    return conn


@dataclass
class AuditRecord:
    id: int | None
    ref_id: str
    date: str
    created_at: str
    client_ref: str
    program: str
    modified: str
    verdict: str
    risk_score: int
    reduction_pct: float
    bob_headline: str | None
    pdf_path: str | None
    sha256: str | None
    runner_type: str
    blast_radius_score: int = 0
    affected_systems_json: str = "[]"
    signed_by: str | None = None
    signed_at: str | None = None
    signed_reason: str | None = None
    correction_count: int = 0
    rejected_by: str | None = None
    rejected_at: str | None = None
    rejection_reason: str | None = None


def write_audit_record(
    audit: AuditResult,
    pdf_path: Path | None = None,
    sha256: str | None = None,
    bob_headline: str | None = None,
    correction_count: int = 0,
    db_path: Path = _DEFAULT_DB,
) -> AuditRecord:
    import json
    d = audit.diff
    impact = getattr(audit, "impact", None)
    blast_score = impact.blast_radius_score if impact else 0
    affected_json = json.dumps(impact.affected_systems) if impact else "[]"

    conn = _connect(db_path)
    try:
        cur = conn.execute("""
            INSERT INTO audit_records
              (ref_id, date, created_at, client_ref, program, modified,
               verdict, risk_score, reduction_pct, bob_headline, pdf_path, sha256,
               runner_type, blast_radius_score, affected_systems_json, correction_count)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            audit.ref_id,
            audit.date,
            datetime.utcnow().isoformat(),
            audit.client_ref or "",
            audit.original_file,
            audit.modified_file,
            d.verdict,
            d.risk_score,
            d.reduction_pct,
            bob_headline,
            str(pdf_path) if pdf_path else None,
            sha256,
            d.runner_type,
            blast_score,
            affected_json,
            correction_count,
        ))
        conn.commit()
        return AuditRecord(
            id=cur.lastrowid,
            ref_id=audit.ref_id,
            date=audit.date,
            created_at=datetime.utcnow().isoformat(),
            client_ref=audit.client_ref or "",
            program=audit.original_file,
            modified=audit.modified_file,
            verdict=d.verdict,
            risk_score=d.risk_score,
            reduction_pct=d.reduction_pct,
            bob_headline=bob_headline,
            pdf_path=str(pdf_path) if pdf_path else None,
            sha256=sha256,
            runner_type=d.runner_type,
            blast_radius_score=blast_score,
            affected_systems_json=affected_json,
            correction_count=correction_count,
        )
    finally:
        conn.close()


def reject_record(
    ref_id: str,
    cro_name: str,
    rejection_reason: str,
    db_path: Path = _DEFAULT_DB,
) -> AuditRecord | None:
    conn = _connect(db_path)
    try:
        rejected_at = datetime.utcnow().isoformat()
        conn.execute(
            "UPDATE audit_records SET rejected_by=?, rejected_at=?, rejection_reason=? WHERE ref_id=?",
            (cro_name, rejected_at, rejection_reason, ref_id),
        )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM audit_records WHERE ref_id=?", (ref_id,)
        ).fetchall()
        if not rows:
            return None
        return AuditRecord(**dict(rows[0]))
    finally:
        conn.close()


def get_records(
    db_path: Path = _DEFAULT_DB,
    verdict: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditRecord]:
    conn = _connect(db_path)
    try:
        query = "SELECT * FROM audit_records"
        params: list = []
        if verdict:
            query += " WHERE verdict = ?"
            params.append(verdict)
        query += f" ORDER BY id DESC LIMIT {limit} OFFSET {offset}"
        rows = conn.execute(query, params).fetchall()
        return [AuditRecord(**dict(r)) for r in rows]
    finally:
        conn.close()


def get_record_by_ref_id(ref_id: str, db_path: Path = _DEFAULT_DB) -> AuditRecord | None:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM audit_records WHERE ref_id=?", (ref_id,)
        ).fetchall()
        return AuditRecord(**dict(rows[0])) if rows else None
    finally:
        conn.close()


def get_kpis(db_path: Path = _DEFAULT_DB) -> dict:
    conn = _connect(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0]
        flagged = conn.execute("SELECT COUNT(*) FROM audit_records WHERE verdict='FLAGGED'").fetchone()[0]
        avg_reduction = conn.execute("SELECT AVG(reduction_pct) FROM audit_records WHERE verdict='PASS'").fetchone()[0] or 0.0
        return {
            "total_audits": total,
            "flagged_count": flagged,
            "pass_count": total - flagged,
            "avg_cpu_reduction_pct": round(avg_reduction, 1),
            "monthly_saving_usd": int(avg_reduction * 300 * total),
        }
    finally:
        conn.close()


def update_bob_headline(
    ref_id: str,
    headline: str,
    db_path: Path = _DEFAULT_DB,
) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            "UPDATE audit_records SET bob_headline=? WHERE ref_id=?",
            (headline, ref_id),
        )
        conn.commit()
    finally:
        conn.close()


def sign_contract(
    ref_id: str,
    cro_name: str,
    *,
    approval_reason: str,
    db_path: Path = _DEFAULT_DB,
) -> AuditRecord | None:
    conn = _connect(db_path)
    try:
        signed_at = datetime.utcnow().isoformat()
        conn.execute(
            "UPDATE audit_records SET signed_by=?, signed_at=?, signed_reason=? WHERE ref_id=?",
            (cro_name, signed_at, approval_reason, ref_id),
        )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM audit_records WHERE ref_id=?", (ref_id,)
        ).fetchall()
        if not rows:
            return None
        return AuditRecord(**dict(rows[0]))
    finally:
        conn.close()
