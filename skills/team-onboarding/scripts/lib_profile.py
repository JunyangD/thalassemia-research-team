# -*- coding: utf-8 -*-
"""
lib_profile.py — 地贫科研团队 · 团队档案与工作区公共库

被 init_workspace.py / read_profile.py / manage_members.py / check_workspace.py 共用。
设计约束：
  1. 只用标准库，跨平台（Windows / macOS / Linux）。
  2. 所有文件读写显式 encoding='utf-8'，避免 Windows 默认码页导致中文乱码。
  3. 不覆盖已有档案：写入前先检查，必要时备份。

档案分两级：
  · 工作区内正本：<workspace>/团队宪章/team-profile.json
  · 全局指针：~/.workbuddy/team-profiles/<plugin>.json  （只存 workspace 路径与摘要，便于跨会话定位）
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PLUGIN = "thalassemia-research-team"
SCHEMA_VERSION = "1.0"

DEFAULT_TEAM_NAME = {"zh": "地贫科研团队", "en": "Thalassemia Research Team"}

# ---------------------------------------------------------------- 默认成员

DEFAULT_MEMBERS = [
    {
        "agentId": "thalassemia-research-team-lead",
        "name": "大管家",
        "profession": "科研调度总监",
        "duty": "拆解任务、按专业路由给成员、监控进度、汇总各线结论；不亲自代写专业产出",
        "scope": "编排与汇编",
        "builtin": True,
        "enabled": True,
        "role": "lead",
    },
    {
        "agentId": "librarian",
        "name": "馆长",
        "profession": "知识库馆长",
        "duty": "论文与推文入库、文献检索、引用核验、引用网络维护",
        "scope": "文献与知识库",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "thalassemia-expert",
        "name": "地贫管家",
        "profession": "地贫研究专家",
        "duty": "实验设计、文献深度分析、研究方向规划、机制推演、综述撰写",
        "scope": "领域专业判断",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "data-engineer",
        "name": "代码专家",
        "profession": "数据分析工程师",
        "duty": "Python/R 脚本、统计分析、可视化出图、工具与小流程开发",
        "scope": "数据与代码",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "research-advisor",
        "name": "科研顾问",
        "profession": "科研项目规划师",
        "duty": "选题方案、项目背景、临床数据需求、文献综述、基金申报支撑",
        "scope": "项目规划",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "business-strategist",
        "name": "商业巨头",
        "profession": "商业策划师",
        "duty": "商业计划书、商业模式设计、财务预测、成果转化叙事",
        "scope": "商业转化",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "medical-professor",
        "name": "医学教授",
        "profession": "医学讲师",
        "duty": "教材讲解、考纲解析、知识点整理、复习笔记与试题解析",
        "scope": "医学教学",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "science-illustrator",
        "name": "绘图师",
        "profession": "科研绘图师",
        "duty": "实验流程图、分子机制图、科研配图（PPT 原生形状，可编辑）",
        "scope": "科研配图",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
    {
        "agentId": "maintenance-engineer",
        "name": "维护师",
        "profession": "服务器环境运维工程师",
        "duty": "服务器/虚拟机环境构建、镜像源治理、依赖安装、环境准入与审计",
        "scope": "环境运维",
        "builtin": True,
        "enabled": True,
        "role": "member",
    },
]

DEFAULT_PREFERENCES = {
    "citation": {
        "style": "pmid-inline",
        "recentYears": 5,
        "verifyBy": "pubmed-verifier",
        "note": "观点句末标（pmid：XXXXXXX），红色字体，句号在括号外；逐条核验后才可写入正文",
    },
    "docFormat": {
        "font": "中文宋体 / 西文 Times New Roman",
        "bodySize": "四号",
        "headingSize": "三号加粗",
        "lineSpacing": 1.5,
        "firstLineIndent": "2 字符",
        "paper": "A4",
        "bibliographyStyle": "GB/T 7714",
    },
    "antiAiTone": True,
    "language": "zh",
}

# 根目录只允许这些条目（收敛的分层纪律：散件一律归档到 任务/ 或 共享/）
ROOT_ITEMS = ["README.md", "团队宪章", ".workbuddy", "成员", "项目", "任务", "共享"]

SUBDIRS = [
    "团队宪章",
    ".workbuddy/memory",
    "共享/技能库",
    "共享/交付",
    "项目",
    "任务",
]


# ---------------------------------------------------------------- 基础工具

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def safe_stdout() -> None:
    """避免 Windows 控制台编码导致中文输出报错。"""
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def backup_file(path: Path) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_name(path.name + f".bak.{stamp}")
    shutil.copy2(path, bak)
    return str(bak)


# ---------------------------------------------------------------- 指针与定位

def pointer_path() -> Path:
    return Path.home() / ".workbuddy" / "team-profiles" / f"{PLUGIN}.json"


def write_pointer(profile: dict) -> Path:
    p = pointer_path()
    data = {
        "plugin": PLUGIN,
        "schemaVersion": SCHEMA_VERSION,
        "workspace": profile["workspace"],
        "profilePath": str(Path(profile["workspace"]) / "团队宪章" / "team-profile.json"),
        "teamName": profile.get("teamName", DEFAULT_TEAM_NAME),
        "leadName": profile.get("leadName", "大管家"),
        "ownerCall": profile.get("owner", {}).get("call", ""),
        "memberCount": len([m for m in profile.get("members", []) if m.get("enabled", True)]),
        "updatedAt": now_iso(),
    }
    save_json(p, data)
    return p


def candidate_workspaces() -> list:
    home = Path.home()
    docs = home / "Documents"
    return [
        Path(os.getcwd()) / "团队宪章" / "team-profile.json",
        docs / DEFAULT_TEAM_NAME["zh"] / "团队宪章" / "team-profile.json",
        home / DEFAULT_TEAM_NAME["zh"] / "团队宪章" / "team-profile.json",
        home / "Desktop" / DEFAULT_TEAM_NAME["zh"] / "团队宪章" / "team-profile.json",
    ]


def find_profile() -> tuple:
    """返回 (profile_dict 或 None, 来源说明)。"""
    p = pointer_path()
    if p.exists():
        try:
            ptr = load_json(p)
            pp = Path(ptr.get("profilePath", ""))
            if pp.exists():
                return load_json(pp), f"pointer:{p}"
            return None, f"pointer_dangling:{p} -> {pp} (档案已不存在)"
        except Exception as e:
            return None, f"pointer_broken:{p} ({e})"
    for cand in candidate_workspaces():
        if cand.exists():
            try:
                return load_json(cand), f"scan:{cand}"
            except Exception:
                continue
    return None, "not_found"


# ---------------------------------------------------------------- profile 构造

def build_profile(payload: dict) -> dict:
    """把引导问答的结果整理成规范档案；缺项用默认值补齐。"""
    workspace = payload.get("workspace") or str(
        Path.home() / "Documents" / DEFAULT_TEAM_NAME["zh"]
    )
    workspace = str(Path(workspace).expanduser().resolve())

    team_name = payload.get("teamName") or DEFAULT_TEAM_NAME
    if isinstance(team_name, str):
        team_name = {"zh": team_name, "en": payload.get("teamNameEn", team_name)}

    prefs = dict(DEFAULT_PREFERENCES)
    user_prefs = payload.get("preferences") or {}
    for k, v in user_prefs.items():
        if isinstance(v, dict) and isinstance(prefs.get(k), dict):
            prefs[k] = {**prefs[k], **v}
        else:
            prefs[k] = v
    if payload.get("owner", {}).get("language"):
        prefs["language"] = payload["owner"]["language"]

    members_in = payload.get("members")
    if not members_in:
        members_in = [dict(m) for m in DEFAULT_MEMBERS]
    else:
        # 用户只给了精简名单时，补齐缺省字段；主理人强制存在
        normalized = []
        for m in members_in:
            base = next(
                (d for d in DEFAULT_MEMBERS if d["agentId"] == m.get("agentId")), None
            )
            item = dict(base) if base else {}
            item.update({k: v for k, v in m.items() if v is not None})
            item.setdefault("builtin", base is not None)
            item.setdefault("enabled", True)
            item.setdefault("role", "member")
            if not item.get("agentId"):
                item["agentId"] = "custom-" + (slugify(item.get("name", "")) or f"m{len(normalized) + 1}")
            normalized.append(item)
        members_in = normalized

    if not any(m.get("role") == "lead" for m in members_in):
        members_in.insert(0, dict(DEFAULT_MEMBERS[0]))

    profile = {
        "schemaVersion": SCHEMA_VERSION,
        "plugin": PLUGIN,
        "teamName": team_name,
        "leadName": payload.get("leadName") or "大管家",
        "workspace": workspace,
        "owner": {
            "call": payload.get("owner", {}).get("call") or "老师",
            "field": payload.get("owner", {}).get("field") or "地中海贫血与血液遗传病",
            "language": prefs.get("language", "zh"),
            "note": payload.get("owner", {}).get("note", ""),
        },
        "preferences": prefs,
        "members": members_in,
        "server": payload.get("server")
        or {
            "enabled": False,
            "host": "",
            "user": "",
            "sharedRoot": "",
            "privateRoot": "",
            "note": "未配置；维护师首次被调用时会先问清机器信息再动手",
        },
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    return profile


def slugify(text: str) -> str:
    """只保留 ASCII 字母数字，避免生成含中文的 agentId。"""
    out = []
    for ch in str(text):
        if ch.isascii() and ch.isalnum():
            out.append(ch.lower())
        elif ch.isascii() and ch in "-_ ":
            out.append("-")
    s = "".join(out).strip("-")
    return s


# ---------------------------------------------------------------- 渲染

def render_charter(profile: dict) -> str:
    owner = profile.get("owner", {})
    prefs = profile.get("preferences", {})
    cit = prefs.get("citation", {})
    fmt = prefs.get("docFormat", {})
    team_zh = profile.get("teamName", {}).get("zh", DEFAULT_TEAM_NAME["zh"])

    rows = []
    for m in profile.get("members", []):
        state = "启用" if m.get("enabled", True) else "停用"
        kind = "内置" if m.get("builtin") else "自定义"
        rows.append(
            f"| {m.get('name','')} | {m.get('profession','')} | {m.get('duty','')} | {m.get('scope','')} | {kind}／{state} |"
        )
    member_table = "\n".join(rows)

    return f"""# {team_zh} · 团队宪章

