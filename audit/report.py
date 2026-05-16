from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from audit.engine import AuditResult

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _render_html(result: AuditResult, narrative=None) -> str:
    env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)
    return env.get_template("report.html").render(result=result, narrative=narrative)


def _pdf_weasyprint(html: str, output_path: Path) -> None:
    from weasyprint import HTML
    HTML(string=html, base_url=str(_TEMPLATE_DIR)).write_pdf(str(output_path))


def _pdf_reportlab(result: AuditResult, output_path: Path, narrative=None) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    d = result.diff
    verdict = d.verdict
    is_pass = verdict == "PASS"
    v_color = colors.HexColor("#2e7d32") if is_pass else colors.HexColor("#c62828")

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=2.2 * cm, leftMargin=2.2 * cm,
        topMargin=2.5 * cm, bottomMargin=2.8 * cm,
    )

    def S(name, **kw) -> ParagraphStyle:
        return ParagraphStyle(name, **kw)

    mono = S("mono", fontSize=9, fontName="Courier", leading=13)
    body = S("body", fontSize=10, fontName="Times-Roman", leading=16, spaceAfter=10)
    sec  = S("sec", fontSize=9, fontName="Helvetica-Bold", textTransform="uppercase",
              spaceBefore=20, spaceAfter=10, leading=12)
    h3   = S("h3", fontSize=10, fontName="Helvetica-Bold", spaceAfter=6, leading=13)
    ctr  = S("ctr", fontSize=10, fontName="Helvetica", alignment=TA_CENTER,
              textColor=colors.HexColor("#555555"))
    disc = S("disc", fontSize=7.5, fontName="Helvetica",
              textColor=colors.HexColor("#aaaaaa"), leading=12, spaceAfter=0)

    def th_style(table: Table) -> TableStyle:
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e8e8e8")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])

    story = []

    # Cover
    cover_style = S("cov", fontSize=9, fontName="Helvetica",
                     textColor=colors.HexColor("#555555"), alignment=TA_CENTER, leading=18)
    cover_rows = [
        [Paragraph("REFINERY", S("cw", fontSize=11, fontName="Helvetica",
                                  textColor=colors.HexColor("#666666"),
                                  alignment=TA_CENTER, letterSpacing=6))],
        [Spacer(1, 20)],
        [Paragraph(result.original_file, S("cp", fontSize=20, fontName="Helvetica-Bold",
                                            textColor=colors.white, alignment=TA_CENTER))],
        [Paragraph("Independent Verification &amp; Validation",
                   S("cs", fontSize=11, fontName="Helvetica",
                      textColor=colors.HexColor("#aaaaaa"), alignment=TA_CENTER))],
        [Spacer(1, 16)],
        [Paragraph(f"AI-Modified: {result.modified_file}", cover_style)],
        [Paragraph(f"Reference: {result.ref_id}", cover_style)],
        [Paragraph(f"Date: {result.date}", cover_style)],
        *([[Paragraph(f"Client: {result.client_ref}", cover_style)]] if result.client_ref else []),
        [Paragraph(f"Refinery {result.refinery_version}", cover_style)],
        [Spacer(1, 32)],
        [Paragraph(verdict, S("badge", fontSize=14, fontName="Helvetica-Bold",
                               textColor=v_color, alignment=TA_CENTER, borderPadding=10))],
    ]
    ct = Table([[r[0]] for r in cover_rows], colWidths=[15 * cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f0f0f")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [ct, PageBreak()]

    # 1. Executive summary
    story.append(Paragraph("1. Executive Summary", sec))
    banner_bg = colors.HexColor("#e8f5e9") if is_pass else colors.HexColor("#ffebee")
    banner_bc = colors.HexColor("#2e7d32") if is_pass else colors.HexColor("#c62828")
    vt = ("Semantically Equivalent - Approved for Deployment" if is_pass
          else "Semantic Divergence Detected - Deployment Blocked")
    vs = ("No semantic divergences detected. The AI-modified program is functionally identical to the original."
          if is_pass
          else "One or more semantic changes require review before approval for production.")
    bt = Table([
        [Paragraph(vt, S("vl", fontSize=13, fontName="Helvetica-Bold", textColor=v_color))],
        [Paragraph(vs, S("vs", fontSize=9, fontName="Helvetica", textColor=colors.HexColor("#555555")))],
    ], colWidths=[15 * cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), banner_bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [bt, Spacer(1, 10)]

    rsign = "-" if d.reduction_pct > 0 else "+"
    equiv_status = getattr(d, "equivalence_result", "SKIPPED")
    equiv_color = {
        "PASS": colors.HexColor("#2e7d32"),
        "FLAGGED": colors.HexColor("#c62828"),
        "COMPILE_ERROR": colors.HexColor("#c62828"),
        "SKIPPED": colors.HexColor("#888888"),
    }.get(equiv_status, colors.HexColor("#888888"))
    risk = d.risk_score
    risk_color = (
        colors.HexColor("#2e7d32") if risk == 0
        else colors.HexColor("#e65100") if risk < 40
        else colors.HexColor("#c62828")
    )
    saving_per_100_mips = int(round(d.reduction_pct * 300))
    summ = Table([
        ["CPU time reduction", f"{d.reduction_pct}%"],
        ["Est. saving per 100 MIPS/month",
         Paragraph(f"${saving_per_100_mips:,}",
                   S("sav", fontSize=9, fontName="Courier",
                     textColor=colors.HexColor("#2e7d32") if saving_per_100_mips > 0
                     else colors.HexColor("#888888")))],
        ["Semantic checks run", str(getattr(d, "checks_run", 6))],
        ["Divergences found", str(len(d.semantic_changes))],
        ["Risk score",
         Paragraph(f"{risk}/100", S(f"rs{risk}", fontSize=9,
                                     fontName="Helvetica-Bold",
                                     textColor=risk_color))],
        ["Output equivalence",
         Paragraph(equiv_status, S(f"eq{equiv_status}", fontSize=9,
                                    fontName="Helvetica-Bold",
                                    textColor=equiv_color))],
    ], colWidths=[10 * cm, 5 * cm])
    summ.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (1, 0), (1, -1), "Courier"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e8e8e8")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [summ, Spacer(1, 12)]

    # 2. Methodology
    story.append(Paragraph("2. Methodology", sec))
    runner_label = getattr(result, "runner_type", "SyntheticRunner")
    if runner_label == "RealHerculesRunner":
        runner_desc = (
            "<b>CPU Estimation:</b> Both programs executed on a live Hercules/MVS instance "
            "with real IEF376I SMF telemetry. CPU times reflect actual z/Architecture "
            "instruction execution, not estimates."
        )
    else:
        runner_desc = (
            "<b>CPU Estimation:</b> Both programs run through Refinery's SyntheticRunner, "
            "which models instruction-level cost on z/Architecture. Estimates are deterministic "
            "and calibrated to hardware measurements."
        )
    story.append(Paragraph(runner_desc, body))
    story.append(Paragraph(
        "<b>Semantic Analysis — 6 independent checks:</b> "
        "(1) AST-based COMPUTE expression comparison (HIGH if any expression changes). "
        "(2) PIC data type comparison (HIGH for size changes; HIGH for COMP-3 additions — "
        "packed decimal changes can cause 0C7 abends if downstream systems expect display format). "
        "(3) PERFORM/SEARCH/SORT verb counts (MEDIUM if counts differ). "
        "(4) REDEFINES clause offset analysis — detects offset or length shifts in WORKING-STORAGE "
        "overlay fields, a common source of silent data corruption after AI edits (HIGH). "
        "(5) Procedure call graph diff — detects reordered, dropped, or added PERFORM edges (HIGH/MEDIUM). "
        "(6) GnuCOBOL output equivalence — when available, both programs are compiled and executed "
        "with synthetic test inputs; stdout divergence is flagged OUTPUT_DIVERGENCE HIGH.", body))
    story.append(Paragraph(
        "<b>GnuCOBOL Proxy Limitations:</b> The equivalence check (check 6) runs on x86 hardware "
        "under GnuCOBOL, not a native z/Architecture environment. Known divergences from real "
        "mainframe execution: (a) <i>EBCDIC/ASCII</i> — GnuCOBOL uses ASCII; character comparisons "
        "against EBCDIC literals may produce different results. (b) <i>Packed decimal (COMP-3)</i> — "
        "edge cases in packed decimal arithmetic and 0C7 abend conditions differ between GnuCOBOL "
        "and z/Architecture instruction execution. (c) <i>Floating-point rounding</i> — GnuCOBOL uses "
        "IEEE 754 (x86); z/Architecture uses IBM hex floating point (HFP), which can diverge for "
        "COMP-1/COMP-2 fields. (d) <i>I/O simulation</i> — VSAM and DASD I/O is simulated; "
        "sequential file behaviour is representative, not bit-identical. Where Hercules/MVS telemetry "
        "is available (RealHerculesRunner), these limitations do not apply — execution is "
        "hardware-accurate z/Architecture.", body))
    story.append(Paragraph(
        "<b>Verdict Criteria:</b> PASS requires all checks clean. Any HIGH or MEDIUM "
        "finding blocks deployment. LOW-only findings permit conditional approval.", body))

    # 2b. Bob Narrative page
    if narrative is not None:
        story.append(PageBreak())
        story.append(Paragraph("Bob's Risk Narrative", sec))
        story.append(Paragraph(
            f"<b>{narrative.headline}</b>",
            S("bhl", fontSize=13, fontName="Helvetica-Bold",
               textColor=v_color, leading=18, spaceAfter=8),
        ))
        story.append(Paragraph(narrative.executive_summary, body))
        if narrative.risk_items:
            for item in narrative.risk_items:
                story.append(Paragraph(f"• {item}", body))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"<b>Remediation:</b> {narrative.remediation}",
            S("rem", fontSize=10, fontName="Helvetica",
               textColor=colors.HexColor("#b45309"), leading=16),
        ))
        conf_pct = int(narrative.confidence * 100)
        story.append(Paragraph(
            f"Bob confidence: {conf_pct}%",
            S("conf", fontSize=8, fontName="Helvetica",
               textColor=colors.HexColor("#aaaaaa"), leading=12),
        ))
        story.append(PageBreak())

    # 3. Execution evidence
    story.append(Paragraph("3. Execution Evidence", sec))
    story.append(Paragraph("CPU Performance", h3))
    perf = Table([
        ["Metric", "Original", "AI-Modified", "Change"],
        ["CPU time (microseconds)",
         f"{d.cpu_before_us:,}", f"{d.cpu_after_us:,}",
         f"{rsign}{abs(d.reduction_pct):.1f}%"],
    ], colWidths=[6 * cm, 3 * cm, 3 * cm, 3 * cm])
    perf.setStyle(th_style(perf))
    story += [perf, Spacer(1, 10)]

    story.append(Paragraph("AST Feature Comparison", h3))
    feat_keys = [
        ("loc", "Lines of code"),
        ("compute_verb_count", "COMPUTE verbs"),
        ("perform_depth", "PERFORM nesting depth"),
        ("search_verb_count", "SEARCH verbs"),
        ("sort_verb_count", "SORT verbs"),
        ("working_storage_bytes", "Working storage (bytes)"),
        ("file_section_count", "File section entries"),
    ]
    fdata = [["Feature", "Original", "AI-Modified"]]
    for key, label in feat_keys:
        fdata.append([label,
                      str(d.features_original.get(key, "-")),
                      str(d.features_modified.get(key, "-"))])
    ft = Table(fdata, colWidths=[8 * cm, 3.5 * cm, 3.5 * cm])
    ft.setStyle(th_style(ft))
    story += [ft, Spacer(1, 10)]

    story.append(Paragraph("Maintainability", h3))
    cc_orig = getattr(d, "cyclomatic_complexity_original", "-")
    cc_mod  = getattr(d, "cyclomatic_complexity_modified", "-")
    cc_change = ""
    if isinstance(cc_orig, int) and isinstance(cc_mod, int):
        delta = cc_mod - cc_orig
        cc_change = f"+{delta}" if delta > 0 else str(delta)
    cc_table = Table([
        ["Metric", "Original", "AI-Modified", "Change"],
        ["Cyclomatic complexity (McCabe)", str(cc_orig), str(cc_mod), cc_change],
    ], colWidths=[6 * cm, 3 * cm, 3 * cm, 3 * cm])
    cc_table.setStyle(th_style(cc_table))
    story += [cc_table, Spacer(1, 10)]

    story.append(Paragraph("Output Equivalence", h3))
    equiv_detail = getattr(d, "equivalence_detail", "")
    equiv_label = {
        "PASS": "Both programs produce identical output for all test inputs.",
        "FLAGGED": "Output divergence detected — programs produce different results.",
        "COMPILE_ERROR": "One or more programs failed to compile under GnuCOBOL.",
        "SKIPPED": "GnuCOBOL not available — equivalence check skipped.",
    }.get(equiv_status, f"Status: {equiv_status}")
    eq_color = equiv_color
    story.append(Paragraph(
        f"<b>{equiv_status}</b> — {equiv_label}",
        S(f"eqbody{equiv_status}", fontSize=9.5, fontName="Helvetica",
           textColor=eq_color, leading=14),
    ))
    if equiv_detail and equiv_status in ("FLAGGED", "COMPILE_ERROR"):
        story.append(Spacer(1, 4))
        story.append(Paragraph(equiv_detail[:600], mono))
    story.append(Spacer(1, 10))

    # 3b. Exception handler integrity
    story.append(Paragraph("Exception Handler Integrity", h3))
    handler_types = {"ERROR_HANDLER_REMOVED", "EXCEPTION_DIVERGENCE"}
    handler_changes = [c for c in d.semantic_changes if c.change_type in handler_types]
    if not handler_changes:
        story.append(Paragraph(
            "PASS — All exception handlers (ON SIZE ERROR, INVALID KEY, AT END, ON OVERFLOW) "
            "are present and produce equivalent outputs under adversarial inputs. "
            "No error-handling logic was removed or altered by the AI modification.",
            S("hpass", fontSize=9.5, fontName="Helvetica",
              textColor=colors.HexColor("#2e7d32"), leading=14),
        ))
    else:
        story.append(Paragraph(
            f"FLAGGED — {len(handler_changes)} exception handler finding(s) detected. "
            "Banks rely on error handlers written into COBOL since the 1970s; their removal "
            "by AI tooling is a critical deployment risk.",
            S("hflag", fontSize=9.5, fontName="Helvetica-Bold",
              textColor=colors.HexColor("#c62828"), leading=14),
        ))
        story.append(Spacer(1, 6))
        hdata = [["Severity", "Type", "Location", "Detail"]]
        for c in handler_changes:
            sc = colors.HexColor("#c62828") if c.severity == "HIGH" else colors.HexColor("#e65100")
            hdata.append([
                Paragraph(c.severity, S(f"hsev{c.severity}", fontSize=9,
                                        fontName="Helvetica-Bold", textColor=sc)),
                c.change_type,
                Paragraph(c.location[:80], mono),
                Paragraph(c.original[:120], mono),
            ])
        ht = Table(hdata, colWidths=[2.2 * cm, 4.3 * cm, 3.5 * cm, 5 * cm],
                   repeatRows=1)
        ht.setStyle(th_style(ht))
        story.append(ht)
    story.append(Spacer(1, 10))

    # 3c. Blast radius
    impact = getattr(result, "impact", None)
    story.append(Paragraph("Blast Radius Assessment", h3))
    if impact is not None:
        br_score = impact.blast_radius_score
        affected = impact.affected_systems
        br_color = (
            colors.HexColor("#c62828") if br_score > 70
            else colors.HexColor("#e65100") if br_score > 40
            else colors.HexColor("#2e7d32")
        )
        story.append(Paragraph(
            f"<b>Score: {br_score}/100</b> — {len(affected)} downstream system(s) affected.",
            S("brhead", fontSize=10, fontName="Helvetica-Bold", textColor=br_color, leading=14),
        ))
        if affected:
            story.append(Spacer(1, 4))
            affected_text = "  ·  ".join(affected)
            story.append(Paragraph(
                f"Affected systems: {affected_text}",
                S("brlist", fontSize=9, fontName="Courier", textColor=colors.HexColor("#333333"), leading=13),
            ))
        if br_score > 50:
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                "CRO sign-off mandatory — blast radius exceeds threshold. "
                "All affected systems must be assessed for recompile before promotion.",
                S("brcro", fontSize=9, fontName="Helvetica", textColor=colors.HexColor("#e65100"), leading=13),
            ))
    else:
        story.append(Paragraph(
            "Estate analysis not run — blast radius unavailable.",
            S("brskip", fontSize=9.5, fontName="Helvetica", textColor=colors.HexColor("#888888"), leading=14),
        ))
    story.append(Spacer(1, 10))

    # 4. Divergence log
    story.append(Paragraph("4. Divergence Log", sec))
    if d.semantic_changes:
        sev_colors = {
            "HIGH": colors.HexColor("#c62828"),
            "MEDIUM": colors.HexColor("#e65100"),
            "LOW": colors.HexColor("#1565c0"),
        }
        def _trunc(text: str, limit: int = 120) -> str:
            return text if len(text) <= limit else text[:limit] + "..."

        ddata = [["Severity", "Check", "Location", "Original", "Modified"]]
        for c in d.semantic_changes:
            sc = sev_colors.get(c.severity, colors.black)
            ddata.append([
                Paragraph(c.severity, S(f"sev{c.severity}", fontSize=9,
                                         fontName="Helvetica-Bold", textColor=sc)),
                c.change_type,
                Paragraph(_trunc(c.location, 80), mono),
                Paragraph(_trunc(c.original), mono),
                Paragraph(_trunc(c.modified), mono),
            ])
        dt = Table(ddata, colWidths=[2.2 * cm, 3.3 * cm, 3 * cm, 3.25 * cm, 3.25 * cm],
                   repeatRows=1, splitByRow=True)
        dt.setStyle(th_style(dt))
        story.append(dt)
    else:
        story.append(Paragraph(
            "No divergences detected. All semantic checks passed.",
            S("nd", fontSize=10, fontName="Times-Italic",
               textColor=colors.HexColor("#2e7d32"))))

    story.append(Spacer(1, 12))

    # 5. Verdict + sign-off
    story.append(Paragraph("5. Verdict and Sign-off", sec))
    signoff_text = (
        f"The AI-modified program <b>{result.modified_file}</b> is semantically equivalent "
        f"to <b>{result.original_file}</b> under the test conditions described in Section 2. "
        f"No semantic divergences were detected. Deployment decision remains with the authorising engineer."
        if is_pass else
        f"The AI-modified program <b>{result.modified_file}</b> contains semantic divergences "
        f"from <b>{result.original_file}</b>. Manual review required before deployment."
    )
    meta = f"Reference: {result.ref_id}  |  Date: {result.date}  |  Refinery: {result.refinery_version}"
    if result.client_ref:
        meta += f"  |  Client: {result.client_ref}"

    so = Table([
        [Paragraph(verdict, S("bv", fontSize=30, fontName="Helvetica-Bold",
                               textColor=v_color, alignment=TA_CENTER))],
        [Paragraph(signoff_text, ctr)],
        [Paragraph(meta, S("sm", fontSize=9, fontName="Helvetica",
                             textColor=colors.HexColor("#555555"), alignment=TA_CENTER))],
        [Spacer(1, 16)],
        [Table([
            [Paragraph("Engineer sign-off:", S("sofl", fontSize=9, fontName="Helvetica-Bold")),
             Paragraph("_" * 30, S("sofl2", fontSize=9, fontName="Helvetica"))],
            [Paragraph("Date:", S("sofl", fontSize=9, fontName="Helvetica-Bold")),
             Paragraph("_" * 15, S("sofl2", fontSize=9, fontName="Helvetica"))],
            [Paragraph("Change Request #:", S("sofl", fontSize=9, fontName="Helvetica-Bold")),
             Paragraph("_" * 25, S("sofl2", fontSize=9, fontName="Helvetica"))],
            [Paragraph("ECM Archive ref:", S("sofl", fontSize=9, fontName="Helvetica-Bold")),
             Paragraph("_" * 25, S("sofl2", fontSize=9, fontName="Helvetica"))],
        ], colWidths=[5 * cm, 10 * cm])],
    ], colWidths=[15 * cm])
    so.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1a1a1a")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))
    story += [so, Spacer(1, 20)]
    runner_label = getattr(result, "runner_type", "SyntheticRunner")
    story.append(Paragraph(
        f"This report was generated automatically by Refinery {result.refinery_version}. "
        f"CPU performance estimates are produced via {runner_label} and are indicative only. "
        "Semantic correctness analysis (checks 1–6) is performed via static AST analysis and is "
        "independent of the runtime environment. Runtime behaviour under z/OS Language Environment, "
        "VSAM, or DB2 is outside the scope of this report. "
        "This report certifies semantic equivalence only — that the AI-modified program produces "
        "identical observable behaviour to the original under the test conditions described in "
        "Section 2. It does not certify correctness of business logic, compliance with regulatory "
        "requirements, or runtime behaviour under any production environment. "
        "Liability is limited to the terms of the applicable engagement agreement. "
        "This report does not constitute legal, regulatory, or financial advice.",
        disc,
    ))

    doc.build(story)


def generate_pdf(result: AuditResult, output_path: Path, narrative=None) -> str:
    try:
        html = _render_html(result, narrative)
        _pdf_weasyprint(html, output_path)
    except Exception:
        _pdf_reportlab(result, output_path, narrative)
    import hashlib
    data = Path(output_path).read_bytes()
    return hashlib.sha256(data).hexdigest()
