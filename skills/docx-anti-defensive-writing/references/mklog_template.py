# -*- coding: utf-8 -*-
"""
mklog_template.py — 生成《防御性写作修改清单》（逐处前后对照，便于自查与留痕）

用法：
    python mklog_template.py <改后的.docx> <改前的.docx或备份文件> [输出.md]

输出内容：
    · 段落总数、实际改动段数
    · 逐段前后对照（只列有差异的段）
    · 一句总评：本次改动的性质分布

为什么需要它：改完一定要能回答「我到底改了什么」。没有清单的批量改写，
过两周自己都说不清哪些句子被动过。
"""

import os
import sys

try:
    import docx
except ImportError:
    sys.exit("缺少 python-docx。请先安装：pip install python-docx")


def read_paras(path):
    return [p.text.strip() for p in docx.Document(path).paragraphs]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    new_path, old_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None

    new_paras = read_paras(new_path)
    old_paras = read_paras(old_path)

    lines = ["# 防御性写作修改清单", ""]
    lines.append(f"- 改后文件：`{os.path.basename(new_path)}`")
    lines.append(f"- 改前文件：`{os.path.basename(old_path)}`")
    lines.append(f"- 改前段数：{len(old_paras)}　改后段数：{len(new_paras)}")
    lines.append("")

    if len(old_paras) != len(new_paras):
        lines.append(
            "> ⚠ 前后段数不一致。这通常意味着误删或误合并了段落，"
            "请对照原文核查后再采用本清单。"
        )
        lines.append("")

    changed = []
    for i in range(min(len(old_paras), len(new_paras))):
        o, n = old_paras[i], new_paras[i]
        if o and o != n:
            changed.append(i)

    lines.append(f"## 改动统计\n\n共 {len(changed)} 段有改动。\n")

    if not changed:
        lines.append("未检出文本差异。\n")
    else:
        lines.append("## 逐处对照\n")
        lines.append("| 段号 | 改前 | 改后 |")
        lines.append("|---|---|---|")
        for i in changed:
            o = old_paras[i].replace("|", "\\|")
            n = new_paras[i].replace("|", "\\|")
            lines.append(f"| {i} | {o} | {n} |")
        lines.append("")

    lines.append("## 自查要点\n")
    lines.append("- [ ] 删掉的是防御动作（自证克制、假想辩解、重复免责），不是真实的科学限制")
    lines.append("- [ ] 限制条件改成正面范围陈述，没有消失")
    lines.append("- [ ] 对冲词换成了具体数值或区间")
    lines.append("- [ ] 参考文献、表格、图注、章节编号未被改动")
    lines.append("- [ ] 改过的段落抽读 3–5 处，语气自然")

    text = "\n".join(lines) + "\n"

    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"已写出 → {out_path}")
    else:
        print(text)


if __name__ == "__main__":
    main()