> 本文件是团队的人读版约定。机器读的正本是同目录下的 `team-profile.json`。
> 两者内容不一致时，以 `team-profile.json` 为准，并请运行 `manage_members.py list` 重新生成本文件。

## 一、基本设定

| 项目 | 内容 |
|------|------|
| 团队名称 | {team_zh}（{profile.get('teamName', {}).get('en', '')}） |
| 主理人 | {profile.get('leadName', '大管家')} |
| 服务对象 | {owner.get('call', '老师')} |
| 研究方向 | {owner.get('field', '')} |
| 交流语言 | {owner.get('language', 'zh')} |
| 工作目录 | `{profile.get('workspace', '')}` |
| 建档时间 | {profile.get('createdAt', '')} |

{('> 补充说明：' + owner.get('note')) if owner.get('note') else ''}

## 二、成员名册

| 名字 | 职业 | 职责 | 归属 | 类型／状态 |
|------|------|------|------|-----------|
{member_table}

> 成员可增可减可改名。内置成员停用后不再参与调度；自定义成员由主理人以角色卡方式驱动。
> 改动统一走 `scripts/manage_members.py`，不要手改 json。

## 三、引用与写作规范（全员适用）

1. **格式**：`（pmid：XXXXXXX）` —— 中文全角括号 + 全角冒号 + 半角数字，写在观点句末，**句号在括号之外**。
2. **颜色**：PMID 标注须为红色字体（RGB `C00000`）。
3. **核验**：任何 PMID 必须先经核验（`pubmed-verifier` 技能，NCBI/Europe PMC 数据源）确认题名、作者、刊名、年份一致；无法核验者一律不引，宁少勿滥。
4. **时效**：优先近 {cit.get('recentYears', 5)} 年文献；奠基性文献可放宽年限，但须注明其为奠基文献。
5. **去 AI 腔**：不用「值得注意的是」「综上所述」「首先／其次／最后」等模板化表达；句长要有起伏，避免全篇等长句。
6. **排版**：{fmt.get('font', '中文宋体 / 西文 Times New Roman')}，正文 {fmt.get('bodySize', '四号')}，标题 {fmt.get('headingSize', '三号加粗')}，{fmt.get('lineSpacing', 1.5)} 倍行距，首行缩进 {fmt.get('firstLineIndent', '2 字符')}，{fmt.get('paper', 'A4')}；参考文献按 {fmt.get('bibliographyStyle', 'GB/T 7714')}。
7. **交付自检**：交付前用脚本统计全文 `（pmid：` 次数，并逐条确认颜色为红色。

