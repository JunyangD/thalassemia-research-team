# -*- coding: utf-8 -*-
"""
read_profile.py — 定位团队档案并输出精简摘要，供主理人每轮启动时注入上下文。

用法：
    python read_profile.py            # 输出 JSON 摘要
    python read_profile.py --raw      # 输出完整档案

查找顺序：全局指针 → 常见候选目录（当前目录 / 文档 / 用户目录 / 桌面）。
输出 found=false 表示尚未建档，主理人应转入首次引导流程。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_profile as L  # noqa: E402


def main() -> int:
    L.safe_stdout()
    raw = "--raw" in sys.argv
    profile, source = L.find_profile()

    if profile is None:
        print(
            json.dumps(
                {
                    "found": False,
                    "source": source,
                    "pointerPath": str(L.pointer_path()),
                    "hint": "尚未建档，请按 team-onboarding 的首次引导流程向用户提问后再建目录",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if raw:
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        return 0

    data = L.brief(profile)
    data["found"] = True
    data["source"] = source
    data["profilePath"] = str(Path(profile.get("workspace", "")) / "团队宪章" / "team-profile.json")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
