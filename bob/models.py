from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RiskNarrative:
    headline: str
    executive_summary: str
    risk_items: list[str]
    remediation: str
    confidence: float  # 0.0 = Bob unavailable, 1.0 = high confidence
