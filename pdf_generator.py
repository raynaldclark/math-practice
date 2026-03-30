# File: pdf_generator.py
# Version: 2.0
# Last Updated: 2026-03-30
# Changes: 支持答案数据，最后一页添加答案
# Status: COMPLETE

import os
import re
import tempfile
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER


VERTICAL_TYPES = {
    "vert_addsub",
    "vert_mul",
    "vert_div",
    "mixed_all",
    "mixed_bracket",
    "solve_tri",
}

CHINESE_FONT = None


def _register_chinese_font():
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simkai.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", path))
                return "ChineseFont"
            except Exception:
                continue
    return None


CHINESE_FONT = _register_chinese_font()


def _make_styles():
    base = CHINESE_FONT or "Helvetica"
    return {
        "section": ParagraphStyle(
            "Section",
            fontName=base,
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
            textColor=HexColor("#212121"),
        ),
        "question": ParagraphStyle(
            "Question",
            fontName=base,
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=2 * mm,
            textColor=HexColor("#212121"),
        ),
        "answer": ParagraphStyle(
            "Answer",
            fontName=base,
            fontSize=11,
            leading=15,
            alignment=TA_LEFT,
            spaceAfter=1 * mm,
            textColor=HexColor("#424242"),
            bulletText=None,
        ),
        "footer": ParagraphStyle(
            "Footer",
            fontName=base,
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=HexColor("#9E9E9E"),
        ),
        "answer_title": ParagraphStyle(
            "AnswerTitle",
            fontName=base,
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceBefore=10 * mm,
            spaceAfter=8 * mm,
            textColor=HexColor("#1565C0"),
        ),
    }


def _build_q_table(section_name, questions, answers, qtype, styles, start_num):
    """为竖式/混合类构建两列+空行的 Table"""
    is_vertical = qtype in VERTICAL_TYPES
    q_style = styles["question"]

    if is_vertical:
        paired = [
            (questions[i], answers[i] if i < len(answers) else "")
            for i in range(0, len(questions), 2)
        ]
        flowables = []
        for idx, (q1, a1) in enumerate(paired):
            num = start_num + idx * 2
            q_rows = []
            row_heights = []
            if len(questions) > idx * 2 + 1:
                q2 = questions[idx * 2 + 1]
                num2 = num + 1
                q_rows.append(
                    [
                        Paragraph(f"{num}. {q1}", q_style),
                        Paragraph(f"{num2}. {q2}", q_style),
                    ]
                )
            else:
                q_rows.append(
                    [Paragraph(f"{num}. {q1}", q_style), Paragraph("", q_style)]
                )
            row_heights.append(None)
            for _ in range(6):
                q_rows.append([Paragraph("", q_style), Paragraph("", q_style)])
                row_heights.append(8 * mm)
            sub_table = Table(q_rows, colWidths=[None, None], rowHeights=row_heights)
            sub_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#FFFFFF")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            flowables.append(KeepTogether([sub_table]))
        return flowables

    else:
        rows = []
        for idx, q in enumerate(questions):
            num = start_num + idx
            rows.append([Paragraph(f"{num}.  {q}", q_style)])
        col_widths = [170 * mm] if len(rows) <= 1 else None
        table = Table(rows, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#FFFFFF")),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return table


def _build_answer_content(questions_data, styles):
    """构建答案内容 - 连续排列"""
    a_style = styles["answer"]
    story = []

    story.append(Paragraph("参考答案", styles["answer_title"]))

    total = 0
    for section_name, questions, answers, qtype in questions_data:
        start = total
        story.append(Paragraph(f"【{section_name}】", styles["section"]))

        answer_parts = []
        for idx, ans in enumerate(answers):
            num = start + idx + 1
            num_text = f"{num}."
            ans_text = f"{ans}"
            answer_parts.append(
                f'<font color=HexColor("#1565C0")>{num_text}</font>{ans_text}&#160;&#160;&#160;&#160;'
            )

        answer_line = "".join(answer_parts)
        story.append(Paragraph(answer_line, a_style))
        story.append(Spacer(1, 1 * mm))

        total += len(questions)

    return story


def _draw_page_number(c, doc, total_pages):
    """在页脚绘制页码"""
    c.saveState()
    c.setFont(CHINESE_FONT or "Helvetica", 9)
    c.setFillColor(HexColor("#9E9E9E"))
    page_num = c.getPageNumber()
    if total_pages > 0:
        text = f"第 {page_num} 页 / 共 {total_pages} 页"
    else:
        text = f"第 {page_num} 页"
    c.drawCentredString(doc.leftMargin + doc.width / 2, 12 * mm, text)
    c.restoreState()


class PDFGenerator:
    def _make_story(self, questions_data, styles, include_answer=True):
        """构建 PDF story"""
        story = []
        total_count = 0
        for section_name, questions, answers, qtype in questions_data:
            start = total_count
            result = _build_q_table(
                section_name, questions, answers, qtype, styles, start + 1
            )
            total_count += len(questions)
            story.append(Paragraph(f"【{section_name}】", styles["section"]))
            if isinstance(result, list):
                story.extend(result)
            else:
                story.append(result)
            story.append(Spacer(1, 4 * mm))

        if include_answer:
            story.append(PageBreak())
            story.extend(_build_answer_content(questions_data, styles))

        return story

    def get_pdf_bytes(self, questions_data):
        styles = _make_styles()

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tmp_doc = SimpleDocTemplate(
                tmp_path,
                pagesize=A4,
                leftMargin=20 * mm,
                rightMargin=20 * mm,
                topMargin=18 * mm,
                bottomMargin=22 * mm,
            )
            story1 = self._make_story(questions_data, styles, include_answer=False)
            tmp_doc.build(
                story1,
                onFirstPage=lambda c, d: _draw_page_number(c, d, 0),
                onLaterPages=lambda c, d: _draw_page_number(c, d, 0),
            )
            with open(tmp_path, "rb") as f:
                tmp_content = f.read()
            total_pages = len(re.findall(b"/Type /Page", tmp_content))
        finally:
            os.unlink(tmp_path)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=22 * mm,
        )
        story2 = self._make_story(questions_data, styles, include_answer=True)
        doc.build(
            story2,
            onFirstPage=lambda c, d: _draw_page_number(c, d, total_pages),
            onLaterPages=lambda c, d: _draw_page_number(c, d, total_pages),
        )
        return buffer.getvalue()


def generate_default_filename():
    return f"数学练习_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"