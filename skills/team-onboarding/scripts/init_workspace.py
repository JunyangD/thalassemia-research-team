# -*- coding: utf-8 -*-
"""
init_workspace.py — 按引导问答的结果，在用户指定路径建立工作区。

用法：
    python init_workspace.py --input payload.json [--force]

payload.json 至少包含 workspace 字段，其余缺项用默认值补齐。示例：
{
  "workspace": "D:/科研/地贫科研团队",
  "teamName": {"zh": "地贫科研团队", "en": "Thalassemia Research Team"},
  "leadName": "大管家",
  "owner": {"call": "老师", "field": "地中海贫血", "language": "zh"},
  "members": null
}

退出码：0 成功；2 已存在档案且未加 --force；1 参数或执行错误。
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_profile as L  # noqa: E402


def main() -> int:
    L.safe_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="引导结果 JSON 文件路径")
    ap.add_argument("--force", action="store_true", help="已存在档案时覆盖（会先备份）")
    args = ap.parse_args()

    payload_path = Path(args.input).expanduser()
    if not payload_path.exists():
        print(json.dumps({"ok": False, "error": f"输入文件不存在：{payload_path}"}, ensure_ascii=False))
        return 1

    payload = L.load_json(payload_path)
    if not payload.get("workspace"):
        print(json.dumps({"ok": False, "error": "payload 缺少 workspace 字段"}, ensure_ascii=False))
        return 1

    profile = L.build_profile(payload)
    ws = Path(profile["workspace"])
    profile_path = ws / "团队宪章" / "team-profile.json"

    backup = None
    if profile_path.exists():
        if not args.force:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "code": 2,
                        "error": "该目录已存在团队档案，未做任何改动",
                        "profilePath": str(profile_path),
                        "hint": "如需读取现有配置用 read_profile.py；如需重建请加 --force（会先备份）",
                    },
                    ensure_ascii=False,
                )
            )
            return 2
        backup = L.backup_file(profile_path)

    result = L.ensure_workspace(profile, force=args.force)
    result["ok"] = True
    result["backup"] = backup
    result["memberNames"] = [m.get("name") for m in L.active_members(profile)]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
