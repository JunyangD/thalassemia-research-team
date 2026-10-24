---
name: docx-anti-defensive-writing
description: 把「反防御性写作」原则落到 .docx 论文正文上并原地改写——提取段落、逐段判定、定点替换、保留格式、留清单与备份。当需要对 Word 论文/报告做「去防御腔、去自证克制、去假想辩解」的批量改写时使用。触发词：防御性写作、anti-defensive-writing、论文去防御腔、docx 正文改写、把 anti-defensive-writing 扫一遍。
---

# 给 .docx 正文做反防御性写作改写

把 `anti-defensive-writing`（如 `~/.workbuddy/skills/anti-defensive-writing/`）的**判定原则**，
落到一份 **Word 正文**上，产出「改后的 docx + 备份 + 逐处修改清单」。

## 核心原则（改写尺度）

论文是**学术发布会**，不是项目日志、不是自我审查报告。所以：

- **只删防御动作，不删科学限制。** 口径限制、方法学限制、样本量边界、功效不足的声明 —— **一律保留**；
  要删的是**重复**、**自证克制**（"我们不宣称…"、"须特别声明…"）、**预防假想误解**（替审稿人先攻击自己）。
- **把限制改成正面范围陈述。** "本研究存在多方面局限" → "本研究的适用范围受以下边界限定"；
  "正确表述为 X，不写作 Y" → "记作 X"。
- **把对冲词换成精确值。** "多数" → 给出数；"可能" → 给出区间或删掉。
- **不整段重写，不动参考文献 / 表格 / 图注占位 / 章节编号。**
- **段落总数必须不变。** 改完先核对段数 == 改前段数。

## 流程

### 0. 备份（先做，别省）
```
cp -f "<正文>.docx" "<正文>.docx.bak.<YYYYMMDD>_<HHMM>_ADW前"
```

### 1. 提取正文为带行号的 raw.md
用 python-docx 遍历 `doc.paragraphs`，打印 `序号 + repr(文本)`，落到 `<短名>_raw.md`。
**这一步产出的序号即后续 E 表的键。**

### 2. 逐段判定
按 anti-defensive-writing 的检测清单过一遍，重点抓：
- 段首就摆限制 / 以「须声明」「须注意」「需要限定的是」起句
- 反复出现「不宣称」「不等价于」「不能写作 X」的否定式自证
- 高影响位置（摘要、小节首句、结论首句）堆 caveat
- 「不是 X 而是 Y」句式、冗余的 然而/尽管如此/虽然

### 3. 写 E 表（**关键：行号口径**）
在 `references/fix_template.py` 基础上改，写 `E["<短名>"] = [(行号, 原串, 新串), ...]`：
- 行号用 **1-based**（就是第 1 步打印出来的序号）；
- 原串必须是**文档里的精确子串**（含全角标点、空格）；
- 新串填 `""` 表示整句/整段删除该子串；
- 同一段可有多条，按 order 依次命中。

### 4. 跑改写
引擎逻辑（见模板）：
```python
paras = doc.paragraphs
for idx0, old, new in E[key]:
    p = paras[idx0 - 1]              # ← 1-based → 0-based，漏了这一步会全部 NOT_FOUND
    txt = "".join(r.text for r in p.runs)
    if old not in txt: print("NOT_FOUND", idx0, old[:30]); continue
    txt = txt.replace(old, new, 1)
    p.runs[0].text = txt             # 只写 runs[0]，其余 runs 清空 ⇒ 段落格式保留
    for r in p.runs[1:]: r.text = ""
```
跑完打印 `applied / NOT_FOUND` 计数；**有 NOT_FOUND 就回滚 docx 重来，别带病保存**。

### 5. 生成修改清单
用 `references/mklog_template.py`，配一张「段落号 → (命中规则, 说明)」的分类字典，
产出《防御性写作修改清单_<日期>.md》：改前/改后对照 + 依据。

### 6. 复核
- 段数不变（`len(doc.paragraphs)` 与改前一致）；
- 重开 docx 抽查 3–5 处；
- 清单里每一处都能在 diff 里找到对应。

## 踩过的坑（务必先看）

| 坑 | 现象 | 处置 |
|---|---|---|
| **行号差一位** | 首跑 `applied: 0`，全 NOT_FOUND | `Read`/打印是 **1-based**，`paragraphs` 是 **0-based** → `idx = 行号 - 1` |
| **MSYS 路径** | `Package not found` | 本机 python 是 Windows 原生，**不认 `/d/...`**，必须用 `r"D:\..."` |
| **跨行段落** | 某处替换落到相邻段 | 在 raw.md 里定位段落边界，必要时用 `paras[i]` 单独补刀 |
| **直接改 run** | 字体/字号丢失 | 只改 `runs[0].text`，其余 runs 置空 |
| **多备份** | 目录里两份同名 bak | 只留一份，另一份删掉归一 |

## 交付物
1. `<正文>.docx`（已改）
2. `<正文>.docx.bak.<时间戳>_ADW前`（备份）
3. `防御性写作修改清单_<日期>.md`（逐处对照 + 依据）
