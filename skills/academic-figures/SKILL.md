---
name: academic-figures
description: >-
  论文配图一键生成：一条命令从 JSON/CSV/Excel 生成顶刊级图表。22 种图表
  （柱状/分组柱/散点/热力图/森林图/KM 生存曲线/ROC/小提琴/箱线/组合图/
  PRISMA 流程图/漏斗/BA 一致性/PCA/韦恩 2~4 集合/聚类热图/双轴/Cox 多因素
  回归森林图），9 套配色（含色盲安全 Okabe-Ito 与 NEJM/Lancet/Science 期刊
  色板），9 种期刊投稿预设，YAML 流水线一条命令出全套论文图，一次渲染多格式
  导出（TIFF/PNG/PDF），支持 Python 编程调用与 --wizard 选图向导，渲染看门狗
  +自动降级重试，PDF 重叠+字号双门禁，600dpi 输出。纯本地运行，数据不出机，
  中文零配置。
when_to_use: >-
  用户要画图/出图/生成图表时使用：柱状图、散点图、热力图、森林图、KM 生存
  曲线、ROC 曲线、小提琴图、箱线图、组合图、流程图、PRISMA 系统综述、Meta
  漏斗图、韦恩/欧拉图、PCA 得分图、Bland-Altman 一致性；需要论文/期刊/SCI
  配图导出（600dpi、色盲安全）；或把数据文件转成学术图表。
---

<!--
═══════════ 元数据归档（2026-09-13 frontmatter 规范化）═══════════
ZCode 技能自动发现只识别 frontmatter 白名单键：
  name / description / when_to_use / license / metadata
且 description 超过 1024 字符会被静默丢弃（本技能 v2.x 自动发现
失效根因）。以下键自 frontmatter 移出归档，信息不丢失：
  version: 3.2.0
  date: 2026-09-17
  author: docsor1212
  lang: zh
  metadata: {clawdbot: {emoji: "📊", category: visualization}}
  requires: {python: ">=3.8", pip: [matplotlib, numpy, pymupdf, scipy]}
运行依赖见 requirements.txt 与 scripts/setup_env.py；版本史见文末版本历史。
═════════════════════════════════════════════════════════════════
-->

# Academic Figures — 论文配图一键生成工具

> 📊 **22种图表 · 9套配色（含色盲安全+期刊色板） · 零配置中文 · 600dpi出版级输出 · PDF/TIFF/SVG全支持 · 渲染看门狗+中文诊断**
> 纯本地运行 · 数据不出本机 · Python一条命令搞定 · 内置校验+验证门禁

> ⚡ **三条最常用边界**：投稿 PDF 加 `--verify`（仅 PDF 生效）；`--journal` 会锁定图宽（`--width` 被忽略）；cluster_heatmap >3000 行自动降采样到 2000 行。

**一条命令，输出即验证：**
```bash
python3 scripts/gen_figure.py -t bar -d data.json -o fig.pdf --theme okabe-ito --verify
# 退出码含义见下方「数据校验与退出码」；--verify 检出重叠 = exit 2（修复机制，不要交付）
```

## ✨ 核心亮点

| 特性 | 说明 |
|------|------|
| 📊 **22种图表** | 见下方「图表类型」全表；v2.7 加 Cox 多因素回归森林图，v2.8 加 4 集合椭圆韦恩 |
| 🎨 **9套配色** | **Okabe-Ito色盲安全**（Nature Methods 金标准）、GLM 素雅莫兰迪、NEJM/Lancet/Science 期刊色板等 |
| 📐 **期刊预设** | `--journal nature/lancet/nejm/science/cma/cn-core`：官方栏宽、字号、字体族、600dpi 一键应用 |
| 🧭 **上手向导** | `--wizard` 四问生成完整命令（非交互环境自动打印选图决策树） |
| 🛡️ **数据校验** | 18种类型/别名全覆盖的结构校验；致命错误→exit 1 不落盘，警告→继续运行 |
| ⏱️ **渲染看门狗** | 超时强制中断并给中文建议（exit 5）；内存不足自动降级重试（v2.8） |
| ✅ **验证门禁** | `--verify` 像素级重叠检查（exit 2）；`audit_pdf.py` 字号门禁（期刊最小字号） |
| 🇨🇳 **中文零配置** | 自动检测中文字体（含字典键、补充平面），彻底告别乱码 |
| 📈 **统计标注** | 误差棒、显著性标记(p值星号)、趋势线、置信区间、Cox PH 假设检验提示 |
| 🧩 **组合图** | 多面板A+B+C，每个面板可放任意图表类型，期刊figure标准布局 |
| 📄 **多格式输出** | PNG 600dpi + SVG + PDF + TIFF + EPS；`--multi-format` 一次多格式 |

