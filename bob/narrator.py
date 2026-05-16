from __future__ import annotations

import json
import os
import re
from pathlib import Path

from audit.engine import AuditResult
from bob.models import RiskNarrative
from bob.providers import BaseProvider

_TEMPLATE = (Path(__file__).parent / "prompt_template.txt").read_text()

_PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {}


def _get_provider(name: str) -> BaseProvider:
    if not _PROVIDER_REGISTRY:
        _candidates = {
            "ibm_bob": "bob.providers.ibm_bob.IBMBobProvider",
            "openai":  "bob.providers.openai.OpenAIProvider",
            "local":   "bob.providers.local.OllamaProvider",
            "demo":    "bob.providers.demo.DemoProvider",
        }
        for key, dotpath in _candidates.items():
            try:
                module_path, cls_name = dotpath.rsplit(".", 1)
                import importlib
                mod = importlib.import_module(module_path)
                _PROVIDER_REGISTRY[key] = getattr(mod, cls_name)
            except Exception:
                pass  # provider unavailable (missing deps/credentials)
    cls = _PROVIDER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown BOB_PROVIDER: {name!r}. Valid: {list(_PROVIDER_REGISTRY)}")
    return cls()


def narrate(result: AuditResult, provider: str | None = None) -> RiskNarrative:
    provider_name = provider or os.environ.get("BOB_PROVIDER", "ibm_bob")
    d = result.diff
    changes_json = json.dumps(
        [
            {
                "type": c.change_type,
                "severity": c.severity,
                "location": c.location,
                "original": c.original[:200],
                "modified": c.modified[:200],
            }
            for c in d.semantic_changes
        ],
        indent=2,
    )
    prompt = _TEMPLATE.format(
        verdict=d.verdict,
        risk_score=d.risk_score,
        reduction_pct=d.reduction_pct,
        semantic_changes=changes_json,
        context="No additional RAG context available.",
    )
    try:
        p = _get_provider(provider_name)
        raw = p.complete(prompt)
        return _parse(raw)
    except Exception as exc:
        return RiskNarrative(
            headline="Bob unavailable — manual review required",
            executive_summary=(
                f"Bob's narrative could not be generated ({exc}). "
                "Review the findings table in the audit report manually."
            ),
            risk_items=[
                f"{c.severity}: {c.change_type} @ {c.location}"
                for c in d.semantic_changes
            ],
            remediation="Contact your Refinery administrator to check BOB_PROVIDER configuration.",
            confidence=0.0,
        )


def _parse(raw: str) -> RiskNarrative:
    cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        return RiskNarrative(
            headline=data["headline"],
            executive_summary=data["executive_summary"],
            risk_items=data.get("risk_items", []),
            remediation=data["remediation"],
            confidence=float(data.get("confidence", 0.8)),
        )
    except (json.JSONDecodeError, KeyError):
        headline_m = re.search(r"HEADLINE:\s*(.+)", raw)
        summary_m = re.search(r"SUMMARY:\s*(.+?)(?=RISK:|REMEDIATION:|$)", raw, re.DOTALL)
        remediation_m = re.search(r"REMEDIATION:\s*(.+)", raw, re.DOTALL)
        return RiskNarrative(
            headline=headline_m.group(1).strip() if headline_m else "Risk detected — see findings",
            executive_summary=summary_m.group(1).strip() if summary_m else raw[:300],
            risk_items=[],
            remediation=remediation_m.group(1).strip() if remediation_m else "Review semantic changes above.",
            confidence=0.5,
        )
