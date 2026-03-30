# File: app_wx.py
# Version: 2.3-wxPython
# Last Updated: 2026-03-28
# Changes:
#   1. 题型选择改为两列Grid布局
#   2. 添加题型大类标题
#   3. 添加运行日志区域（宋体、5行高度）
#   4. 修复批量保存路径（使用exe所在目录）
#   5. 为每个题型添加问号提示
#   6. 按钮随窗口宽度自动分布
# Status: COMPLETE

import wx
import random
import os
import sys
import tempfile
import webbrowser
from datetime import datetime

from question_generator import QUESTION_CATEGORIES, QUESTION_RULES, get_questions_data
from pdf_generator import PDFGenerator, generate_default_filename


# ============ 颜色 ============
COLOR_PRIMARY = wx.Colour(33, 150, 243)  # 蓝色（按钮用）
COLOR_PRIMARY_DARK = wx.Colour(25, 118, 210)  # 深蓝（按钮用）
COLOR_ACCENT = wx.Colour(76, 175, 80)  # 绿色（按钮用）
COLOR_BG = wx.Colour(240, 240, 240)  # 浅灰（背景）
COLOR_CARD = wx.Colour(255, 255, 255)  # 白色（卡片）
COLOR_TEXT = wx.Colour(80, 80, 80)  # 深灰（主文字）
COLOR_TEXT_SEC = wx.Colour(120, 120, 120)  # 中灰（次要文字）
COLOR_DIVIDER = wx.Colour(200, 200, 200)  # 浅灰（分割线）
COLOR_VIOLET = wx.Colour(138, 43, 226)  # 紫罗兰色（批量按钮）


# ============ 题型行 ============
class TypeRow(wx.Panel):
    def __init__(self, parent, type_code, type_name, on_change_callback):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.type_code = type_code  # 英文code，内部存储用
        self.type_name = type_name  # 中文名，checkbox显示用
        self._selected = False
        self._on_change = on_change_callback
        self.SetBackgroundColour(COLOR_CARD)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.checkbox = wx.CheckBox(self, label=type_name)
        self.checkbox.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        self.checkbox.SetForegroundColour(COLOR_TEXT)
        self.checkbox.Bind(wx.EVT_CHECKBOX, self._on_check)

        # 添加问号提示按钮（无背景色）
        help_btn = wx.Button(self, label="?", size=(22, 22), style=wx.BORDER_NONE)
        help_btn.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                faceName="Arial",
            )
        )
        help_btn.SetBackgroundColour(COLOR_CARD)
        help_btn.SetForegroundColour(COLOR_TEXT_SEC)
        help_btn.SetToolTip(QUESTION_RULES.get(type_code, "暂无说明"))

        count_lbl = wx.StaticText(self, label="数量:")
        count_lbl.SetForegroundColour(COLOR_TEXT_SEC)
        count_lbl.SetFont(
            wx.Font(
                11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )
        )

        self.count_input = wx.TextCtrl(
            self, value="5", size=(45, -1), style=wx.TE_CENTER
        )
        self.count_input.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        self.count_input.Bind(wx.EVT_TEXT, self._on_count)

        sizer.Add(
            self.checkbox,
            proportion=1,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=4,
        )
        sizer.Add(help_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=2)
        sizer.Add(count_lbl, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=4)
        sizer.Add(self.count_input, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=2)
        self.SetSizer(sizer)

    def _on_check(self, e):
        self._selected = e.IsChecked()
        self._on_change(self)

    def _on_count(self, e):
        try:
            self._count = max(1, min(20, int(self.count_input.GetValue())))
        except Exception:
            self._count = 5

    def is_selected(self):
        return self._selected

    def set_selected(self, value):
        self._selected = value
        self.checkbox.SetValue(value)

    @property
    def count(self):
        try:
            return max(1, min(20, int(self.count_input.GetValue())))
        except Exception:
            return 5


# ============ 分类卡片（已废弃，保留用于参考） ============
# 现在使用Grid两列布局，分类信息不再单独显示