## 图表类型

| 类别 | 类型 | 命令 | 核心功能 |
|------|------|------|---------|
| 比较 | 柱状图 | `-t bar` | 分组柱状图、误差棒、显著性标记、斜纹填充 |
| 比较 | 水平柱状图 | `-t hbar` | 横向柱状图、比率标注（"4.96x"） |
| 构成 | 堆叠柱状图 | `-t stacked_bar` | 构成比、百分比标签、总计标注 |
| 分布 | 箱线图 | `-t box` | 箱线图+抖动散点 |
| 分布 | 小提琴图 | `-t violin` | 密度估计、内置均值/中位线 |
| 趋势 | 散点图 | `-t scatter` | 趋势线、相关系数、分组着色、点标签 |
| 趋势 | 折线图 | `-t line` | 多系列、误差带、标记点 |
| 趋势 | 双Y轴图 | `-t dual_axis` | 左右Y轴、实线+虚线、合并图例 |
| 矩阵 | 热力图 | `-t heatmap` | 单元格标注、自定义色阶、colorbar |
| 矩阵 | 聚类热图 | `-t cluster_heatmap` | 层次聚类重排、`--downsample` 降采样出口 |
| 统计推断 | 森林图 | `-t forest` | CI横线、权重气泡、总效应菱形、I²、事件数；`--stats cox` 多因素回归 |
| 生存分析 | KM生存曲线 | `-t km` | 阶梯函数、删失标记、Log-rank检验、风险表、中位生存 |
| 诊断试验 | ROC曲线 | `-t roc` | AUC、95%CI、最优截断点、DeLong 多模型对比 |
| 集合 | 韦恩图 | `-t venn` | 2~4 集合（4 集合为椭圆布局）；`--area` 面积比例 Euler |
| 组合 | **组合图** | `-t composite` | 多面板A+B+C，每面板任意图表类型（⚠面板内不可嵌套 composite），期刊figure布局 |
| 流程 | **流程图** | `-t diagram` | 架构/流程块、箭头、分组标注，CONSORT式研究设计 |
| 系统综述 | **PRISMA流程图** | `-t prisma` | PRISMA 2020 系统综述流程图；数字自洽自动校验（对不上拒绝出图），`lang=zh` 中文标准版 |

按「类别」列速览；上手路径见 `references/quickstart.md`，完整命令速查见 `references/cheatsheet.md`。

## 选图决策树（精简版；完整版+上手四步见 references/quickstart.md）

```text
分组比较 → bar/box/violin（配对→paired）｜均值±误差棒 → bar（JSON errors）
两列相关 → scatter｜时间-事件 → km / forest --stats cox｜诊断 → roc（--compare）
集合交并 → venn（--area）｜数值矩阵 → heatmap / cluster_heatmap｜多变量分类 → pca
Meta 汇总 → forest（--egger）｜一致性 → bland_altman｜流程 → diagram/prisma
多面板 → composite
```

拿不准就跑 `--suggest -d 数据文件`（自动分析并推荐），或 `--wizard`（问答式生成命令）。
**首次使用？** 完整决策树、上手四步、Python 内调用与常见第一坑见
**`references/quickstart.md`**（独立快速入门指南）。

## 快速开始

