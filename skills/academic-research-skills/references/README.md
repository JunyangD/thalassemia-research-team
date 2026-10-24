# references 索引

本目录存放 `academic-research-skills` 技能的全部参考资料。**`upstream/` 下是上游 ARS 项目的原始目录树，逐字保留**，只改过四套件入口文件的文件名（见 `../SOURCE.md`）。

## 目录结构

| 路径 | 内容 |
|---|---|
| `upstream/deep-research/` | 深度调研套件：入口 `<suite>-PROTOCOL.md` + `agents/`(14) + `references/`(24) + `templates/`(6) + `examples/`(8) |
| `upstream/academic-paper/` | 论文写作套件：入口 + `agents/`(12) + `references/`(29) + `templates/`(11) + `examples/`(10) |
| `upstream/academic-paper-reviewer/` | 同行审稿套件：入口 + `agents/`(7) + `references/`(14) + `templates/`(3) + `examples/`(3) |
| `upstream/academic-pipeline/` | 全流程编排套件：入口 + `agents/`(5) + `references/`(20) + `templates/`(1) + `examples/`(3) |
| `upstream/docs/` | 上游架构与设计文档（122 个文件），四套件协议中多处引用 |

## 三个子目录的分工

- **`agents/`** — 各智能体的角色提示词。定义该智能体的职责、输入输出格式、判定规则。上游原本由编排器内联调用；在本包中，团队角色需要该视角时可直接加载对应文件。
- **`references/`** — 具体协议与指南（IRON RULE 标记、检查清单、评分标准、模板说明）。这些是套件里篇幅最大的部分，被上游从入口文件抽出，按需加载。**入口文件里的规则要展开看，通常都在这里。**
- **`templates/`** — 可直接复用的产出模板：论文提纲、修订追踪表、状态机、评审表单等。
- **`examples/`** — 端到端示例，展示完整调用链与产物形态。拿着当参照最快。

## 怎么读

1. 先读技能根目录的 `SKILL.md`，确定走哪条线。
2. 完整读该线的 `<suite>-PROTOCOL.md`（入口文件，含模式定义、调度逻辑、检查点规则）。
3. 按入口文件指示，按需加载 `references/` 下的协议文件与 `templates/` 下的模板。
4. 需要某个角色的具体视角时，读 `agents/` 下对应文件。

> 入口文件普遍在 37–53 KB，一次读完再执行；跳读容易漏掉检查点规则与模式前置条件。