## 四、目录约定

根目录只允许 7 项：`README.md`、`团队宪章/`、`.workbuddy/`、`成员/`、`项目/`、`任务/`、`共享/`。禁止在根目录堆放临时脚本或散件。

| 东西 | 放哪 |
|------|------|
| 长期项目 | `项目/<项目名>_<YYYYMMDD>/` |
| 一次性任务过程文件 | `任务/<YYYY-MM>/<MMDD>_<任务名>/` |
| 成员本职产物 | `成员/<成员名>/项目/` |
| 成品与跨成员共用 | `共享/交付/` |
| 自建技能 | `共享/技能库/` |

## 五、团队协作铁律

1. 团队由主理人创建，任何成员不得代建。
2. 专业产出必须由对应成员输出，主理人只做编排与汇编。
3. 跨成员信息流经主理人中转，成员之间不直连。
4. 环境类操作只能由维护师执行，其他人不得擅自安装或升级。
5. 破坏性操作（删除、覆盖配置、批量改权限）动手前必须报备并留回滚方案。
"""


def render_readme(profile: dict) -> str:
    team_zh = profile.get("teamName", {}).get("zh", DEFAULT_TEAM_NAME["zh"])
    owner = profile.get("owner", {})
    enabled = [m for m in profile.get("members", []) if m.get("enabled", True)]
    rows = "\n".join(
        f"| {m.get('name','')} | {m.get('profession','')} | {m.get('duty','')} |"
        for m in enabled
    )
    return f"""# {team_zh}

