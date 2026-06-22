"""Word 报告生成：从原 methods.py 的 docx 读写移植。

加载模板 → （可选）按字段填充表格 → 保存到输出目录，返回文件路径。
"""
from __future__ import annotations

import os

from docx import Document

from config import REPORT_TEMPLATE_DIR

DEFAULT_TEMPLATE = "报告2.docx"


def _fill_fields(doc: Document, fields: dict | None) -> None:
    """按 {表格首列关键字: 填入第二列的值} 填充模板表格。fields 为空则不改。"""
    if not fields:
        return
    for table in doc.tables:
        for row in table.rows:
            if len(row.cells) < 2:
                continue
            key_text = row.cells[0].text.strip()
            for key, value in fields.items():
                if key and key in key_text:
                    row.cells[1].text = str(value)


def generate_report(save_path: str, fields: dict | None = None,
                    template: str = DEFAULT_TEMPLATE) -> str:
    """生成报告 docx，返回保存路径。"""
    template_path = REPORT_TEMPLATE_DIR / template
    if not template_path.exists():
        raise FileNotFoundError(f"报告模板不存在：{template_path}")

    doc = Document(str(template_path))
    _fill_fields(doc, fields)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    doc.save(save_path)
    return save_path
