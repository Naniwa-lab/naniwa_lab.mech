#!/usr/bin/env bash
# データを検査してから GitHub に反映する．
#
#   ./_tools/deploy.sh "お知らせを1件追加"
#
# 引数を省略すると「サイト更新」というコミットメッセージになります．
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .git ]; then
  echo "エラー: このフォルダは git リポジトリではありません．" >&2
  echo "  git clone https://github.com/jignoah/naniwa_lab.mech.git" >&2
  exit 1
fi

echo "── データを検査します ──"
if command -v uv >/dev/null 2>&1; then
  uv run _tools/labsite.py check
else
  python3 _tools/labsite.py check
fi

echo
echo "── 変更点 ──"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "  変更はありません．"
  exit 0
fi
git status --short

echo
git add -A
git commit -m "${1:-サイト更新}"
git push

echo
echo "反映しました．1〜2分で https://jignoah.github.io/naniwa_lab.mech/ に出ます．"