{owner.get('call', '老师')}的科研工作目录，由「{profile.get('leadName', '大管家')}」按专业把任务分给团队成员完成。

## 成员

| 名字 | 职业 | 职责 |
|------|------|------|
{rows}

## 怎么用

直接用中文把需求说出来即可，不需要记命令。例如：

- 「帮我查近五年地贫铁过载的文献，整理成表」
- 「这个数据帮我做个差异分析并出图」
- 「按照这个思路写一份基金标书的研究背景」

需要调整团队（加人、减人、改名、换工作目录）时，直接说「我要改团队配置」。

## 目录说明

- `团队宪章/` — 团队约定与机器可读的档案（`team-profile.json`）
- `成员/` — 每位成员的产出
- `项目/` — 长期项目
- `任务/` — 一次性任务的过程文件，按月归档
- `共享/` — 成品交付与自建技能

## 注意

- 档案改动请走 `共享/技能库` 之外的管理脚本，不要手改 `team-profile.json`
- 本目录里的 `团队宪章.md` 与 `team-profile.json` 冲突时，以 json 为准
"""


def render_memory(profile: dict) -> str:
    team_zh = profile.get("teamName", {}).get("zh", DEFAULT_TEAM_NAME["zh"])
    return f"""# 项目长期记忆 · {team_zh}

> 逐日流水见 `YYYY-MM-DD.md`；本文件只留跨会话仍然有用的事实与规程。

## 一、基本设定

- 服务对象：{profile.get('owner', {}).get('call', '')}
- 研究方向：{profile.get('owner', {}).get('field', '')}
- 主理人：{profile.get('leadName', '')}
- 工作目录：`{profile.get('workspace', '')}`
- 团队成员与职责见 `团队宪章/团队宪章.md`

