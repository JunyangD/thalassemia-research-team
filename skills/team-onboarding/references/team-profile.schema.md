# team-profile.json 字段说明

团队档案的正本，位于 `<工作目录>/团队宪章/team-profile.json`。
人读版是同目录的 `团队宪章.md`（由脚本渲染，勿手改）。两者冲突时以本 JSON 为准。

> 修改请走 `manage_members.py`，手改容易漏掉人读版与全局指针的同步。

---

## 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `schemaVersion` | string | 档案格式版本，当前 `"1.0"` |
| `plugin` | string | 固定 `"thalassemia-research-team"` |
| `teamName` | `{zh, en}` | 团队名称。用户改中文名后英文名保留默认值，可手改 |
| `leadName` | string | 主理人称呼，与 `members` 中 `role=lead` 的 `name` 保持一致 |
| `workspace` | string | 工作目录绝对路径，正斜杠或反斜杠均可 |
| `owner` | object | 服务对象信息，见下 |
| `preferences` | object | 写作与引用偏好，见下 |
| `members` | array | 成员名册，见下 |
| `server` | object | 服务器登记，未配置时 `enabled=false` |
| `createdAt` / `updatedAt` | string | `YYYY-MM-DDTHH:MM:SS` |

## owner

| 字段 | 说明 |
|------|------|
| `call` | 对用户的称呼。所有成员对外说话都用它，不要用"用户" |
| `field` | 研究方向。成员判断"方案对不对路"的唯一依据 |
| `language` | `zh` / `mixed` / `en` |
| `note` | 自由补充，可空 |

## preferences

```json
{
  "citation": {
    "style": "pmid-inline",
    "recentYears": 5,
    "verifyBy": "pubmed-verifier",
    "note": "观点句末标（pmid：XXXXXXX），红色字体，句号在括号外"
  },
  "docFormat": {
    "font": "中文宋体 / 西文 Times New Roman",
    "bodySize": "四号",
    "headingSize": "三号加粗",
    "lineSpacing": 1.5,
    "firstLineIndent": "2 字符",
    "paper": "A4",
    "bibliographyStyle": "GB/T 7714"
  },
  "antiAiTone": true,
  "language": "zh"
}
```

`citation.style` 可选值：

| 值 | 含义 |
|----|------|
| `pmid-inline` | 句末标 `（pmid：XXXXXXX）`，红色，句号在括号外 |
| `gbt7714` | 正文用顺序编码上标，文末 GB/T 7714 列表 |
| `author-year` | 作者-年份制（APA 风格） |
| `none` | 暂不设定，成员按期刊要求临时商量 |

`antiAiTone` 为 true 时，所有文字产出须过 `anti-defensive-writing` 与去模板化表达检查。

## members[]

| 字段 | 必填 | 说明 |
|------|------|------|
| `agentId` | 是 | 内置成员用固定 ID（如 `data-engineer`）；自定义成员用 `custom-<ascii>` |
| `name` | 是 | 显示名，用户可改 |
| `profession` | 是 | 职业头衔 |
| `duty` | 是 | 职责。路由全靠它，写得越具体越好 |
| `scope` | 否 | 归属分组，用于人读版表格 |
| `builtin` | 是 | 是否有对应 agent 文件 |
| `enabled` | 是 | 是否参与调度 |
| `role` | 是 | `lead` 或 `member`，有且只有一个 `lead` |

内置 `agentId` 清单（不可新增，只能停用）：

```
thalassemia-research-team-lead  主理人
librarian                       馆长
thalassemia-expert              地贫管家
data-engineer                   代码专家
research-advisor                科研顾问
business-strategist             商业巨头
medical-professor               医学教授
science-illustrator             绘图师
maintenance-engineer            维护师
```

## server

```json
{
  "enabled": false,
  "host": "",
  "user": "",
  "sharedRoot": "",
  "privateRoot": "",
  "note": "未配置；维护师首次被调用时会先问清机器信息再动手"
}
```

**凭据（密码、密钥口令）一律不写入本文件。** 需要时由用户在会话内提供。

## 全局指针

`~/.workbuddy/team-profiles/thalassemia-research-team.json` 只存定位信息（工作目录、档案路径、团队名、称呼、成员数、更新时间）。
作用是让新会话不必扫描磁盘就能找到档案。档案搬家后重跑 `init_workspace.py` 或任意 `manage_members.py` 命令即可重建指针。
