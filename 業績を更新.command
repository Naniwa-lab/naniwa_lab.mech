#!/usr/bin/env bash
# ダブルクリックで実行できる「業績更新ボタン」．
#
#   ~/Dropbox/浪花業績/ の一番新しい 業績データ_YYYYMMDD.json を読んで
#   サイトの業績ページを作り直し，GitHub に反映します．
#
# ターミナルからは  ./業績を更新.command  でも同じです．
set -euo pipefail
cd "$(dirname "$0")"

echo "───────────────────────────────"
echo " 研究室HP 業績更新"
echo "───────────────────────────────"
echo

python3 _tools/from_gyoseki.py
echo

./_tools/deploy.sh "業績を更新"

echo
echo "https://naniwa-lab.github.io/naniwa_lab.mech/publications.html"
echo "（反映まで1〜2分かかります）"
echo
read -n 1 -s -r -p "何かキーを押すと閉じます．"
echo
