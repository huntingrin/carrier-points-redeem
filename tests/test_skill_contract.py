#!/usr/bin/env python3
"""Offline contract checks for the integration layer.

These checks protect the two things that are easy to break by accident:
1. every documented path still exists after a doc edit;
2. the normal path stays small (no carrier silently grows a third required file).

No network, no browser, no writes outside a temp dir.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# 正常路径的阅读预算：每家最多两篇，合计不超过 155 行。
HOT_PATH = {
    "移动": ["skills/cmcc-points-redeem/GUIDE.md"],
    "联通": [
        "skills/cucc-points-redeem/GUIDE.md",
        "skills/cucc-points-redeem/references/redemption-types.md",
    ],
    "电信": [
        "skills/ct-points-redeem/GUIDE.md",
        "skills/ct-points-redeem/references/phonefee.md",
    ],
}
HOT_PATH_LINE_BUDGET = 155
ENTRY_LINE_BUDGET = 150

# 文档里的示例号码；真实号码一律脱敏，不能出现 11 位明文。
EXAMPLE_NUMBERS = {"13800138000", "13900139000", "13900000000"}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MOBILE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")


def markdown_files():
    return sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)


class DocLinks(unittest.TestCase):
    def test_every_relative_link_resolves(self):
        broken = []
        for path in markdown_files():
            for target in LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                if not (path.parent / target).exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [], "以下相对链接指向不存在的文件:\n" + "\n".join(broken))

    def test_paths_quoted_in_entry_exist(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        quoted = set(re.findall(r"`(skills/[^`]+?\.md)`", entry))
        self.assertTrue(quoted, "入口没有列出任何子技能路径")
        missing = sorted(q for q in quoted if not (ROOT / q).exists())
        self.assertEqual(missing, [], f"入口引用了不存在的路径: {missing}")


class ReadPath(unittest.TestCase):
    def test_hot_path_files_exist(self):
        missing = [f for files in HOT_PATH.values() for f in files if not (ROOT / f).exists()]
        self.assertEqual(missing, [])

    def test_hot_path_stays_small(self):
        details = {}
        for carrier, files in HOT_PATH.items():
            lines = sum(len((ROOT / f).read_text(encoding="utf-8").splitlines()) for f in files)
            details[carrier] = (len(files), lines)
            self.assertLessEqual(lines, HOT_PATH_LINE_BUDGET, f"{carrier} 的正常路径超预算: {details[carrier]}")
            self.assertLessEqual(len(files), 2, f"{carrier} 的正常路径超过两篇")

    def test_entry_stays_small(self):
        lines = len((ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(lines, ENTRY_LINE_BUDGET, "入口文件过长，会把固定成本推高")

    def test_read_list_keeps_failure_docs_out_of_normal_path(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        start = entry.index("## 三、路由与最小阅读清单")
        section = entry[start : entry.index("\n## ", start + 4)]
        rows = [line for line in section.splitlines() if line.startswith("|") and "GUIDE.md" in line]
        self.assertEqual(len(rows), 3, "阅读清单应恰好覆盖三家")
        for row in rows:
            cells = [c.strip() for c in row.split("|")]
            normal = cells[2] if len(cells) > 2 else ""
            self.assertIn("GUIDE.md", normal)
            for failure_doc in ("browser-flow.md", "transaction-state.md"):
                self.assertNotIn(failure_doc, normal, f"{failure_doc} 不应出现在必读列")


class SkillShape(unittest.TestCase):
    def test_subskills_do_not_expose_skill_md(self):
        exposed = [str(p.relative_to(ROOT)) for p in (ROOT / "skills").glob("*/SKILL.md")]
        self.assertEqual(exposed, [], "子技能会单独出现在宿主技能列表里")

    def test_frontmatter_present(self):
        for name in ("SKILL.md", "skills/cmcc-points-redeem/GUIDE.md",
                     "skills/cucc-points-redeem/GUIDE.md", "skills/ct-points-redeem/GUIDE.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), f"{name} 缺少 frontmatter")
            self.assertIn("name:", text[:400])
            self.assertIn("description:", text[:600])

    def test_install_bundle_includes_references(self):
        script = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn('"$SCRIPT_DIR/references"', script, "install.sh 未拷贝 references/，安装后会缺文件")

    def test_reference_docs_are_linked_from_entry(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in ("references/observe.md", "references/browser.md"):
            self.assertIn(name, entry, f"入口没有指向 {name}")


class FirstRun(unittest.TestCase):
    def test_entry_does_not_force_a_browser(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("不要要求安装或切换浏览器", "先查登录态", "不要问\"你用哪个浏览器\""):
            self.assertIn(phrase, entry, f"入口缺少首次使用约束: {phrase}")

    def test_browser_doc_keeps_capability_ladder(self):
        text = (ROOT / "references/browser.md").read_text(encoding="utf-8")
        for phrase in ("T1", "T2", "T3", "xdg-open", "不要", "Cookie"):
            self.assertIn(phrase, text, f"浏览器文档缺少: {phrase}")

    def test_login_entry_is_not_hand_built(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("不要手工拼登录 URL", entry)
        text = (ROOT / "references/browser.md").read_text(encoding="utf-8")
        for phrase in ("让站点带你过去", "goBack", "已经是登录页就直接交接"):
            self.assertIn(phrase, text, f"浏览器文档缺少登录入口约束: {phrase}")

    def test_readme_documents_manual_install(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("手动安装", text)
        self.assertIn("Windows", text)


class SafetyInvariants(unittest.TestCase):
    def test_entry_keeps_core_rules(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "请告诉我你的运营商和手机号",
            "不要用号段推断运营商",
            "不索取聊天中的验证码",
            "现金补款必须为 0",
            "不重复提交",
            "10010",
        ):
            self.assertIn(phrase, entry, f"入口缺少关键约束: {phrase}")

    def test_guides_keep_account_and_cash_rules(self):
        for path in (ROOT / "skills").glob("*/GUIDE.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in ("本机", "现金", "验证码"):
                self.assertIn(phrase, text, f"{path.name} 缺少关键约束: {phrase}")

    def test_no_unmasked_mobile_numbers(self):
        found = []
        for path in markdown_files():
            for number in MOBILE.findall(path.read_text(encoding="utf-8")):
                if number not in EXAMPLE_NUMBERS:
                    found.append(f"{path.relative_to(ROOT)}: {number[:3]}****{number[-2:]}")
        self.assertEqual(found, [], "文档中出现未脱敏号码")


class StateScriptsStillWork(unittest.TestCase):
    def test_subskill_state_tests_pass(self):
        for name in ("ct-points-redeem", "cucc-points-redeem"):
            directory = ROOT / "skills" / name
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_transaction_state.py"],
                cwd=directory, capture_output=True, text=True,
            )
            self.assertEqual(
                completed.returncode, 0,
                f"{name} 的状态脚本测试失败:\n{completed.stdout}\n{completed.stderr}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
