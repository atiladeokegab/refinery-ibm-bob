from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from audit.engine import run_audit
from audit.report import generate_pdf
from bob.narrator import narrate

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Refinery — AI Change Contract Enforcer",
    layout="wide",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230E0E0C'/><g transform='translate(6 5)'><rect x='0' y='0' width='20' height='3.5' rx='1.75' fill='%23F0EDE5'/><rect x='3.5' y='6' width='13' height='3.5' rx='1.75' fill='%23F0EDE5'/><rect x='7' y='12' width='6' height='3.5' rx='1.75' fill='%2300D46A'/><rect x='9' y='18' width='2' height='3.5' rx='1' fill='%2300D46A'/></g></svg>",
)

# ── Inject website design system ───────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Serif:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
  .stApp { background: #FDFCF7; }
  h1, h2, h3 { font-family: 'IBM Plex Serif', serif; color: #111110; }
  .refinery-brand { font-family: 'IBM Plex Serif', serif; font-style: italic; font-weight: 700;
                    font-size: 28px; letter-spacing: -0.5px; color: #111110; }
  .badge-flag { background: #C0392B22; color: #C0392B; padding: 6px 14px; border-radius: 3px;
                font-family: 'IBM Plex Mono', monospace; font-weight: 700; font-size: 14px; }
  .badge-pass { background: #00D46A22; color: #00A854; padding: 6px 14px; border-radius: 3px;
                font-family: 'IBM Plex Mono', monospace; font-weight: 700; font-size: 14px; }
  .bob-panel { background: #0C0C0A; border-radius: 6px; padding: 20px; color: #C4C0B6;
               font-family: 'IBM Plex Sans', sans-serif; margin-top: 16px; }
  .bob-headline { color: #FDFCF7; font-size: 15px; font-weight: 600; margin-bottom: 10px; }
  .bob-body { font-size: 13px; line-height: 1.7; color: #C4C0B6; }
  .bob-remediation { color: #DDA63A; margin-top: 10px; font-size: 12px; }
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #00D46A; color: #0E0E0C; border: none; font-family: 'IBM Plex Mono', monospace;
    font-weight: 500; border-radius: 3px;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover { background: #00B85C; }
</style>
""", unsafe_allow_html=True)

SAMPLES = Path(__file__).parent / "sample_files"

# ── Header ─────────────────────────────────────────────────────────
st.markdown('<div class="refinery-brand">Refinery</div>', unsafe_allow_html=True)
st.caption("AI Change Contract Enforcer · IBM Bob modifies the COBOL · Refinery maps the blast radius and blocks unsafe deployments")
st.divider()

col_in, col_out = st.columns([1, 1], gap="large")

# ── Left column: inputs ────────────────────────────────────────────
with col_in:
    st.subheader("Upload COBOL pair")
    st.caption("Upload your own files, or use a pre-built scenario below.")
    orig_upload = st.file_uploader("Original COBOL (pre-Bob)", type=["cob", "cbl", "txt"], key="orig")
    mod_upload  = st.file_uploader("AI-Modified COBOL (post-Bob)", type=["cob", "cbl", "txt"], key="mod")

    st.divider()
    st.caption("Pre-built scenarios")
    scenario = st.radio(
        "scenario",
        ["FLAGGED — COMPUTE drift in interest calculation", "PASS — COMP-3 optimisation"],
        label_visibility="collapsed",
    )

    # Auto-load sample on first visit
    if "s_orig" not in st.session_state:
        st.session_state["s_orig"] = SAMPLES / "interest_calc_original.cob"
        st.session_state["s_mod"]  = SAMPLES / "interest_calc_ai_flagged.cob"
        st.session_state["auto_run"] = True

    load_col, run_col = st.columns(2)
    with load_col:
        if st.button("Load sample", use_container_width=True):
            if "FLAGGED" in scenario:
                st.session_state["s_orig"] = SAMPLES / "interest_calc_original.cob"
                st.session_state["s_mod"]  = SAMPLES / "interest_calc_ai_flagged.cob"
            else:
                st.session_state["s_orig"] = SAMPLES / "payroll_original.cob"
                st.session_state["s_mod"]  = SAMPLES / "payroll_ai_pass.cob"

    with run_col:
        run = st.button("Generate Change Contract", type="primary", use_container_width=True)

    if st.session_state.pop("auto_run", False):
        run = True

# ── Resolve file paths ─────────────────────────────────────────────
orig_path: Path | None = None
mod_path:  Path | None = None

if orig_upload and mod_upload:
    with tempfile.NamedTemporaryFile(suffix=".cob", delete=False) as f:
        f.write(orig_upload.read())
        orig_path = Path(f.name)
    with tempfile.NamedTemporaryFile(suffix=".cob", delete=False) as f:
        f.write(mod_upload.read())
        mod_path = Path(f.name)
elif "s_orig" in st.session_state:
    orig_path = st.session_state["s_orig"]
    mod_path  = st.session_state["s_mod"]

# ── Right column: results ──────────────────────────────────────────
with col_out:
    if run and orig_path and mod_path:
        with st.spinner("Mapping blast radius across 8 verification layers..."):
            audit = run_audit(orig_path, mod_path)
            narrative = narrate(audit)
            d = audit.diff

        # Verdict badge
        if d.verdict == "FLAGGED":
            st.markdown('<span class="badge-flag">&#9888; FLAGGED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-pass">&#10003; PASS</span>', unsafe_allow_html=True)

        st.write("")
        m1, m2, m3 = st.columns(3)
        m1.metric("Blast Radius Score", f"{d.risk_score}/100")
        m2.metric("CPU change", f"{d.reduction_pct:+.1f}%")
        m3.metric("Verification layers", str(d.checks_run))

        # Semantic changes
        if d.semantic_changes:
            with st.expander(f"Semantic changes ({len(d.semantic_changes)} found)"):
                for c in d.semantic_changes:
                    st.markdown(f"**[{c.severity}]** `{c.change_type}` @ `{c.location}`")
                    st.code(f"Original: {c.original}\nModified: {c.modified}", language="text")

        # Bob narrative panel
        risk_list_html = ""
        if narrative.risk_items:
            items = "".join(f"<li>{item}</li>" for item in narrative.risk_items)
            risk_list_html = f"<ul style='margin-top:10px;padding-left:18px'>{items}</ul>"

        st.markdown(f"""
        <div class="bob-panel">
          <div style="color:#00D46A;font-family:'IBM Plex Mono',monospace;font-size:11px;
                      margin-bottom:12px;letter-spacing:1px;">&#x2B21; BOB RISK NARRATIVE</div>
          <div class="bob-headline">{narrative.headline}</div>
          <div class="bob-body">{narrative.executive_summary}</div>
          {risk_list_html}
          <div class="bob-remediation"><strong>Remediation:</strong> {narrative.remediation}</div>
        </div>
        """, unsafe_allow_html=True)

        # Blast Radius panel
        impact = getattr(audit, "impact", None)
        if impact is not None:
            st.divider()
            st.subheader("Estate Blast Radius")
            br1, br2 = st.columns(2)
            br1.metric("Systems affected", len(impact.affected_systems))
            score_color = "🔴" if impact.blast_radius_score > 50 else "🟡" if impact.blast_radius_score > 25 else "🟢"
            br2.metric("Blast Radius Score", f"{score_color} {impact.blast_radius_score}/100")

            if impact.direct_callers:
                with st.expander(f"Direct callers ({len(impact.direct_callers)})"):
                    for s in impact.direct_callers:
                        st.markdown(f"- `{s}`")
            if impact.copybook_siblings:
                with st.expander(f"Copybook siblings ({len(impact.copybook_siblings)}) — mismatched layout risk"):
                    for s in impact.copybook_siblings:
                        st.markdown(f"- `{s}`")
            if impact.vsam_co_accessors:
                with st.expander(f"VSAM co-accessors ({len(impact.vsam_co_accessors)})"):
                    for s in impact.vsam_co_accessors:
                        st.markdown(f"- `{s}`")
            if impact.batch_jobs_at_risk:
                with st.expander(f"Batch jobs at risk ({len(impact.batch_jobs_at_risk)})"):
                    for s in impact.batch_jobs_at_risk:
                        st.markdown(f"- `{s}`")
            if impact.blast_radius_score > 50:
                st.error("CRO sign-off required — blast radius exceeds threshold (>50). Bot exits with code 2.")
        else:
            st.divider()
            with st.expander("Estate Blast Radius"):
                st.info("Run the estate indexer first: `python -m estate index --root ./your-estate --db estate.db`, then pass `estate_root` to `run_audit()` to see cross-system impact.")

        # PDF download
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = Path(f.name)
        sha256 = generate_pdf(audit, pdf_path, narrative)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Change Contract (PDF)",
                f.read(),
                file_name=f"refinery_change_contract_{audit.date}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        st.caption(f"SHA-256: `{sha256[:16]}...` — chain of custody sealed")

    elif run:
        st.warning("Upload files or load a sample first.")
    else:
        st.info("Upload a COBOL pair (original + IBM Bob modified), or load a sample scenario, then click Generate Change Contract.")
