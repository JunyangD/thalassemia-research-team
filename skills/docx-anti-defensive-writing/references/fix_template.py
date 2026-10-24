# -*- coding: utf-8 -*-
"""
fix_template.py — 对 .docx 正文做定点改写（子串级替换，尽量保留格式）

用途：把「防御性写作」判定结果落到 Word 正文上——不是重写全文，而是逐处把
防御动作换成平静陈述，其余一个字不动。

用法：
    python fix_template.py <要改的.docx>

    先只导出段落看结构（不改）：
    python fix_template.py <要改的.docx> --list

流程：
    1. 备份原文件为 <原名>.docx.bak.<时间戳>_ADW前
    2. 按 E 表逐条定位并替换
    3. 核对段落总数未变
    4. 打印命中/未命中清单

E 表写法：
    (段落序号, 原文片段, 替换文本)
    · 段落序号来自 --list 的输出（0 起算），不是 Word 里的可见行号。
    · 原文片段必须是该段中能唯一匹配的子串；匹配不到会记为「未命中」并跳过，
      绝不猜着改。
    · 替换文本写 "" 表示删除该片段。

铁律：
    · 先备份，备份失败就停。
    · 段落总数必须不变。
    · 不动参考文献、表格、图注占位、章节编号。
    · 只删防御动作，不删真实的科学限制。
"""

import json
import os
import shutil
import sys
from datetime import datetime

try:
    import docx
except ImportError:
    sys.exit("缺少 python-docx。请先安装：pip install python-docx")


# ============ 改写表：按需要填写 ============
# 示例（全部注释掉，用时自己打开并改成实际内容）：
#   (12, "待检路径", "路径"),
#   (25, "须特别声明：本研究未预注册。", ""),
E = [
]


def list_paragraphs(doc_path):
    d = docx.Document(doc_path)
    for i, p in enumerate(d.paragraphs):
        text = p.text.strip()
        if text:
            print(f"[{i:04d}] {text[:160]}")
    print(f"\n共 {len(d.paragraphs)} 段（含空段）")


def replace_in_paragraph(p, old, new):
    """在单段内做子串替换。返回 True 表示改成功。

    优先在单个 run 内替换（格式完全保留）；跨 run 时把新文本写入首个涉及的 run，
    并清空其余涉及的 run，仅影响被替换片段本身的格式。
    """
    if old not in p.text:
        return False

    # 单 run 命中：最优路径
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new, 1)
            return True

    # 跨 run：拼出全文定位，再把整段按新全文重建到首个 run
    full = "".join(r.text for r in p.runs)
    idx = full.find(old)
    if idx < 0:
        return False
    new_full = full[:idx] + new + full[idx + len(old):]

    if not p.runs:
        return False
    p.runs[0].text = new_full
    for r in p.runs[1:]:
        r.text = ""
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args:
        sys.exit(__doc__)

    doc_path = args[0]
    if not os.path.exists(doc_path):
        sys.exit(f"文件不存在：{doc_path}")

    if "--list" in flags:
        list_paragraphs(doc_path)
        return

    edits = E
    if "--edits" in flags:
        ep = sys.argv[sys.argv.index("--edits") + 1]
        with open(ep, "r", encoding="utf-8") as f:
            edits = [tuple(x) for x in json.load(f)]

    if not edits:
        sys.exit("改写表是空的。先跑 --list 看段落，再填 E 表或用 --edits 指定 JSON。")

    # 1. 备份
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(doc_path)
    bak = f"{base}{ext}.bak.{stamp}_ADW前"
    try:
        shutil.copy2(doc_path, bak)
    except Exception as e:
        sys.exit(f"备份失败，已中止（未改动原文件）：{e}")
    print(f"已备份 → {bak}")

    # 2. 改写
    d = docx.Document(doc_path)
    before = len(d.paragraphs)
    hits, misses = [], []

    for item in edits:
        if len(item) != 3:
            misses.append((item, "格式错误，应为 (段落序号, 原串, 新串)"))
            continue
        idx, old, new = item
        if not isinstance(idx, int) or idx < 0 or idx >= len(d.paragraphs):
            misses.append((item, f"段落序号越界（共 {len(d.paragraphs)} 段）"))
            continue
        p = d.paragraphs[idx]
        if replace_in_paragraph(p, old, new):
            hits.append((idx, old, new))
        else:
            misses.append((item, "该段内找不到原文片段"))

    # 3. 段落数核对
    if len(d.paragraphs) != before:
        sys.exit(
            f"段落数发生变化（{before} → {len(d.paragraphs)}），已中止且未保存。"
            f"原文备份在 {bak}"
        )

    # 4. 保存
    d.save(doc_path)
    print(f"已保存 → {doc_path}")
    print(f"命中 {len(hits)} 处，未命中 {len(misses)} 处")

    if misses:
        print("\n未命中清单（需人工处理，不要忽略）：")
        for item, why in misses:
            print(f"  · 第 {item[0] if isinstance(item, (tuple, list)) and item else '?'} 段：{why}")
            print(f"    原串：{item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else ''}")

    print("\n下一步：抽 3–5 处改过的段落读一遍，确认语气自然、科学限制没被删掉。")


if __name__ == "__main__":
    main()
