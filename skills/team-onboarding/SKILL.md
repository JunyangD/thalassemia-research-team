---
name: team-onboarding
description: >
  地贫科研团队的初始化与成员自定义。负责三件事：①首次使用的引导式建档（问清称呼、研究方向、
  团队名、主理人名字、工作目录、成员配置、引用与排版偏好），并在用户指定路径生成团队工作文件夹；
  ②每轮对话开始时读取已存档案，把团队配置注入调度上下文；③后续改配置（加人、减人、停用、改名、
  换团队名、换工作目录、登记服务器）。触发词：首次使用、初始化、建档、建工作文件夹、改团队配置、
  加成员、删成员、改名字、换目录、onboarding、setup。
---

# 团队初始化与成员自定义

这个技能解决一个具体问题：**用户第一次用这个团队时，团队还不知道他是谁、研究什么、要几个人、文件放哪。**
没有这一步，团队就会用一套通用假设硬干，产出不对味。

服务对象通常是**不熟悉 AI 的科研人员**。所以本技能的第一原则是：**不让用户面对空白输入框**——每个问题都给选项、给默认值、给一句大白话解释。

---

## 一、先判断走哪条路

第一步永远是探测，不要凭印象假设。

```bash
python <skill_dir>/scripts/read_profile.py
```

| 输出 | 走哪条路 |
|------|---------|
| `"found": false` | **路径 A：首次建档**（本技能主体） |
| `"found": true` | **路径 B：直接开工**。把摘要里的 `members`、`owner.call`、`preferences`、`workspace` 记进上下文，然后用 `owner.call` 称呼用户 |
| 用户明确说"我要改团队/加个人/改名/换目录" | **路径 C：改配置** |

`skill_dir` 是本技能目录，即 `<专家包>/skills/team-onboarding`。

---

## 二、路径 A：首次建档

### A0. 开场（先安抚，再提问）

第一次建档时，先说一句让用户安心的话，再开始问：

> 先花两分钟做个登记，之后就不用再填了。我一次只问两三个问题，拿不准的地方我会给建议选项，您直接选就行。

**然后分三轮提问，每轮用 AskUserQuestion 工具做成选项卡片。**
一次只问 2–3 个，绝不把所有问题堆在一轮里——问题一多，不熟 AI 的用户会直接放弃。

> 如果 AskUserQuestion 不可用，就退化成纯文本提问：每个问题给出"1./2./3."编号选项和默认值，让用户回数字或直接说。

---

### A1. 第一轮：先认识您

三个问题（header 分别为「称呼」「研究方向」「交流语言」）：

**Q1 我该怎么称呼您？**
- 老师（推荐）
- 主任
- 医生
- （用户可自己输入姓名或别的称呼）

**Q2 您主要的研究方向是什么？**
- 地中海贫血
- 血液遗传病
- 基因治疗与基因编辑
- （用户可自己输入；这是自由文本高发区，务必允许自定义）

**Q3 平时用哪种语言跟我交流？**
- 中文（推荐）
- 中英混合
- 英文

> 用户答的研究方向会作为 `owner.field` 注入所有成员，是他们判断"这个方案对不对路"的唯一依据。**不要跳过，也不要替用户填成"地贫"。**

---

### A2. 第二轮：起名字、定位置

**Q4 您想怎么称呼我（主理人）？**
- 大管家（推荐）
- 总管
- 助理
- （可自定义）

**Q5 团队叫什么名字？**
- 地贫科研团队（推荐，默认）
- 血液病科研团队
- 我自己的实验室名
- （可自定义；用户改中文名后，英文名保留 `Thalassemia Research Team`，后续可手改 `teamName.en`）

**Q6 工作文件夹放在哪里？**
- 我的文档／地贫科研团队（推荐，默认）
- 桌面／地贫科研团队
- 我自己指定一个路径（选此项时，**必须追问一句**："请把完整路径发给我，例如 `D:\科研\地贫科研团队`"）

> Windows 路径要用反斜杠或正斜杠都行，脚本会自动规范化。用户给的路径若已存在同名团队档案，脚本会拒绝覆盖并提示——这时转路径 B。

---

### A3. 第三轮：定班底

**Q7 团队先配几个人？**
- 全套 9 人（推荐）：主理人 + 文献、领域、数据、规划、商业、医学、配图、环境
- 精简 5 人：主理人 + 文献、领域、数据、规划
- 只留主理人，以后再加
- 我自己挑（选此项时，列出 9 个名字和一句话职责，让用户报编号）