## 二、写作与引用规范

- 引用：`（pmid：XXXXXXX）`，红色，句末，句号在括号外，逐条核验
- 去 AI 腔、排版要求见 `团队宪章/团队宪章.md` 第三节

## 三、待补充

（每次完成实质工作后，把有长期价值的事实补到这里；流水写入当日文件）
"""


def render_daily_log(profile: dict) -> str:
    team_zh = profile.get("teamName", {}).get("zh", DEFAULT_TEAM_NAME["zh"])
    return f"""# {now_date()} 工作流水 · {team_zh}

<!-- 追加式记录：做了什么、结论是什么、留了哪些文件。不写临时路径与工具报错。 -->

"""


# ---------------------------------------------------------------- 工作区落地

def ensure_workspace(profile: dict, force: bool = False) -> dict:
    """按档案建目录并写文件。返回 {created:[], skipped:[], profilePath, pointerPath}"""
    ws = Path(profile["workspace"])
    profile_path = ws / "团队宪章" / "team-profile.json"

    created, skipped = [], []

    def mkdir(rel: str):
        p = ws / rel
        if p.exists():
            skipped.append(rel)
        else:
            p.mkdir(parents=True, exist_ok=True)
            created.append(rel)

    ws.mkdir(parents=True, exist_ok=True)
    for rel in SUBDIRS:
        mkdir(rel)

    for m in profile.get("members", []):
        mkdir(f"成员/{m.get('name', '未命名')}/项目")
    mkdir(f"任务/{datetime.now().strftime('%Y-%m')}")

    files = {
        ws / "README.md": render_readme(profile),
        ws / "团队宪章" / "团队宪章.md": render_charter(profile),
        ws / ".workbuddy" / "memory" / "MEMORY.md": render_memory(profile),
        ws / ".workbuddy" / "memory" / f"{now_date()}.md": render_daily_log(profile),
    }
    written, kept = [], []
    for path, text in files.items():
        if path.exists() and not force:
            kept.append(str(path.relative_to(ws)))
            continue
        write_text(path, text)
        written.append(str(path.relative_to(ws)))

    save_json(profile_path, profile)
    ptr = write_pointer(profile)

    return {
        "workspace": str(ws),
        "profilePath": str(profile_path),
        "pointerPath": str(ptr),
        "createdDirs": created,
        "skippedDirs": skipped,
        "writtenFiles": written,
        "keptFiles": kept,
    }


def regenerate_views(profile: dict) -> list:
    """档案改动后重渲染人读版文件。"""
    ws = Path(profile["workspace"])
    profile["updatedAt"] = now_iso()
    save_json(ws / "团队宪章" / "team-profile.json", profile)
    write_text(ws / "团队宪章" / "团队宪章.md", render_charter(profile))
    write_text(ws / "README.md", render_readme(profile))
    write_pointer(profile)
    return [
        str(ws / "团队宪章" / "team-profile.json"),
        str(ws / "团队宪章" / "团队宪章.md"),
        str(ws / "README.md"),
    ]


def active_members(profile: dict) -> list:
    return [m for m in profile.get("members", []) if m.get("enabled", True)]


def brief(profile: dict) -> dict:
    """给主理人注入上下文的精简摘要。"""
    ws = Path(profile.get("workspace", ""))
    return {
        "workspace": str(ws),
        "teamName": profile.get("teamName", {}),
        "leadName": profile.get("leadName", ""),
        "owner": profile.get("owner", {}),
        "preferences": profile.get("preferences", {}),
        "server": profile.get("server", {}),
        "members": [
            {
                "agentId": m.get("agentId"),
                "name": m.get("name"),
                "profession": m.get("profession"),
                "duty": m.get("duty"),
                "builtin": m.get("builtin", False),
                "role": m.get("role", "member"),
            }
            for m in active_members(profile)
        ],
        "disabled": [
            m.get("name") for m in profile.get("members", []) if not m.get("enabled", True)
        ],
        "rootLayout": sorted(
            [p.name for p in ws.iterdir()] if ws.exists() else []
        ),
    }
