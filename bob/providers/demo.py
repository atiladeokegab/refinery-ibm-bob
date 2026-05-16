from __future__ import annotations
import json
from bob.providers import BaseProvider


class DemoProvider(BaseProvider):
    """Pure-Python provider for demos — no external services needed."""

    def complete(self, prompt: str) -> str:
        # Extract verdict and risk from prompt to build a realistic narrative
        import re
        verdict = "FLAGGED" if "Verdict: FLAGGED" in prompt else "PASS"
        risk = 0
        try:
            risk = int(re.search(r"Risk Score:\s*(\d+)", prompt).group(1))
        except Exception:
            pass

        if verdict == "FLAGGED":
            data = {
                "headline": f"Deployment Blocked — Risk Score {risk}/100",
                "executive_summary": (
                    "IBM Bob's AI refactoring introduced a semantic divergence "
                    "that Refinery's 6-layer verification engine flagged as a "
                    "high-severity deployment risk. The AI-modified program "
                    "cannot be promoted to production without manual review."
                ),
                "risk_items": [
                    "COMPUTE expression drift detected — output may diverge under real transaction volumes",
                    "Output equivalence check failed — programs produce different results under test inputs",
                ],
                "remediation": (
                    "Return the AI-modified COBOL to the originating team with this audit report. "
                    "Each flagged divergence must be reviewed and either corrected or formally "
                    "accepted with a signed risk waiver before deployment can proceed."
                ),
                "confidence": 0.85,
            }
        else:
            comp3 = "COMP-3" in prompt or "comp_3" in prompt.lower() or "packed" in prompt.lower()
            if comp3:
                data = {
                    "headline": "Storage Format Change — Blast Radius Review Required",
                    "executive_summary": (
                        "IBM Bob converted 7 accumulator fields to COMP-3 packed decimal. "
                        "No procedural logic was altered and arithmetic results are numerically identical. "
                        "However, the storage format change affects VSAM record layouts shared with "
                        "downstream batch jobs. CRO sign-off is required before promotion."
                    ),
                    "risk_items": [
                        "COMP-3 storage format change on 7 WORKING-STORAGE fields — VSAM co-accessors may require recompile",
                        "14 downstream systems identified in blast radius — JCL batch jobs reference shared copybooks",
                        "Numerically equivalent under test conditions — edge cases at precision boundary not verified",
                    ],
                    "remediation": (
                        "Submit blast radius report to downstream teams for impact assessment. "
                        "CRO sign-off required due to cross-system scope. "
                        "Recompile all VSAM co-accessor programs before promoting to production."
                    ),
                    "confidence": 0.91,
                }
            else:
                data = {
                    "headline": "No Semantic Divergences — Safe to Deploy",
                    "executive_summary": (
                        "Refinery completed 6 independent verification layers and found no "
                        "semantic divergences. IBM Bob's AI refactoring is functionally "
                        "equivalent to the original program. The change is approved for promotion."
                    ),
                    "risk_items": [],
                    "remediation": "No action required. Programme may proceed to change approval.",
                    "confidence": 0.90,
                }
        return json.dumps(data)
