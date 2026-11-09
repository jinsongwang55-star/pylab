"""极简 Markdown 渲染器，只覆盖课程内容用到的语法子集。

支持: 标题(#~####)、段落、围栏代码块、行内代码、粗体、无序/有序列表、
引用块、表格、分隔线。原始 HTML 会被转义。
"""

from __future__ import annotations

import html
import re

FENCE = "```"
HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
ULIST = re.compile(r"^[-*]\s+(.*)$")
OLIST = re.compile(r"^\d+\.\s+(.*)$")
QUOTE = re.compile(r"^>\s?(.*)$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def _render_table(header: str, separator: str, rows: list[str]) -> str:
    heads = _cells(header)
    aligns = []
    for cell in _cells(separator):
        left, right = cell.startswith(":"), cell.endswith(":")
        aligns.append("center" if left and right else "right" if right else "left")
    out = ["<table><thead><tr>"]
    for index, cell in enumerate(heads):
        align = aligns[index] if index < len(aligns) else "left"
        out.append(f'<th style="text-align:{align}">{_inline(cell)}</th>')
    out.append("</tr></thead><tbody>")
    for row in rows:
        values = _cells(row)
        out.append("<tr>")
        for index in range(len(heads)):
            cell = values[index] if index < len(values) else ""
            align = aligns[index] if index < len(aligns) else "left"
            out.append(f'<td style="text-align:{align}">{_inline(cell)}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _starts_block(line: str) -> bool:
    return bool(
        line.startswith(FENCE)
        or HEADING.match(line)
        or ULIST.match(line)
        or OLIST.match(line)
        or QUOTE.match(line)
        or line.strip() == "---"
        or line.lstrip().startswith("|")
    )


def render(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i, total = 0, len(lines)

    while i < total:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.startswith(FENCE):
            lang = line[len(FENCE):].strip()
            i += 1
            buffer: list[str] = []
            while i < total and not lines[i].startswith(FENCE):
                buffer.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(buffer))}</code></pre>")
            continue

        match = HEADING.match(line)
        if match:
            level = len(match.group(1))
            out.append(f"<h{level}>{_inline(match.group(2))}</h{level}>")
            i += 1
            continue

        if line.strip() == "---":
            out.append("<hr>")
            i += 1
            continue

        if line.lstrip().startswith("|") and i + 1 < total and TABLE_SEP.match(lines[i + 1]):
            header, separator = line, lines[i + 1]
            i += 2
            rows: list[str] = []
            while i < total and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(_render_table(header, separator, rows))
            continue

        if ULIST.match(line):
            items = []
            while i < total and ULIST.match(lines[i]):
                items.append(f"<li>{_inline(ULIST.match(lines[i]).group(1))}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        if OLIST.match(line):
            items = []
            while i < total and OLIST.match(lines[i]):
                items.append(f"<li>{_inline(OLIST.match(lines[i]).group(1))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        if QUOTE.match(line):
            buffer = []
            while i < total and QUOTE.match(lines[i]):
                buffer.append(_inline(QUOTE.match(lines[i]).group(1)))
                i += 1
            out.append("<blockquote>" + "<br>".join(buffer) + "</blockquote>")
            continue

        buffer = []
        while i < total and lines[i].strip() and not _starts_block(lines[i]):
            buffer.append(_inline(lines[i]))
            i += 1
        if not buffer:
            # 形似块起始但未被任何规则消费（例如缺少分隔行的表格行），
            # 按普通段落吃掉，避免原地死循环
            buffer.append(_inline(line))
            i += 1
        out.append("<p>" + "<br>".join(buffer) + "</p>")

    return "\n".join(out)