```bash
# 0️⃣ 首次使用：一键环境准备（装依赖/检测中文字体/清理字体缓存/自检）
python3 scripts/setup_env.py

# 0️⃣ 上手三件套：选图向导 / 交互演示 / 某图型用法
python3 scripts/gen_figure.py --wizard
python3 scripts/gen_figure.py --quick -d 数据文件   # v3.1 一键出图：自动选型直接渲染
python3 scripts/gen_figure.py --demo --cjk
python3 scripts/gen_figure.py --explain bar
# 0️⃣ Python 内调用引擎：见 references/python-api.md（subprocess 推荐；import 嵌入需自行 Agg）

# 1️⃣ 柱状图（默认 glm 素雅配色）
python3 scripts/gen_figure.py -t bar -d data.json -o figure.png \
  --title "图2 主标题 / Subtitle" --ylabel "准确率 Accuracy (%)"

# Meta分析森林图（PDF输出）
python3 scripts/gen_figure.py -t forest -d forest.json -o forest.pdf --theme okabe-ito

# v2.7：原始逐例生存数据 → 自动多因素 Cox 回归 → HR 森林图（含 PH 假设检验）
python3 scripts/gen_figure.py -t forest --data patient.csv --stats cox \
  --cox-time time --cox-event event --cox-cols "age,sex,treat"

# Kaplan-Meier生存曲线 + Log-rank检验
python3 scripts/gen_figure.py -t km -d survival.json -o km.png --theme okabe-ito \
  --title "图3 Kaplan-Meier生存曲线" --xlabel "时间 (月)" --ylabel "生存概率"

# ROC曲线 + AUC
python3 scripts/gen_figure.py -t roc -d roc.json -o roc.png --theme okabe-ito

# v2.8：4 集合椭圆韦恩图（数据格式见 templates/venn.json）
python3 scripts/gen_figure.py -t venn -d venn.json -o venn4.png

# Nature双栏投稿：栏宽183mm、7pt Helvetica、最小字号5pt
python3 scripts/gen_figure.py -t bar -d data.json -o nat.pdf --journal nature --column double
python3 scripts/audit_pdf.py nat.pdf --min-size 5          # 字号门禁（nature=5pt）

# 多面板组合图（Panel A+B+C，期刊figure布局）
python3 scripts/gen_figure.py -t composite -d composite.json -o figure4.png --theme okabe-ito

# 热力图（自定义色阶 + 中文）
python3 scripts/gen_figure.py -t heatmap -d data.json -o heatmap.png --cjk \
  --cmap RdBu_r --vmin -20 --vmax 45

# v2.7：画幅比例预设（16:9 演示 / 9:16 手机竖版）；v2.8：大数据聚类热图降采样
python3 scripts/gen_figure.py -t bar --data d.json --size 16:9
python3 scripts/gen_figure.py -t cluster_heatmap --data big.json --downsample 2000 --timeout 600
```

## ⚠️ 边界与限制（先看这个，免试错）

**数据量**：cluster_heatmap >3000 行自动等距采样到 2000 行并显著告知（也可 `--downsample N` 自定行数）；pca ≤200 特征列；venn 2~4 集合（4 集合为椭圆布局）；paired/bland_altman 需等长；km 无硬上限（5 万行实测 3s）。
**参数兼容**：`--stats` 仅 box/violin（`cox` 仅 forest）；`--compare` 仅 roc；`--egger` 仅 funnel；`--hatch` 仅 bar 系；`--sheet` 仅 xlsx；`--journal` 会锁定宽度（`--width` 被覆盖）；`--area` 仅 venn。`--style glm-hatch` 为主题级斜纹风格（区别于仅 bar 系的 `--hatch`）。
**超时**：默认渲染看门狗按图型与数据量自适应（30~1800s）；`--timeout N` 调整，`--timeout 0` 禁用。

完整矩阵见 `references/limits.md`（超限一律中文报错+修正建议，不出半成品图）。
常见问题速答见 `references/faq.md`（安装/数据/参数/投稿/报错速查 高频 Q&A）。
**参数组合交互**（`--journal` 锁宽度、PDF 重叠检测需显式 `--verify`、默认 DPI 等）
与**运行环境边界**（无显示环境/中文字体）完整表 → `references/limits.md` §六、§七。

