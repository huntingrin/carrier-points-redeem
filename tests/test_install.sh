#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/carrier-points-redeem-test.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_file() {
  [ -f "$1" ] || fail "缺少文件: $1"
}

echo "1. 首次安装"
bash "$ROOT/install.sh" --target "$TMP/skills" >/dev/null
DEST="$TMP/skills/carrier-points-redeem"
assert_file "$DEST/SKILL.md"
assert_file "$DEST/skills/cmcc-points-redeem/GUIDE.md"
assert_file "$DEST/skills/cucc-points-redeem/GUIDE.md"
assert_file "$DEST/skills/ct-points-redeem/GUIDE.md"
[ ! -e "$DEST/skills/cmcc-points-redeem/SKILL.md" ] || fail "子技能不应暴露 SKILL.md"
[ ! -e "$DEST/skills/cucc-points-redeem/SKILL.md" ] || fail "子技能不应暴露 SKILL.md"
[ ! -e "$DEST/skills/ct-points-redeem/SKILL.md" ] || fail "子技能不应暴露 SKILL.md"
assert_file "$DEST/skills/ct-points-redeem/scripts/transaction_state.py"
assert_file "$DEST/skills/cucc-points-redeem/references/browser-flow.md"
assert_file "$DEST/references/observe.md"
assert_file "$DEST/tests/test_skill_contract.py"
[ ! -d "$DEST/.git" ] || fail "不应包含 .git"

echo "2. 重复安装会整体替换"
touch "$DEST/stale-file"
bash "$ROOT/install.sh" --target "$TMP/skills" >/dev/null
[ ! -e "$DEST/stale-file" ] || fail "旧文件未被清理"
assert_file "$DEST/SKILL.md"

echo "3. 三个子技能名称与入口路由表一致"
for name in cmcc-points-redeem cucc-points-redeem ct-points-redeem; do
  grep -q "skills/$name/GUIDE.md" "$DEST/SKILL.md" || fail "入口未指向 $name"
done
grep -q "请告诉我你的运营商和手机号" "$DEST/SKILL.md" || fail "缺少单问入口"
grep -q "不要用号段推断运营商" "$DEST/SKILL.md" || fail "缺少禁止号段推断规则"
grep -q "话费（短信方法）" "$DEST/skills/cucc-points-redeem/GUIDE.md" || fail "联通话费分支未显式展示"
grep -q "10010" "$DEST/skills/cucc-points-redeem/GUIDE.md" || fail "联通话费缺少 10010 说明"
grep -q "话费" "$DEST/skills/cucc-points-redeem/agents/openai.yaml" || fail "联通展示信息缺少话费"
grep -q "10010" "$DEST/SKILL.md" || fail "入口范围缺少联通话费"
grep -q "references/observe.md" "$DEST/SKILL.md" || fail "入口缺少一屏一读模板引用"

echo "4. 归档旧独立版本（可选开关）"
mkdir -p "$TMP/skills/cmcc-points-redeem" "$TMP/skills/ct-points-redeem"
touch "$TMP/skills/cmcc-points-redeem/marker"
bash "$ROOT/install.sh" --target "$TMP/skills" --archive-standalone >/dev/null
[ ! -e "$TMP/skills/cmcc-points-redeem" ] || fail "旧独立版本未归档"
[ ! -e "$TMP/skills/ct-points-redeem" ] || fail "旧独立版本未归档"
ARCHIVED="$(find "$TMP/skills" -path '*/.carrier-points-redeem-archive-*/cmcc-points-redeem/marker' -print -quit)"
[ -n "$ARCHIVED" ] || fail "归档目录中缺少 marker"
assert_file "$DEST/SKILL.md"

echo "5. 卸载"
bash "$ROOT/uninstall.sh" --target "$TMP/skills" >/dev/null
[ ! -e "$DEST" ] || fail "卸载后目录仍存在"

echo "PASS"
