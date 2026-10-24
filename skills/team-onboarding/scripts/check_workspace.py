# -*- coding: utf-8 -*-
"""
check_workspace.py — 工作区体检。首次建档后、或怀疑配置被改坏时跑一次。

用法：
    python check_workspace.py

检查项：
  1. 指针与档案是否一致、档案路径是否可达
  2. 档案必填字段是否齐全
  3. 根目录是否只剩约定项目（多出来的会列出来，不自动删）
  4. 启用成员是否都有 成员/<名字>/项目 目录
  5. 记忆文件是否存在
退出码：0 全通过；1 有严重问题；2 只有警告。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_profile as L  # noqa: E402

REQUIRED = ["schemaVersion", "plugin", "teamName", "leadName", "workspace", "owner", "preferences", "members"]


def main() -> int:
    L.safe_stdout()
    problems, warns, oks = [], [], []

    profile, source = L.find_profile()
    if profile is None:
        print(f"❌ 未找到团队档案：{source}")
        print("   下一步：按 team-onboarding 的首次引导流程建档")
        return 1
    oks.append(f"档案定位成功（{source}）")

    for key in REQUIRED:
        if key not in profile:
            problems.append(f"档案缺少字段：{key}")
    if not problems:
        oks.append("必填字段齐全")

    ws = Path(profile.get("workspace", ""))
    if not ws.exists():
        problems.append(f"工作目录不存在：{ws}")
        print(json.dumps({"ok": False, "problems": problems, "warnings": warns}, ensure_ascii=False, indent=2))
        return 1
    oks.append(f"工作目录可达：{ws}")

    extra = sorted(p.name for p in ws.iterdir() if p.name not in L.ROOT_ITEMS)
    if extra:
        warns.append("根目录出现约定之外的条目（请归档到 任务/ 或 共享/）：" + "、".join(extra))
    else:
        oks.append("根目录结构符合约定")

    for rel in ("团队宪章", ".workbuddy/memory", "共享/交付", "项目", "任务"):
        if not (ws / rel).exists():
            problems.append(f"缺少目录：{rel}")

    for m in L.active_members(profile):
        d = ws / "成员" / m.get("name", "")
        if not d.exists():
            warns.append(f"成员目录缺失：成员/{m.get('name')}（可手动创建或说一声让主理人补）")

    if (ws / ".workbuddy" / "memory" / "MEMORY.md").exists():
        oks.append("长期记忆文件存在")
    else:
        warns.append("缺少 .workbuddy/memory/MEMORY.md")

    ptr = L.pointer_path()
    if ptr.exists():
        oks.append(f"全局指针存在：{ptr}")
    else:
        warns.append("全局指针不存在，其他会话可能定位不到工作区（重跑 init 或 manage_members 可重建）")

    print(json.dumps(
        {"ok": not problems, "ok_items": oks, "problems": problems, "warnings": warns},
        ensure_ascii=False, indent=2,
    ))
    if problems:
        return 1
    return 2 if warns else 0


if __name__ == "__main__":
    raise SystemExit(main())