## 配色方案

**默认配色 = `glm`**（素雅莫兰迪风，色盲安全）。`--list-themes` 终端看色卡，`--theme-swatch glm -o swatch.png` 出色板图。

| 方案 | 说明 | 色盲安全 |
|------|------|---------|
| `glm` ⭐默认 | 素雅莫兰迪（钢蓝/暖黄/鼠尾草绿/灰紫/珊瑚） | ✅ 是 |
| `okabe-ito` | Nature Methods金标准（Wong 2011）— 期刊投稿首选 | ✅ 是 |
| `cool` | 素雅冷色调（藏青/海蓝/青灰/石板色） | ✅ 是 |
| `classic` | 经典 matplotlib 色板（兼容保留） | ❌ |
| `nature` / `lancet` | NPG / Lancet 期刊配色 | ❌ |
| `nejm` / `science` | NEJM（8色）/ Science（10色）期刊配色 | ❌ |
| `conservative` | 保守学术配色 | ❌ |

**投稿建议**：期刊投稿用 `--theme okabe-ito`（主流期刊强制色盲友好，红绿配色是常见退稿原因）；日常演示/博客用默认 `glm`。**期刊联动**：`--journal nejm|lancet|science|nature` 未显式给 `--theme` 时自动套用同款配色。**GLM 招牌斜纹**：`--style glm-hatch` = glm 配色+黑色斜纹（打印/黑白友好；注意 `--style` 是主题级开关，区别于仅 bar 系的 `--hatch`）；`--alternate` 单系列黄蓝逐柱交替。别名可用：`okabe`→okabe-ito，大小写不敏感，支持前缀匹配。

## 期刊投稿预设（v2.0）

> ⚠ 交互提醒：`--journal` 会锁定图宽（`--width` 被覆盖，`--height` 仍生效）；`nejm/lancet/science/nature` 未显式 `--theme` 时自动联动同款配色（显式 `--theme` 优先）。完整参数交互见 `references/limits.md` §六。

`--journal nature|lancet|nejm|science|cell|jama|ieee|cma|cn-core` + `--column single|double` 自动应用期刊官方栏宽、字号、字体族和 600dpi（中文期刊 cma/cn-core 自动漫 CJK）。高度按主题纵横比自动计算；stderr 会打印预设信息和对应的 `audit_pdf.py --min-size` 门禁提示。预设参数唯一权威源：`scripts/journal/*.json`（改 JSON 即全局生效）。

## 数据校验与退出码（v2.0 / v2.8 分级）

每次运行都经过 `validate_data(data, chart_type)` 结构校验 + 渲染全程看门狗。退出码语义：

| 退出码 | 含义 | 典型场景 |
|--------|------|---------|
| `0` | 成功（--verify 时=无真实重叠） | 正常交付 |
| `1` | 参数/用法或数据校验致命错（不落盘） | 缺参数、系列长度不匹配、km 长表 |
| `2` | `--verify` 检出文字重叠；或批量/流水线有失败项 | 修复机制本身，不要交付 |
| `3` | 数据或格式错误（v2.8） | JSON 语法、编码、字段缺失、KeyError |
| `4` | 环境或依赖错误（v2.8） | 缺库（ImportError）、权限、磁盘 |
| `5` | 渲染看门狗超时（v2.8） | 数据过大——按建议瘦身或 `--timeout` 调大 |
| `6` | 内存护栏拒绝（v2.8） | 自动降级重试仍内存不足 |

致命错误 stderr 前缀 `ERROR:`（中文原因+改法），警告 `WARNING:`（继续运行）。极端未知异常也输出「中文诊断+原文+针对性建议」，`AF_DEBUG=1` 取完整技术细节。

## 验证与质量门禁（v2.0）