**Q8 引用和排版按哪套来？**（这决定产出文档长什么样）
- 句末标 PMID 红色 + 宋体四号1.5倍行距（推荐，适合中文医学论文）
- GB/T 7714 顺序编码制
- 作者-年份制（APA 风格）
- 先不定，以后再说

**Q9（可省，只在用户表现出有服务器时问）有没有服务器或集群要接？**
- 没有，只用本机（推荐）
- 有，我稍后告诉你地址
- 以后再说

> Q9 若答"有"，不要当场追问 IP 和密码。只把 `server.enabled` 置为 true，其余留空，等维护师第一次被调用时自己问。

---

### A4. 建目录前先给一张确认表

把收上来的信息整理成表，让用户过一眼。**这是防错的最后一道闸**，尤其路径和团队名。

```
| 项目 | 内容 |
|------|------|
| 称呼 | 老师 |
| 研究方向 | 地中海贫血与铁过载 |
| 团队名 | 地贫科研团队 |
| 主理人 | 大管家 |
| 成员 | 9 人（全套） |
| 工作目录 | D:\科研\地贫科研团队 |
| 引用规范 | 句末 PMID 红色 + 宋体四号1.5倍行距 |
| 服务器 | 暂不接 |

确认无误我就开始建文件夹；有要改的直接说。
```

用户点头后再往下走。**没确认就建目录，等于把档案建在错的地方。**

---

### A5. 落盘

把确认后的信息写成一个 JSON（用 Write 工具落盘，UTF-8），然后跑脚本：

```bash
python <skill_dir>/scripts/init_workspace.py --input <临时payload.json>
```

payload 最小示例：

```json
{
  "workspace": "D:/科研/地贫科研团队",
  "teamName": { "zh": "地贫科研团队", "en": "Thalassemia Research Team" },
  "leadName": "大管家",
  "owner": { "call": "老师", "field": "地中海贫血与铁过载", "language": "zh" },
  "members": null
}
```

- `members: null` = 用默认 9 人全套。
- 精简 5 人时传数组，只列要留下的：

```json
"members": [
  {"agentId": "thalassemia-research-team-lead", "name": "大管家", "role": "lead"},
  {"agentId": "librarian"},
  {"agentId": "thalassemia-expert"},
  {"agentId": "data-engineer"},
  {"agentId": "research-advisor"}
]
```

只给 `agentId` 即可，职业和职责会自动补全；用户自定义的名字用 `"name"` 覆盖。

**退出码含义**：`0` 成功；`2` 该目录已有档案（没动任何文件，转路径 B）；`1` 参数错误。

---

### A6. 确认建好，并说清下一步

建完必须回显三件事，缺一不可：

1. **目录树**（截取 `createdDirs`，按层级展示）
2. **成员名册**（`memberNames`）
3. **一句话怎么用**："以后直接把需求说中文就行，不用记命令。"

收尾话术示例：

> 建好了，在 `D:\科研\地贫科研团队`。
> 里面分五块：`团队宪章` 放约定，`成员` 放各人产出，`项目` 放长期课题，`任务` 放一次性活儿，`共享` 放成品。
> 以后您直接说需求，我派给对应的人去做。想改团队配置随时说一声。

最后跑一次体检确认没有半成品状态：

```bash
python <skill_dir>/scripts/check_workspace.py
```

---

## 三、路径 B：已有档案

`read_profile.py` 返回 `found: true` 时：

1. 把 `owner.call` 当称呼用（用户叫"老师"就别说"用户"）。
2. 把 `members` 里 `role=lead` 之外的人当作可用班底，按 `duty` 路由；**`disabled` 里的人一律不派活**。
3. `preferences.citation` / `docFormat` 是全体成员的硬约束，下发任务时随 prompt 一起传。
4. `server.enabled` 为 false 时，不要主动提服务器方案。

不要重复提问。用户已经答过的东西再问一遍，是最伤体验的错误。

---

## 四、路径 C：改配置

统一走 `manage_members.py`，不要手改 JSON——手改会漏掉 `团队宪章.md`、`README.md` 和全局指针的同步。

```bash
# 看现状
python <skill_dir>/scripts/manage_members.py list

# 加人（自定义成员）
python <skill_dir>/scripts/manage_members.py add --name 统计师 --profession 生物统计师 --duty "样本量与检验效能计算"

# 停用 / 启用（内置成员只能停用，不能删文件）
python <skill_dir>/scripts/manage_members.py disable --id medical-professor
python <skill_dir>/scripts/manage_members.py enable  --id medical-professor

# 删自定义成员
python <skill_dir>/scripts/manage_members.py remove --id custom-m9

# 改名
python <skill_dir>/scripts/manage_members.py rename --id science-illustrator --name 美工

# 换主理人称呼 / 换团队名 / 改称呼与方向 / 登记服务器
python <skill_dir>/scripts/manage_members.py set-lead  --name 总管
python <skill_dir>/scripts/manage_members.py set-team  --name "血液病科研团队"
python <skill_dir>/scripts/manage_members.py set-owner --call 主任 --field "骨髓衰竭性疾病"
python <skill_dir>/scripts/manage_members.py set-server --enabled --host 10.0.0.5 --user lab --shared-root /data/shared --private-root /home/lab
```

