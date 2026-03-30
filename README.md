# 三年级数学练习题生成器

一款面向小学三年级学生的数学练习题生成器，支持随机出题和 PDF 导出。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![wxPython](https://img.shields.io/badge/wxPython-4.0+-green.svg)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-orange.svg)

## 功能特点

- **17 种题型**，覆盖三年级数学核心知识点
- **随机组卷**，每次生成题目不同
- **实时预览**，直接查看生成的试卷
- **PDF 导出**，支持中文显示
- **批量生成**，可一次生成多份不同的练习卷
- **跨平台**，支持 Windows、macOS、Linux

## 题型分类

| 分类 | 题型 |
|------|------|
| 竖式计算 | 竖式加减法、竖式乘法、竖式除法 |
| 混合运算 | 加减乘除混合、带括号混合运算、求未知数△ |
| 单位换算 | 人民币换算、时间换算、长度换算、质量换算 |
| 图形与测量 | 周长计算、面积计算、面积单位换算 |
| 概念题 | 找规律填数、倍的认识、小数加减法、方向与位置 |

## 运行方式

### 直接运行 EXE（Windows）

下载 `dist/三年级数学练习.exe`，直接双击运行，无需安装任何依赖。

### 源码运行

```bash
pip install wxPython reportlab
python main.py
```

## 项目结构

```
mathapp/
├── main.py                  # 程序入口（wxPython GUI）
├── question_generator.py    # 题目生成逻辑
├── pdf_generator.py         # PDF 生成（基于 ReportLab）
├── icon.png                 # 应用图标
└── README.md
```

## 使用说明

1. **选择题型**：勾选左侧复选框，每个题型可设置题目数量（1~20）
2. **快捷操作**：
   - 全选 / 清空：快速选中或取消所有题型
   - 随机：随机选择 N 个题型（可设置 N）
3. **生成试卷**：
   - **预览**：生成临时 PDF 并直接打开查看
   - **生成练习题**：选择保存路径，导出 PDF 文件
   - **批量保存**：输入数量，在 `output/` 文件夹生成多份不同试卷

## License

MIT