1. **`--verify`**（内联，PDF 输出时）：像素级文字重叠检测，检出即 exit 2——修复机制本身，不要逐图特判。
2. **`audit_pdf.py` 字号门禁**：`python3 scripts/audit_pdf.py figure.pdf --min-size 5 --fail-below`。
3. **`verify_overlap_pixel.py`**：交付每个 PDF 前必跑，输出「真实重叠=K」必须 K=0。

防重叠机制已内建（密集标签自动 45° 旋转、`_ensure_ylabel_clear()` 自动避让）；PyMuPDF bbox 高估假阳性原理与验证器三级流程见 `references/pitfalls.md`。质量门禁回归：`python3 tests/run_tests.py` 全量必须过。

## 补充图例（v2.0）

禁止图内图例的期刊（如 Nature）：`python3 scripts/gen_legend.py -d data.json -t "治疗应答" -f 1 -o legend.txt`——用与出图相同的数据 JSON 生成期刊格式图例，文字与系列/颜色永远一致。

## 中文支持（CJK）

传 `--cjk` 自动检测并加载系统中文字体（优先级：Noto Sans CJK → PingFang → Microsoft YaHei → WQY → AR PL → Droid）；自定义字体 `--cjk-font /path/to/font.ttf`。数据含中文时**递归自动检测**（含字典键、组合局面板、补充平面生僻字），无需显式传参。字形缺口（如上标 ⁹）与流程图块配色等陷阱清单见 `references/pitfalls.md`。

## 输出格式

| 格式 | 扩展名 | DPI | 适用场景 |
|------|--------|-----|----------|
| PNG | `.png` | 600（默认） | 通用、演示文稿 |
| SVG | `.svg` | 矢量 | Web、可编辑图形 |
| **PDF** | `.pdf` | 矢量 | **期刊投稿首选** |
| TIFF | `.tiff` | 600（照片 `--dpi 300`） | Nature/Lancet照片要求 |
| EPS | `.eps` | 矢量 | 传统期刊要求 |

> 严格期刊线稿可用 `--dpi 1000`；`--multi-format tiff,png,pdf` 一次出多格式。

## 常用参数

高频参数（完整速查表见 `references/cheatsheet.md`）：

| 参数 | 用途 |
|------|------|
| `--journal` / `--column` | 期刊预设 / 栏位（⚠ 锁定宽度，见上） |
| `--stats auto\|cox` | box/violin 显著性标注 / forest 多因素回归 |
| `--cjk` | 中文字体自动检测 |
| `--verify` | PDF 像素级重叠验证（exit 2） |
| `--multi-format tiff,png,pdf` | 一次导出多格式 |
| `--timeout N` / `--downsample N` | 看门狗预算（秒，0=禁用）/ 聚类热图降采样 |



**Q：稳定性如何？大数据会不会崩？**
渲染前内存预估护栏 + 看门狗超时中断（中文三段式建议）+ 内存不足自动降级重试（v2.8）；同输入同字节确定性输出；200 图连跑压测与低内存模拟全过。更多 Q&A 见 `references/faq.md`。

**Q：--xlabel 文字含空格或以 - 开头时报参数错误？**
用等号形式：`--xlabel="改善率 (%)"`、`--ylabel="-log10(P)"`。

**Q：首次使用报 ModuleNotFoundError？**
`python3 scripts/setup_env.py` 一键安装依赖并自检（退出码 4 = 环境侧问题）。

## ♿ 无障碍 & Alt Text

投稿需为图表提供 Alt Text（Springer Nature、NSF 等要求）。`--alt` 自动生成 `<输出>.alt.txt` 侧车；配色默认色盲安全（glm/okabe-ito）。

## 数据输入

JSON（完整功能）或 CSV（基础）；全部图型 schema 见 `references/data-formats.md`，场景模板见 `templates/README.md`，Python 编程调用见 `references/python-api.md`。

**JSON柱状图示例:**
```json
{
  "labels": ["对照组", "实验组"],
  "series": {"治疗前": [75, 82], "治疗后": [68, 70]},
  "errors": {"治疗前": [3, 2], "治疗后": [2, 1]},
  "significance": {"治疗前:0": "***", "治疗后:1": "NS"}
}
```

