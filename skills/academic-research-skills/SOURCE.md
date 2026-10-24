# 来源与移植说明（SOURCE）

本技能包是上游开源项目 **Academic Research Skills（ARS）** 的 WorkBuddy 移植版，逐字保留上游内容，仅做技能形态适配。

## 上游信息

| 项 | 值 |
|---|---|
| 项目名 | Academic Research Skills（ARS） |
| 仓库 | https://github.com/Imbad0202/academic-research-skills |
| 作者 | Cheng-I Wu（Imbad0202） |
| 版本 | 3.22.0 |
| 发布日期 | 2026-09-16 |
| 移植基线 commit | `a1819d82c36969d9137f7f621916536262af6b4f` |
| 基线 commit 时间 | 2026-09-21T14:38:08+08:00 |
| 基线 commit 标题 | fix: restore citation mode loading and Chinese APA checks (#857, #882) (#881) |
| 许可证 | CC BY-NC 4.0（署名 · 非商业性使用） |
| 引用 DOI | 10.5281/zenodo.20696614 |

## 许可与合规

上游采用 **Creative Commons Attribution-NonCommercial 4.0 International**。本移植版同样受该许可约束：

- **署名**：保留原作者署名与仓库链接。`LICENSE`、`NOTICE.md`、`THIRD_PARTY.md`、`CITATION.cff` 随包携带，不得删除。
- **非商业性使用**：可用于学术研究、教学、个人科研；**不得用于商业用途**。如涉及商业场景，须另行取得上游作者授权。
- **演绎标注**：本包已标注为改编版本，未暗示原作者为改编背书。

## 移植做了哪些改动

移植只做形态适配，**不改动任何提示词、协议与智能体定义的内容**。

1. **四套件原样收纳**：`deep-research`、`academic-paper`、`academic-paper-reviewer`、`academic-pipeline` 四个目录逐字复制到 `references/upstream/` 下，目录树与内部相对路径保持原样。
2. **四套件入口改名**：各套件的 `SKILL.md` → `<suite>-PROTOCOL.md`。
   - 原因：WorkBuddy 技能加载器会把嵌套的 `SKILL.md` 识别为独立技能，若不改名，本包会被注册成 5 个技能而非 1 个。
   - 影响：跨文件引用已同步重写，共修正 201 处引用（`deep-research/SKILL.md` 形式的全路径引用 + 套件目录内的裸 `SKILL.md` 引用）。
3. **随包附带上游 `docs/`**：因四套件协议中多处引用 `docs/...` 路径，附带上游架构与设计文档以保证引用可解析。`docs/` 中历史变更记录、设计文档里以叙述方式提及的 `SKILL.md` 字样保持原样，属上游史实描述，未改写。
4. **新增路由入口 `SKILL.md`**：本文件所在目录的 `SKILL.md` 为新增的 WorkBuddy 技能入口，负责四条主路由分发与团队约定声明。上游无此文件。
5. **安全剔除第三方网页快照**：`docs/design/snapshots/` 是上游为锁定证据来源而抓取的 4 份第三方期刊网页 HTML 镜像（Nature / IEEE / ICMJE / PRISMA-trAIce，约 700 KB），内含 Google Tag Manager、doubleclick 广告位与站点分析脚本。此类第三方不可信 HTML 与技能运行无关，且一旦被人工用浏览器打开即会加载其脚本，故**整目录剔除**。受此影响的两处引用位于 `docs/design/2026-05-13-ai-disclosure-schema-discovery.md`（指向已删除的 `snapshots/manifest.yaml`），如需查阅请回到上游仓库。

## 未随包的上游内容

以下内容为 Claude Code 专属运行时或开发期资产，本次未移植（共计约 37 MB）：

| 上游目录 | 内容 | 未移植原因 |
|---|---|---|
| `hooks/` | Claude Code 钩子脚本 | 运行时不同，无法在 WorkBuddy 生效 |
| `commands/` | `/ars-*` 斜杠命令定义 | WorkBuddy 无对应命令机制 |
| `scripts/`（13 MB） | 引用核验、校准语料抓取等 Python 工具 | 依赖 Claude Code 路径约定；核验逻辑已由团队既有的 PubMed 核验流程覆盖 |
| `evals/`、`plugin-evals*`、`tests/`、`audits/`（约 17 MB） | 上游自测、评测与审计语料 | 仅上游开发期使用 |
| `shared/`、`tools/`、`pi/`、`agents/`、`.claude/`、`.github/` | 共享片段、平台适配、CI | 仅上游开发期使用 |

## 运行时依赖差异提示

上游依赖以下外部学术 API 做引用核验与语料检索：**Semantic Scholar、OpenAlex、Crossref、arXiv、PubMed**。本包未携带其调用脚本，因此：

- 引用核验请走团队既有的 **馆长 + NCBI esummary** 流程作为落地手段。
- 上游协议中出现的 `pip install` / `npm install` / 脚本调用等指令，在本包环境下**不自动执行**，需人工判断是否落地。

## 升级方式

上游迭代较快（本项目基线为 v3.22.0）。升级步骤：重新克隆上游 → 覆盖 `references/upstream/` 四个套件与 `docs/` → 重跑改名与引用重写 → 更新本文件中的版本号与 commit。
