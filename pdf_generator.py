# File: pdf_generator.py
# Version: 1.1
# Last Updated: 2026-03-27
# Changes: 移除标题和日期；添加页码；竖式/混合运算6类每行2题+8行空行
# Status: COMPLETE

import os
import re
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# 需要每行2题+8行空行的题型
VERTICAL_TYPES = {
    "vert_addsub",    # 竖式加减法
    "vert_mul",       # 竖式乘法
    "vert_div",       # 竖式除法
    "mixed_all",      # 加减乘除混合
    "mixed_bracket",  # 带括号混合运算
    "solve_tri",     # 求未知数△
}

# 12行空行（无下划线）
TWELVE_BLANK_LINES = "\n" * 12


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
                pdfmetrics.registerFont(TTFont('ChineseFont', path))
                return 'ChineseFont'
            except Exception:
                continue
    return None


CHINESE_FONT = _register_chinese_font()


def _make_styles():
    base = CHINESE_FONT or 'Helvetica'
    return {
        'section': ParagraphStyle(
            'Section',
            fontName=base, fontSize=14, leading=18,
            alignment=TA_LEFT, spaceBefore=6*mm, spaceAfter=3*mm,
            textColor=HexColor('#212121'),
        ),
        'question': ParagraphStyle(
            'Question',
            fontName=base, fontSize=12, leading=16,
            alignment=TA_LEFT, spaceAfter=2*mm,
            textColor=HexColor('#212121'),
        ),
        'footer': ParagraphStyle(
            'Footer',
            fontName=base, fontSize=10, leading=13,
            alignment=TA_CENTER, textColor=HexColor('#9E9E9E'),
        ),
    }


def _build_q_table(section_name, questions, qtype, styles, start_num):
    """为竖式/混合类构建两列+空行的 Table，不跨页分组"""
    is_vertical = qtype in VERTICAL_TYPES
    q_style = styles['question']

    if is_vertical:
        # 每2题+6行空行 → 一个小Table → KeepTogether（禁止跨页拆分）
        paired = [(questions[i], questions[i+1] if i+1 < len(questions) else None)
                  for i in range(0, len(questions), 2)]
        flowables = []
        for idx, (q1, q2) in enumerate(paired):
            num = start_num + idx * 2
            q_rows = []
            row_heights = []
            if q2 is not None:
                num2 = num + 1
                q_rows.append([Paragraph(f"{num}. {q1}", q_style),
                              Paragraph(f"{num2}. {q2}", q_style)])
            else:
                q_rows.append([Paragraph(f"{num}. {q1}", q_style), Paragraph("", q_style)])
            row_heights.append(None)
            for _ in range(6):
                q_rows.append([Paragraph("", q_style), Paragraph("", q_style)])
                row_heights.append(8*mm)
            sub_table = Table(q_rows, colWidths=[None, None], rowHeights=row_heights)
            sub_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
                ('TOPPADDING',  (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING',   (0, 0), (-1, -1), 6),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            flowables.append(KeepTogether([sub_table]))
        return flowables  # list of KeepTogether

    else:
        # 普通：一列一题
        rows = []
        for idx, q in enumerate(questions):
            num = start_num + idx
            rows.append([Paragraph(f"{num}.  {q}", q_style)])
        col_widths = [170 * mm] if len(rows) <= 1 else None
        table = Table(rows, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#FFFFFF')),
            ('TOPPADDING',  (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return table


def _draw_page_number(c, doc, total_pages):
    """在页脚绘制页码"""
    c.saveState()
    c.setFont(CHINESE_FONT or 'Helvetica', 9)
    c.setFillColor(HexColor('#9E9E9E'))
    page_num = c.getPageNumber()
    if total_pages > 0:
        text = f"第 {page_num} 页 / 共 {total_pages} 页"
    else:
        text = f"第 {page_num} 页"
    c.drawCentredString(doc.leftMargin + doc.width / 2, 12*mm, text)
    c.restoreState()


class PDFGenerator:
    """PDF 试卷生成器"""

    def _make_story(self, questions_data, styles):
        """构建 PDF story"""
        story = []
        total_count = 0
        for section_name, questions, qtype in questions_data:
            start = total_count
            result = _build_q_table(section_name, questions, qtype, styles, start + 1)
            total_count += len(questions)
            story.append(Paragraph(f"【{section_name}】", styles['section']))
            if isinstance(result, list):
                # vertical 类型：result 是 KeepTogether flowables 列表
                story.extend(result)
            else:
                # 非 vertical：result 是单个 Table
                story.append(result)
            story.append(Spacer(1, 4*mm))
        return story

    def get_pdf_bytes(self, questions_data):
        import tempfile, os
        styles = _make_styles()

        # 第一遍：渲染到临时文件，获取总页数
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tmp_doc = SimpleDocTemplate(tmp_path, pagesize=A4,
                                        leftMargin=20*mm, rightMargin=20*mm,
                                        topMargin=18*mm, bottomMargin=22*mm)
            story1 = self._make_story(questions_data, styles)
            tmp_doc.build(story1,
                          onFirstPage=lambda c, d: _draw_page_number(c, d, 0),
                          onLaterPages=lambda c, d: _draw_page_number(c, d, 0))
            with open(tmp_path, 'rb') as f:
                tmp_content = f.read()
            total_pages = len(re.findall(b'/Type /Page', tmp_content))
        finally:
            os.unlink(tmp_path)

        # 第二遍：正式渲染（story 须重新构建，flowables 不可复用）
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=18*mm, bottomMargin=22*mm)
        story2 = self._make_story(questions_data, styles)
        doc.build(story2,
                  onFirstPage=lambda c, d: _draw_page_number(c, d, total_pages),
                  onLaterPages=lambda c, d: _draw_page_number(c, d, total_pages))
        return buffer.getvalue()


def generate_default_filename():
    return f"数学练习_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