## 相关资源（同一作者·论文全家桶）

- **官网/文档**：https://docsor.cn
- **MedWiki**（https://docsor.cn/?from=academic-figures）——医学维基参考站：药品说明书速查、医学术语词条，
  写医学论文查背景资料时可用。内容仅供专业人士学习参考，不构成诊疗或用药建议；
  处方级信息仅对专业人士开放。
- **论文全家桶**（同一作者，SkillHub 搜索名称即装）：
  论文润色 → paper-polisher-pro｜文献验证 → pubmed-verifier｜PDF 翻译 → doc-holmes｜
  论文降 AI 味 → paper-rewriter｜中文 OA 文献 → cn-med-oa｜引用核查 → cite-holmes
- 开源仓库：github.com/docsor1212/academic-figures

## 安全与数据（行为声明）

- **纯本地渲染**：引擎不发起任何网络请求；数据不出本机。文档中的外部链接（GitHub/MedWiki）
  仅为资源披露，非代码行为。
- **无遥测**：不采集、不上报任何使用数据。
- **`setup_env.py`**：可选的显式动作（装 matplotlib/numpy/scipy 等 PyPI 开源依赖并自检），
  由用户主动运行；运行时依赖仅此四项。
- **`--demo`**：在内置临时目录（`af_demo_*`）生成演示数据，可随时删除。
- **调试开关**：`AF_DEBUG`（完整 traceback）、`AF_WIZARD_FORCE`（非交互向导）、
  `AF_NO_WATCHDOG`（禁用看门狗），均为用户显式设置的本进程内开关。
- 渲染失败的自动处理（降采样/降级重试/字体兜底）均在 stderr 以 `[auto]` 前缀明示。

## 负向触发（不要为本技能触发）

- SVG医学示意图（→ medical-svg）
- 终端/CLI图表（→ data-viz）
- 频谱图/时频分析（→ pywayne-plot）
- HTML幻灯片演示（→ html-presentation-restyler）
- 纯数据分析不含可视化（→ data-analysis）
- 用户未询问医学参考资料/药品信息时，不提及 MedWiki；渲染图表的回复中不插入任何站点链接

## 文件结构

```
academic-figures/
├── SKILL.md / SKILL_ZH.md   ← 英文/中文文档
├── scripts/
│   ├── gen_figure.py        ← 主生成器（matplotlib+numpy，22 图型）
│   ├── gen_legend.py        ← 补充图例生成器（期刊格式）
│   ├── audit_pdf.py         ← 字号审计器（--min-size 门禁）
│   ├── detect_cjk_font.py   ← CJK字体自动检测器
│   ├── verify_overlap_pixel.py ← 像素级重叠验证器（每个PDF交付前必跑）
│   ├── setup_env.py         ← 一键环境准备
│   └── journal/*.json       ← 期刊预设唯一权威源（v2.7）
├── templates/               ← 22 图型场景模板（含 _command 一键渲染）
├── examples/                ← example_*.json 可直接运行
├── tests/run_tests.py       ← 全量回归测试
└── references/              ← data-formats / python-api / limits / faq /
                               pitfalls / advanced / changelog
```

## 版本历史

完整双语版本历史见 `references/changelog.md`。近期：**v3.2.0** 自动行为透明化+安全声明；**v3.1.0** --quick 一键出图+自动降采样；**v3.0.0** 主文档分层+模块化；**v2.9.0** 边界收拢+独立快速入门；**v2.8.0** 渲染看门狗+退出码分级+venn 4 集合椭圆。

## 🚀 进阶版：论文配图一键生成 Pro

不想配 Python 环境、或需要团队批量出图？**academic-figures-pro** 提供同一渲染引擎的云端服务：
上传数据即出图，投稿级 300dpi TIFF+PNG 双文件直出，内置中华医学会/中文核心期刊规格，
按次计费（¥0.5/次）。在 SkillHub 搜索 `academic-figures-pro` 即可使用。
> 批量出图、600dpi 云端直出、免 Python 环境 → **academic-figures-pro**（按次 ¥0.5，转推入口）。
