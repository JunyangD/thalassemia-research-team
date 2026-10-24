# -*- coding: utf-8 -*-
"""
manage_members.py — 团队成员与基本设定的增删改。

用法：
    python manage_members.py list
    python manage_members.py add    --name 统计师 --profession 生物统计师 --duty "样本量与检验效能计算"
    python manage_members.py add    --name 统计师 --profession 生物统计师 --duty "..." --scope "统计支持"
    python manage_members.py disable --id data-engineer
    python manage_members.py enable  --id data-engineer
    python manage_members.py remove  --id custom-statistician
    python manage_members.py rename  --id science-illustrator --name 美工
    python manage_members.py set-lead --name 总管
    python manage_members.py set-team --name "血液病科研团队"
    python manage_members.py set-owner --call 主任 --field "骨髓衰竭性疾病"
    python manage_members.py set-server --enabled --host 192.168.1.10 --user lab --shared-root /data/shared --private-root /home/lab

内置成员（builtin=true）不可真正删除，remove 会自动降级为 disable，避免调度表指向不存在的 agent。
每次改动后自动重渲染 团队宪章.md / README.md 并更新全局指针。
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_profile as L  # noqa: E402


def fail(msg: str) -> int:
    print(msg)
    return 1


def main() -> int:
    L.safe_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "action",
        choices=[
            "list", "add", "disable", "enable", "remove", "rename",
            "set-lead", "set-team", "set-owner", "set-server",
        ],
    )
    ap.add_argument("--id")
    ap.add_argument("--name")
    ap.add_argument("--profession")
    ap.add_argument("--duty")
    ap.add_argument("--scope")
    ap.add_argument("--call")
    ap.add_argument("--field")
    ap.add_argument("--enabled", action="store_true")
    ap.add_argument("--host")
    ap.add_argument("--user")
    ap.add_argument("--shared-root")
    ap.add_argument("--private-root")
    args = ap.parse_args()

    profile, source = L.find_profile()
    if profile is None:
        return fail(f"未找到团队档案（{source}）。请先完成首次引导建档。")

    members = profile.setdefault("members", [])
    lead = next((m for m in members if m.get("role") == "lead"), None)

    if args.action == "list":
        print(f"档案：{source}")
        print(f"团队：{profile.get('teamName', {}).get('zh')}｜工作区：{profile.get('workspace')}")
        for m in members:
            mark = "启用" if m.get("enabled", True) else "停用"
            kind = "内置" if m.get("builtin") else "自定义"
            print(f"  [{'主理人' if m.get('role')=='lead' else kind+'/'+mark}] {m.get('agentId')}  {m.get('name')}（{m.get('profession')}）")
        return 0

    if args.action == "add":
        if not args.name or not args.profession:
            return fail("add 需要 --name 与 --profession")
        if any(m.get("name") == args.name for m in members):
            return fail(f"已存在同名成员：{args.name}")
        agent_id = "custom-" + (L.slugify(args.name) or f"m{len(members)}")
        members.append(
            {
                "agentId": agent_id,
                "name": args.name,
                "profession": args.profession,
                "duty": args.duty or f"{args.profession}相关专业工作",
                "scope": args.scope or "自定义",
                "builtin": False,
                "enabled": True,
                "role": "member",
            }
        )
        Path(profile["workspace"], "成员", args.name, "项目").mkdir(parents=True, exist_ok=True)
        print(f"已新增成员：{args.name}（{agent_id}）")

    elif args.action in ("disable", "enable"):
        target = next((m for m in members if m.get("agentId") == args.id), None)
        if target is None:
            return fail(f"未找到成员：{args.id}")
        if target.get("role") == "lead":
            return fail("主理人不可停用；如需换人请用 set-lead 改名字")
        target["enabled"] = args.action == "enable"
        print(f"{target.get('name')} → {'启用' if target['enabled'] else '停用'}")

    elif args.action == "remove":
        target = next((m for m in members if m.get("agentId") == args.id), None)
        if target is None:
            return fail(f"未找到成员：{args.id}")
        if target.get("role") == "lead":
            return fail("主理人不可删除")
        if target.get("builtin"):
            target["enabled"] = False
            print(f"{target.get('name')} 是内置成员，已改为停用（不删除文件），仍可随时 enable")
        else:
            members.remove(target)
            print(f"已移除自定义成员：{target.get('name')}（其历史文件保留在 成员/ 下）")

    elif args.action == "rename":
        target = next((m for m in members if m.get("agentId") == args.id), None)
        if target is None:
            return fail(f"未找到成员：{args.id}")
        if not args.name:
            return fail("rename 需要 --name")
        old = target.get("name")
        target["name"] = args.name
        newdir = Path(profile["workspace"], "成员", args.name, "项目")
        newdir.mkdir(parents=True, exist_ok=True)
        print(f"{old} → {args.name}（旧目录保留，未自动搬迁历史文件）")

    elif args.action == "set-lead":
        if not args.name:
            return fail("set-lead 需要 --name")
        profile["leadName"] = args.name
        if lead:
            lead["name"] = args.name
        else:
            members.insert(0, dict(L.DEFAULT_MEMBERS[0], name=args.name))
        Path(profile["workspace"], "成员", args.name, "项目").mkdir(parents=True, exist_ok=True)
        print(f"主理人称呼 → {args.name}")

    elif args.action == "set-team":
        if not args.name:
            return fail("set-team 需要 --name")
        profile.setdefault("teamName", {})
        profile["teamName"]["zh"] = args.name
        print(f"团队名 → {args.name}（英文名如需改，请直接编辑 team-profile.json 的 teamName.en）")

    elif args.action == "set-owner":
        owner = profile.setdefault("owner", {})
        if args.call:
            owner["call"] = args.call
        if args.field:
            owner["field"] = args.field
        print(f"服务对象 → {owner.get('call')}｜研究方向 → {owner.get('field')}")

    elif args.action == "set-server":
        server = profile.setdefault("server", {})
        server["enabled"] = bool(args.enabled)
        for key, val in (
            ("host", args.host), ("user", args.user),
            ("sharedRoot", args.shared_root), ("privateRoot", args.private_root),
        ):
            if val:
                server[key] = val
        print(f"服务器配置 → enabled={server.get('enabled')} host={server.get('host','')}")

    touched = L.regenerate_views(profile)
    for t in touched:
        print(f"  已更新 {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