# ============ 预览弹窗（可滚动） ============
class PreviewDialog(wx.Dialog):
    def __init__(self, parent, questions_data):
        super().__init__(
            parent,
            title="题目预览",
            size=(540, 620),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.questions_data = questions_data

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="小学数学练习题")
        title.SetFont(
            wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        title.SetForegroundColour(COLOR_PRIMARY)
        main_sizer.Add(title, flag=wx.ALIGN_CENTER | wx.TOP, border=16)
        main_sizer.AddSpacer(6)

        scroll = wx.ScrolledWindow(self)
        scroll.SetScrollRate(0, 20)
        scroll.SetBackgroundColour(COLOR_CARD)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        total = 0
        for section_name, questions, answers, _ in questions_data:
            sec_label = wx.StaticText(scroll, label=("【%s】" % section_name))
            sec_label.SetFont(
                wx.Font(
                    12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
                )
            )
            sec_label.SetForegroundColour(COLOR_PRIMARY)
            scroll_sizer.Add(sec_label, flag=wx.LEFT | wx.TOP, border=8)

            for q in questions:
                total += 1
                q_label = wx.StaticText(scroll, label=("%d.  %s" % (total, q)))
                q_label.SetFont(
                    wx.Font(
                        12,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL,
                    )
                )
                q_label.SetForegroundColour(COLOR_TEXT_SEC)
                scroll_sizer.Add(q_label, flag=wx.LEFT, border=20)

        scroll.SetSizer(scroll_sizer)
        main_sizer.Add(
            scroll, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=8
        )

        total_label = wx.StaticText(self, label=("共 %d 题" % total))
        total_label.SetFont(
            wx.Font(
                10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )
        )
        total_label.SetForegroundColour(COLOR_TEXT_SEC)
        main_sizer.Add(total_label, flag=wx.ALIGN_CENTER | wx.TOP, border=4)
        main_sizer.AddSpacer(8)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_btn = wx.Button(self, wx.ID_CANCEL, "关闭")
        close_btn.SetBackgroundColour(COLOR_DIVIDER)
        export_btn = wx.Button(self, wx.ID_OK, "导出 PDF")
        export_btn.SetBackgroundColour(COLOR_ACCENT)
        export_btn.SetForegroundColour(wx.WHITE)
        btn_sizer.Add(close_btn, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=8)
        btn_sizer.Add(export_btn, proportion=1, flag=wx.EXPAND)
        main_sizer.Add(
            btn_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=16
        )

        self.SetSizer(main_sizer)


# ============ 主窗口 ============
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None, title="三年级数学练习", size=(700, 600), style=wx.DEFAULT_FRAME_STYLE
        )
        self.SetBackgroundColour(COLOR_BG)
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(ico_path):
            self.SetIcon(wx.Icon(ico_path))
        self.Center()
        self.all_rows = []
        self._build_ui()

    def _build_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 顶部标题
        header = wx.Panel(self, style=wx.BORDER_NONE)
        header.SetBackgroundColour(COLOR_BG)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        htitle = wx.StaticText(header, label="三年级数学练习")
        htitle.SetFont(
            wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        htitle.SetForegroundColour(COLOR_TEXT)
        header_sizer.AddStretchSpacer()
        header_sizer.Add(htitle, flag=wx.ALIGN_CENTER | wx.ALL, border=12)
        header_sizer.AddStretchSpacer()
        header.SetSizer(header_sizer)
        main_sizer.Add(header, flag=wx.EXPAND)

        # 题型区域 - 左右两列Grid布局（带分类标题）
        categories = list(QUESTION_CATEGORIES.items())

        col_left = wx.Panel(self, style=wx.BORDER_NONE)
        col_left.SetBackgroundColour(COLOR_BG)
        col_right = wx.Panel(self, style=wx.BORDER_NONE)
        col_right.SetBackgroundColour(COLOR_BG)

        mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        def on_change(row):
            pass

        # 按分类整块分配到左右两列
        left_cats = []
        right_cats = []
        total_types = sum(len(types) for _, types in categories)
        left_count = 0

        for cat_name, types in categories:
            cat_types_count = len(types)
            # 判断放哪边：让两边尽量平衡
            if left_count <= (total_types - left_count - cat_types_count):
                left_cats.append((cat_name, types))
                left_count += cat_types_count
            else:
                right_cats.append((cat_name, types))

        # 左列
        for cat_name, types in left_cats:
            title = wx.StaticText(col_left, label=cat_name)
            title.SetFont(
                wx.Font(
                    12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
                )
            )
            title.SetForegroundColour(COLOR_TEXT)
            left_sizer.Add(title, flag=wx.LEFT | wx.TOP, border=8)

            for type_name, type_code in types:
                row = TypeRow(col_left, type_code, type_name, on_change)
                self.all_rows.append(row)
                left_sizer.Add(row, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        # 右列
        for cat_name, types in right_cats:
            title = wx.StaticText(col_right, label=cat_name)
            title.SetFont(
                wx.Font(
                    12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
                )
            )
            title.SetForegroundColour(COLOR_TEXT)
            right_sizer.Add(title, flag=wx.LEFT | wx.TOP, border=8)

            for type_name, type_code in types:
                row = TypeRow(col_right, type_code, type_name, on_change)
                self.all_rows.append(row)
                right_sizer.Add(row, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        col_left.SetSizer(left_sizer)
        col_right.SetSizer(right_sizer)
        mid_sizer.Add(col_left, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=2)
        mid_sizer.Add(col_right, proportion=1, flag=wx.EXPAND)
        main_sizer.Add(mid_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # 底部按钮区（一排，自动分布）
        bottom_bar = wx.Panel(self, style=wx.BORDER_NONE)
        bottom_bar.SetBackgroundColour(COLOR_CARD)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 功能按钮
        btn_sel = wx.Button(bottom_bar, label="全选")
        btn_sel.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        btn_sel.SetBackgroundColour(COLOR_DIVIDER)
        btn_sel.SetForegroundColour(COLOR_TEXT)
        btn_sel.Bind(wx.EVT_BUTTON, self._on_select_all)

        btn_clr = wx.Button(bottom_bar, label="清空")
        btn_clr.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        btn_clr.SetBackgroundColour(COLOR_DIVIDER)
        btn_clr.SetForegroundColour(COLOR_TEXT)
        btn_clr.Bind(wx.EVT_BUTTON, self._on_clear_all)

        self.rand_input = wx.TextCtrl(
            bottom_bar, value="5", size=(45, -1), style=wx.TE_CENTER
        )
        self.rand_input.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        self.rand_input.Bind(wx.EVT_TEXT, self._on_random)

        btn_rnd = wx.Button(bottom_bar, label="随机")
        btn_rnd.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )
        btn_rnd.SetBackgroundColour(COLOR_DIVIDER)
        btn_rnd.SetForegroundColour(COLOR_TEXT)
        btn_rnd.Bind(wx.EVT_BUTTON, self._on_random)

        self.btn_preview = wx.Button(bottom_bar, label="预览")
        self.btn_preview.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                faceName="Microsoft YaHei",
            )
        )
        self.btn_preview.SetBackgroundColour(COLOR_PRIMARY)
        self.btn_preview.SetForegroundColour(wx.WHITE)
        self.btn_preview.Bind(wx.EVT_BUTTON, self._on_preview)

        self.btn_generate = wx.Button(bottom_bar, label="生成PDF")
        self.btn_generate.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                faceName="Microsoft YaHei",
            )
        )
        self.btn_generate.SetBackgroundColour(COLOR_ACCENT)
        self.btn_generate.SetForegroundColour(wx.WHITE)
        self.btn_generate.Bind(wx.EVT_BUTTON, self._on_generate)

        batch_lbl = wx.StaticText(bottom_bar, label="批量:")
        batch_lbl.SetFont(
            wx.Font(
                11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
            )
        )

        self.batch_input = wx.TextCtrl(
            bottom_bar, value="10", size=(45, -1), style=wx.TE_CENTER
        )
        self.batch_input.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="Microsoft YaHei",
            )
        )

        self.btn_batch = wx.Button(bottom_bar, label="批量生成PDF")
        self.btn_batch.SetFont(
            wx.Font(
                11,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                faceName="Microsoft Yahei",
            )
        )
        self.btn_batch.SetBackgroundColour(COLOR_VIOLET)
        self.btn_batch.SetForegroundColour(wx.WHITE)
        self.btn_batch.Bind(wx.EVT_BUTTON, self._on_batch_save)

        # 按钮按不同比例分配窗口宽度
        bottom_sizer.Add(
            btn_sel, proportion=1, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=4
        )
        bottom_sizer.Add(
            btn_clr, proportion=1, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=4
        )
        bottom_sizer.Add(
            self.rand_input,
            proportion=0,
            flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=2,
        )
        bottom_sizer.Add(
            btn_rnd, proportion=1, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=4
        )
        bottom_sizer.Add(
            self.btn_preview,
            proportion=2,
            flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=4,
        )
        bottom_sizer.Add(
            self.btn_generate,
            proportion=2,
            flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=4,
        )
        bottom_sizer.Add(
            batch_lbl, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=4
        )
        bottom_sizer.Add(
            self.batch_input,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            border=2,
        )
        bottom_sizer.Add(self.btn_batch, proportion=2, flag=wx.ALIGN_CENTER_VERTICAL)

        bottom_bar.SetSizer(bottom_sizer)
        main_sizer.Add(bottom_bar, flag=wx.EXPAND | wx.ALL, border=4)

        # 日志区域（白色背景、宋体、5行高度）
        log_panel = wx.Panel(self, style=wx.BORDER_NONE)
        log_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        log_sizer = wx.BoxSizer(wx.VERTICAL)

        log_title = wx.StaticText(log_panel, label="运行日志")
        log_title.SetFont(
            wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        log_title.SetForegroundColour(COLOR_TEXT)
        log_sizer.Add(log_title, flag=wx.LEFT | wx.TOP, border=8)

        self.log_text = wx.TextCtrl(
            log_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )
        self.log_text.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.log_text.SetForegroundColour(COLOR_TEXT)
        self.log_text.SetFont(
            wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                faceName="SimSun",
            )
        )
        log_sizer.Add(
            self.log_text,
            proportion=1,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            border=4,
        )

        log_panel.SetSizer(log_sizer)
        log_panel.SetMinSize((-1, 100))
        main_sizer.Add(log_panel, flag=wx.EXPAND | wx.BOTTOM, border=4)

        self.SetSizer(main_sizer)

    def _log(self, msg):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.AppendText(f"[{timestamp}] {msg}\n")

    def _get_exe_dir(self):
        """获取exe所在目录或脚本所在目录"""
        if getattr(sys, "frozen", False):
            # 打包后的exe
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发环境
            return os.path.dirname(os.path.abspath(__file__))

    def _get_selected(self):
        return [
            (row.type_code, row.count) for row in self.all_rows if row.is_selected()
        ]

    def _on_select_all(self, e):
        for row in self.all_rows:
            row.set_selected(True)

    def _on_clear_all(self, e):
        for row in self.all_rows:
            row.set_selected(False)

    def _on_random(self, e):
        try:
            num = int(self.rand_input.GetValue())
            num = max(1, min(num, len(self.all_rows)))
        except Exception:
            num = 5
        for row in self.all_rows:
            row.set_selected(False)
        items = self.all_rows[:]
        random.shuffle(items)
        for row in items[:num]:
            row.set_selected(True)

    def _on_preview(self, e):
        selected = self._get_selected()
        if not selected:
            wx.MessageBox("请至少选择一个题型", "提示", wx.OK | wx.ICON_WARNING)
            return
        self._log(f"预览: 已选择 {len(selected)} 个题型")
        questions_data = get_questions_data(selected)
        try:
            self._log("正在生成PDF...")
            pdf_bytes = PDFGenerator().get_pdf_bytes(questions_data)
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp_path = tmp.name
            tmp.close()
            with open(tmp_path, "wb") as f:
                f.write(pdf_bytes)
            self._log(f"PDF已生成: {tmp_path}")
            webbrowser.open_new_tab("file:///" + tmp_path)
        except Exception as ex:
            self._log(f"预览失败: {str(ex)}")
            wx.MessageBox(("打开失败：" + str(ex)), "错误", wx.OK | wx.ICON_ERROR)

    def _on_generate(self, e):
        selected = self._get_selected()
        if not selected:
            wx.MessageBox("请至少选择一个题型", "提示", wx.OK | wx.ICON_WARNING)
            return
        self._log(f"生成试卷: 已选择 {len(selected)} 个题型")
        questions_data = get_questions_data(selected)
        wildcard = "PDF文件 (*.pdf)|*.pdf"
        dlg = wx.FileDialog(
            self,
            "保存试卷",
            wildcard=wildcard,
            defaultFile=generate_default_filename(),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                self._log(f"正在保存到: {path}")
                pdf_bytes = PDFGenerator().get_pdf_bytes(questions_data)
                with open(path, "wb") as f:
                    f.write(pdf_bytes)
                self._log(f"保存成功: {path}")
            except Exception as ex:
                self._log(f"保存失败: {str(ex)}")
                wx.MessageBox(("导出失败：" + str(ex)), "错误", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def _on_batch_save(self, e):
        try:
            count = int(self.batch_input.GetValue())
            count = max(1, min(count, 200))
        except Exception:
            wx.MessageBox("请输入有效的数字（1~200）", "提示", wx.OK | wx.ICON_WARNING)
            return
        selected = self._get_selected()
        if not selected:
            wx.MessageBox("请至少选择一个题型", "提示", wx.OK | wx.ICON_WARNING)
            return
        self._log(f"批量保存: 开始生成 {count} 份试卷")
        questions_data = get_questions_data(selected)

        # 使用exe所在目录的output文件夹
        exe_dir = self._get_exe_dir()
        out_dir = os.path.join(exe_dir, "output")
        os.makedirs(out_dir, exist_ok=True)
        self._log(f"输出目录: {out_dir}")

        ok = 0
        for i in range(count):
            try:
                data = PDFGenerator().get_pdf_bytes(get_questions_data(selected))
                fname = "练习_%03d_%s.pdf" % (i + 1, datetime.now().strftime("%H%M%S"))
                with open(os.path.join(out_dir, fname), "wb") as f:
                    f.write(data)
                ok += 1
                if (i + 1) % 10 == 0 or i == count - 1:
                    self._log(f"进度: {ok}/{count}")
            except Exception:
                pass

        result_msg = (
            f"批量保存完成：\n成功生成 {ok}/{count} 个 PDF 文件\n保存路径：{out_dir}"
        )
        self._log(f"批量保存完成: {ok}/{count} 份")


# ============ 应用入口 ============
class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = App()
    app.MainLoop()
