"""
Phase 8: PDF Report Generator using ReportLab
Generates a professional downloadable contract analysis report.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

# Color palette
NAVY = colors.HexColor('#0F1B35')
SLATE = colors.HexColor('#1E3A5F')
ACCENT = colors.HexColor('#2D7DD2')
LIGHT_BG = colors.HexColor('#F0F4F8')
WHITE = colors.white

RISK_COLORS = {
    "Critical": colors.HexColor('#DC2626'),
    "High": colors.HexColor('#EA580C'),
    "Medium": colors.HexColor('#D97706'),
    "Low": colors.HexColor('#16A34A'),
}

RISK_BG = {
    "Critical": colors.HexColor('#FEF2F2'),
    "High": colors.HexColor('#FFF7ED'),
    "Medium": colors.HexColor('#FFFBEB'),
    "Low": colors.HexColor('#F0FDF4'),
}


def generate_pdf_report(summary: dict, analyzed_clauses: list[dict], filename: str = "contract_analysis.pdf") -> bytes:
    """Generate full PDF analysis report and return as bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = _build_styles()
    story = []

    # --- Cover Header ---
    story.append(_build_header(styles, summary))
    story.append(Spacer(1, 8 * mm))

    # --- Executive Summary ---
    story.append(Paragraph("Executive Summary", styles['section_heading']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=4))

    summary_data = [
        ["Contract Type", summary.get("contract_type", "N/A")],
        ["Parties", summary.get("parties", "N/A")],
        ["Overall Risk", summary.get("overall_risk", "N/A")],
        ["Total Clauses", str(len(analyzed_clauses))],
        ["Average Risk Score", f"{summary.get('avg_score', 0):.1f} / 100"],
        ["Report Date", datetime.now().strftime("%B %d, %Y")],
    ]
    t = Table(summary_data, colWidths=[55 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), SLATE),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 6 * mm))

    # --- Risk Distribution ---
    story.append(Paragraph("Risk Distribution", styles['section_heading']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=4))
    rc = summary.get("risk_counts", {})
    risk_rows = [["Risk Level", "Count", "Visual"]]
    for lvl in ["Critical", "High", "Medium", "Low"]:
        count = rc.get(lvl, 0)
        bar = "|" * min(count * 2, 30) if count > 0 else "-"
        risk_rows.append([lvl, str(count), bar])

    rt = Table(risk_rows, colWidths=[45 * mm, 25 * mm, 95 * mm])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SLATE),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (0, 1), RISK_COLORS.get("Critical", colors.red)),
        ('TEXTCOLOR', (0, 2), (0, 2), RISK_COLORS.get("High", colors.orange)),
        ('TEXTCOLOR', (0, 3), (0, 3), RISK_COLORS.get("Medium", colors.gold)),
        ('TEXTCOLOR', (0, 4), (0, 4), RISK_COLORS.get("Low", colors.green)),
    ]))
    story.append(rt)
    story.append(Spacer(1, 6 * mm))

    # --- Key Findings & Recommendations ---
    findings = summary.get("key_findings", [])
    recs = summary.get("recommendations", [])

    if findings:
        story.append(Paragraph("Key Findings", styles['section_heading']))
        story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=4))
        for f in findings:
            story.append(Paragraph(f"- {escape(str(f))}", styles['body_text']))
        story.append(Spacer(1, 4 * mm))

    if recs:
        story.append(Paragraph("Recommendations", styles['section_heading']))
        story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=4))
        for r in recs:
            story.append(Paragraph(f"- {escape(str(r))}", styles['body_text']))
        story.append(Spacer(1, 6 * mm))

    # --- Clause Analysis Table ---
    story.append(Paragraph("Clause-by-Clause Analysis", styles['section_heading']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=4))

    for clause in analyzed_clauses:
        level = clause.get("risk_level", "Low")
        score = clause.get("risk_score", 0)
        rc_color = RISK_COLORS.get(level, colors.gray)
        bg_color = RISK_BG.get(level, WHITE)

        heading = escape(str(clause.get("heading", "Clause"))[:80])
        clause_type = escape(str(clause.get("type", "General")))
        explanation = escape(str(clause.get("explanation", "")))
        review_pts = [escape(str(point)) for point in clause.get("review_points", [])]

        block = []
        # Clause header row
        header_data = [[
            Paragraph(f"<b>{escape(str(clause.get('index', '')))}. {heading}</b>", styles['clause_heading']),
            Paragraph(f"<b>{clause_type}</b>", styles['clause_type']),
            Paragraph(f"<b>{escape(str(level))} - {escape(str(score))}/100</b>", styles['risk_label']),
        ]]
        ht = Table(header_data, colWidths=[75 * mm, 50 * mm, 40 * mm])
        ht.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 1.0, rc_color),
            ('TEXTCOLOR', (2, 0), (2, 0), rc_color),
        ]))
        block.append(ht)

        if explanation:
            block.append(Paragraph(explanation, styles['explanation']))
        if review_pts:
            for pt in review_pts[:3]:
                block.append(Paragraph(f"  - {pt}", styles['review_point']))

        block.append(Spacer(1, 3 * mm))
        story.append(KeepTogether(block))

    # --- Disclaimer ---
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1')))
    story.append(Spacer(1, 3 * mm))
    disclaimer = ("DISCLAIMER: This report is generated by an AI system for informational and "
                  "educational purposes only. It does not constitute professional legal advice. "
                  "Always consult a qualified attorney before making legal decisions.")
    story.append(Paragraph(disclaimer, styles['disclaimer']))

    doc.build(story)
    return buffer.getvalue()


def _build_header(styles, summary):
    header_data = [[
        Paragraph("AI Legal Contract Analyzer", styles['title']),
        Paragraph(f"<b>{escape(str(summary.get('contract_type', 'Contract Analysis')))}</b><br/>Generated: {datetime.now().strftime('%b %d, %Y')}", styles['subtitle']),
    ]]
    t = Table(header_data, colWidths=[110 * mm, 55 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t


def _build_styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', fontSize=16, textColor=WHITE, fontName='Helvetica-Bold', leading=20),
        'subtitle': ParagraphStyle('subtitle', fontSize=9, textColor=colors.HexColor('#94A3B8'), fontName='Helvetica', alignment=TA_LEFT, leading=13),
        'section_heading': ParagraphStyle('sh', fontSize=12, textColor=SLATE, fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=2),
        'clause_heading': ParagraphStyle('ch', fontSize=9, textColor=NAVY, fontName='Helvetica-Bold'),
        'clause_type': ParagraphStyle('ct', fontSize=8, textColor=SLATE, fontName='Helvetica'),
        'risk_label': ParagraphStyle('rl', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER),
        'body_text': ParagraphStyle('bt', fontSize=9, textColor=colors.HexColor('#374151'), fontName='Helvetica', leading=13, spaceAfter=2),
        'explanation': ParagraphStyle('ex', fontSize=8.5, textColor=colors.HexColor('#374151'), fontName='Helvetica', leading=12, leftIndent=6, spaceAfter=2),
        'review_point': ParagraphStyle('rp', fontSize=8, textColor=colors.HexColor('#6B7280'), fontName='Helvetica', leading=11, leftIndent=12),
        'disclaimer': ParagraphStyle('disc', fontSize=7.5, textColor=colors.HexColor('#6B7280'), fontName='Helvetica-Oblique', leading=11, alignment=TA_JUSTIFY),
    }