改完脚本会自动重渲染人读版文件并更新指针，不需要手动补。

**换工作目录**不支持脚本迁移（涉及大量历史文件）。做法：在新位置跑一次 `init_workspace.py`，再把旧目录的 `项目/`、`任务/`、`成员/` 手动搬过去。

---

## 五、自定义成员怎么被调度

这是本技能最容易出问题的地方，务必讲清。

- **内置成员**（`builtin: true`）有对应的 agent 文件，用 Agent 工具时 `name` 与 `subagent_type` 都传 `agentId`。
- **自定义成员**（`builtin: false`）**没有** agent 文件。调度时用 `general-purpose` 充当，并在 prompt 开头注入角色卡：

```
你现在是「{团队名}」的成员「{name}」，职业是「{profession}」。
职责：{duty}。
服务对象：{owner.call}，研究方向：{owner.field}。
引用规范：{preferences.citation.note}
排版规范：{preferences.docFormat 摘要}
只做本职范围内的事；完成后用 SendMessage 把结论回传给主理人，不要直接联系其他成员。
```

角色卡模板见 `references/member-rolecard-template.md`。

> 这不是"假装有个人"，而是用通用执行体承担一个明确写死的岗位职责。产出仍由该执行体独立完成，主理人不代写。

---

## 六、话术原则（面向不熟 AI 的用户）

1. **一次最多三问。** 超过三问，用户会乱选或直接说"随便"。
2. **每问都给推荐项。** 推荐项排第一，标注"（推荐）"。
3. **不用术语。** 不说 `payload`、`schema`、`profile`，说"登记表""配置文件"。
4. **不问密码。** 服务器凭据等真正要用时再问，且不写进档案。
5. **不催。** 用户说"先这样"，就用默认值建，之后能改。
6. **答完就动手。** 不要在建档环节顺带做科研任务——先把家安好，再谈干活。

---

## 七、脚本清单

| 脚本 | 作用 | 主要参数 |
|------|------|---------|
| `scripts/lib_profile.py` | 公共库：默认成员、档案构造、渲染 | 不直接调用 |
| `scripts/init_workspace.py` | 建目录 + 写档案 + 写指针 | `--input <json>`、`--force` |
| `scripts/read_profile.py` | 定位档案并输出摘要 | 无；`--raw` 出完整档案 |
| `scripts/manage_members.py` | 成员与设定增删改 | 见路径 C |
| `scripts/check_workspace.py` | 体检（结构、字段、目录、指针） | 无 |

脚本路径需要用运行环境的 Python 解释器。**不要假设 `python` 命令可用**：先探测 `python3` / `python` / 托管解释器，取第一个能跑 `--version` 的。

---

## 八、常见问题处置

| 用户说 | 怎么办 |
|-------|--------|
| "我不想建文件夹，就在这儿聊" | 说明：不建档也能聊，但团队记不住您的方向和偏好，每次都要重说。建议花两分钟建一次 |
| "我放错地方了" | 在新位置重建，再搬 `项目/`、`任务/`、`成员/`；旧目录留着不删 |
| "换电脑了" | 指针指向旧机器，会 `found: false`。问用户原来那个文件夹在不在，在就直接读那个目录下的 `团队宪章/team-profile.json` 并重建指针 |
| "成员太多了看不过来" | 用 `disable` 停用不急的几个，不必删 |
| "我要一个别人都没有的岗位" | 用 `add`，`--duty` 写清"他负责干什么、产出长什么样"。职责写得越具体，这个岗位越好用 |
| "为什么他老说自己不会" | 检查该成员是否被停用；自定义成员的角色卡里 `duty` 是否为空 |

---

## 九、收尾自检（每次建档后必须做）

- [ ] `read_profile.py` 返回 `found: true`，`workspace` 与用户说的一致
- [ ] `check_workspace.py` 退出码为 0（或仅有可解释的警告）
- [ ] 工作区根目录条目不超过 7 项
- [ ] 每位启用成员都有 `成员/<名字>/项目/`
- [ ] 已把 `owner.call`、`field`、成员名册、引用与排版偏好记入本轮上下文
