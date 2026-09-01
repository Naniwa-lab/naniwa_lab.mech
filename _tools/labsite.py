#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow"]
# ///
"""
研究室HP 更新ツール

ニュースの追加，写真の登録，メンバーの更新，データの検査を
コマンド1本でできるようにしたものです．

使い方（uv がある場合．Pillow を自動で用意してくれます）:

    uv run _tools/labsite.py news add --title "○○が受賞しました" --cat award
    uv run _tools/labsite.py photo add ~/Desktop/naniwa.jpg --as naniwa.jpg
    uv run _tools/labsite.py member photo images/naniwa.jpg
    uv run _tools/labsite.py student add --grade B4 --name "山田 太郎" --theme "不整地走破性の評価"
    uv run _tools/labsite.py check

uv が無い場合は `python3 _tools/labsite.py ...` でも動きます
（写真の縮小だけ Pillow が必要．無ければそのままコピーします）．
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IMAGES = ROOT / "images"

NEWS_CATS = {"paper": "論文", "award": "受賞", "event": "イベント", "lab": "研究室"}
PUB_CATS = {"journal", "intl", "domestic", "preprint"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


# ---------------------------------------------------------------- 入出力

def load(name: str):
    path = DATA / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"{path} が見つかりません．")
    except json.JSONDecodeError as e:
        die(f"{path} の JSON が壊れています（{e.lineno}行目付近）: {e.msg}")


def save(name: str, obj) -> None:
    path = DATA / name
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"  → {path.relative_to(ROOT)} を更新しました")


def die(msg: str) -> "None":
    print(f"エラー: {msg}", file=sys.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------------- news

def cmd_news_add(a) -> None:
    d = a.date or date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        die(f"日付は YYYY-MM-DD の形式で指定してください（受け取った値: {d}）")
    if a.cat not in NEWS_CATS:
        die(f"cat は {' / '.join(NEWS_CATS)} のいずれかです（受け取った値: {a.cat}）")

    news = load("news.json")
    item = {"date": d, "cat": a.cat, "title": a.title, "sub": a.sub or "", "url": a.url or ""}
    news.append(item)
    news.sort(key=lambda n: n.get("date", ""), reverse=True)
    save("news.json", news)
    print(f"  追加: {d} [{NEWS_CATS[a.cat]}] {a.title}")


def cmd_news_list(a) -> None:
    news = load("news.json")
    for i, n in enumerate(news):
        label = NEWS_CATS.get(n.get("cat", ""), n.get("cat", "?"))
        print(f"[{i:2}] {n.get('date','????-??-??')}  {label:4}  {n.get('title','')}")
    print(f"\n計 {len(news)} 件")


def cmd_news_rm(a) -> None:
    news = load("news.json")
    if not 0 <= a.index < len(news):
        die(f"番号は 0〜{len(news)-1} の範囲で指定してください（`news list` で確認できます）")
    removed = news.pop(a.index)
    save("news.json", news)
    print(f"  削除: {removed.get('date')} {removed.get('title')}")


# ---------------------------------------------------------------- photo

def cmd_photo_add(a) -> None:
    src = Path(a.file).expanduser()
    if not src.is_file():
        die(f"{src} が見つかりません．")

    name = a.as_name or src.name
    if Path(name).suffix.lower() not in IMAGE_SUFFIXES:
        die(f"画像の拡張子が想定外です: {name}")
    IMAGES.mkdir(exist_ok=True)
    dest = IMAGES / name

    if dest.exists() and not a.force:
        die(f"{dest.relative_to(ROOT)} は既にあります．上書きするなら --force を付けてください．")

    try:
        from PIL import Image, ImageOps
    except ImportError:
        shutil.copy2(src, dest)
        print(f"  Pillow が無いのでそのままコピーしました → {dest.relative_to(ROOT)}")
        print("  （縮小したい場合は `uv run` で実行してください）")
        return

    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)          # スマホ写真の向きを補正
        before = im.size
        if max(im.size) > a.max_side:
            im.thumbnail((a.max_side, a.max_side), Image.LANCZOS)
        if dest.suffix.lower() in {".jpg", ".jpeg"}:
            im = im.convert("RGB")
            im.save(dest, "JPEG", quality=a.quality, optimize=True, progressive=True)
        else:
            im.save(dest, optimize=True)
        after = im.size

    kb_in, kb_out = src.stat().st_size / 1024, dest.stat().st_size / 1024
    print(f"  {before[0]}x{before[1]} ({kb_in:.0f}KB) → {after[0]}x{after[1]} ({kb_out:.0f}KB)")
    print(f"  → {dest.relative_to(ROOT)}")
    print(f"  HTML/JSON からは \"images/{name}\" として参照できます")


def cmd_photo_list(a) -> None:
    if not IMAGES.exists():
        print("images/ がありません．")
        return
    files = sorted(p for p in IMAGES.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    if not files:
        print("images/ は空です．")
        return
    for p in files:
        print(f"  images/{p.name}  ({p.stat().st_size/1024:.0f}KB)")


# ---------------------------------------------------------------- member

def cmd_member_photo(a) -> None:
    members = load("members.json")
    faculty = members.get("faculty") or []
    if not faculty:
        die("members.json に faculty がありません．")

    target = faculty[0]
    if a.name:
        hits = [m for m in faculty if a.name in m.get("name", "")]
        if not hits:
            die(f"faculty に「{a.name}」が見当たりません．")
        target = hits[0]

    rel = a.path
    if not (IMAGES / Path(rel).name).is_file():
        die(f"{rel} が images/ にありません．先に `photo add` で登録してください．")
    target["photo"] = f"images/{Path(rel).name}"
    save("members.json", members)
    print(f"  {target.get('name')} の写真を {target['photo']} にしました")


def cmd_student_add(a) -> None:
    members = load("members.json")
    students = members.setdefault("students", [])
    # 「（準備中）」のプレースホルダが同学年にあれば置き換える
    for s in students:
        if s.get("grade") == a.grade and "準備中" in s.get("name", ""):
            s["name"], s["theme"] = a.name, a.theme or ""
            save("members.json", members)
            print(f"  {a.grade} の「（準備中）」枠を {a.name} に置き換えました")
            return
    students.append({"grade": a.grade, "name": a.name, "theme": a.theme or ""})
    save("members.json", members)
    print(f"  追加: {a.grade} {a.name}")


def cmd_student_clear(a) -> None:
    members = load("members.json")
    members["students"] = []
    save("members.json", members)
    print("  students を空にしました（サイト上は「準備中です．」と表示されます）")


# ---------------------------------------------------------------- check

def cmd_pubs_clean(a) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pubclean import clean_all

    pubs = load("publications.json")
    cleaned, n_over, unused = clean_all(pubs)

    changed = [(i, [k for k in b if pubs[i].get(k) != b.get(k)])
               for i, b in enumerate(cleaned) if pubs[i] != b]

    for ov in unused:
        print(f"  注意：当たらなかった手直しがあります → "
              f"{json.dumps(ov.get('match'), ensure_ascii=False)}")
    if n_over:
        print(f"  手直しを {n_over} 件のレコードに再適用しました")

    if not changed:
        print("  整形の必要はありませんでした．")
        return

    print(f"\n  {len(changed)} 件を整形します：")
    for i, keys in changed[: a.show]:
        print(f"   [{i}] {cleaned[i].get('title','')[:44]}")
        for k in keys:
            print(f"       {k}: {pubs[i].get(k)!r}")
            print(f"       {' ' * len(k)}→ {cleaned[i].get(k)!r}")
    if len(changed) > a.show:
        print(f"   … ほか {len(changed) - a.show} 件（--show で表示数を変えられます）")

    if a.dry_run:
        print("\n  --dry-run なので書き込んでいません．")
        return
    save("publications.json", cleaned)


def cmd_check(a) -> None:
    problems: list[str] = []
    notes: list[str] = []

    # --- site.json
    site = load("site.json")
    for key in ("lab", "univ", "dept", "email"):
        if not site.get(key):
            problems.append(f"site.json: 「{key}」が空です")

    # --- news.json
    news = load("news.json")
    for i, n in enumerate(news):
        where = f"news.json[{i}]"
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", n.get("date", "")):
            problems.append(f"{where}: date が YYYY-MM-DD ではありません（{n.get('date')!r}）")
        if n.get("cat") not in NEWS_CATS:
            problems.append(f"{where}: cat が不正です（{n.get('cat')!r}）")
        if not n.get("title"):
            problems.append(f"{where}: title が空です")
        if n.get("url") and not str(n["url"]).startswith(("http://", "https://")):
            problems.append(f"{where}: url が http(s) で始まっていません")
    if news != sorted(news, key=lambda n: n.get("date", ""), reverse=True):
        notes.append("news.json が日付降順に並んでいません（表示は自動でソートされるので実害はありません）")

    # --- members.json
    members = load("members.json")
    for group in ("faculty", "students", "alumni"):
        if not isinstance(members.get(group, []), list):
            problems.append(f"members.json: 「{group}」がリストではありません")
    for i, m in enumerate(members.get("faculty", [])):
        photo = m.get("photo") or ""
        if photo and not (ROOT / photo).is_file():
            problems.append(f"members.json faculty[{i}]: 写真 {photo} が見つかりません")
        if not photo:
            notes.append(f"members.json faculty[{i}] ({m.get('name')}): 写真が未設定です")
    placeholders = [s for s in members.get("students", []) if "準備中" in s.get("name", "")]
    if placeholders:
        notes.append(f"members.json: 学生が「（準備中）」のままの枠が {len(placeholders)} 件あります")

    # --- publications.json
    pubs = load("publications.json")
    counts = {c: 0 for c in PUB_CATS}
    for i, p in enumerate(pubs):
        if p.get("cat") not in PUB_CATS:
            problems.append(f"publications.json[{i}]: cat が不正です（{p.get('cat')!r}）")
        else:
            counts[p["cat"]] += 1
        if not isinstance(p.get("year"), int):
            problems.append(f"publications.json[{i}]: year が整数ではありません（{p.get('year')!r}）")
        if not p.get("title"):
            problems.append(f"publications.json[{i}]: title が空です")

    # --- ファイルの存在
    for required in (".nojekyll", "index.html", "assets/style.css", "assets/site.js"):
        if not (ROOT / required).exists():
            problems.append(f"{required} がありません")
    if not (ROOT / "favicon.ico").exists() and not (ROOT / "favicon.svg").exists():
        notes.append("favicon が未設置です")

    # --- 報告
    print("── データ ──")
    print(f"  お知らせ    {len(news)} 件")
    print(f"  教員        {len(members.get('faculty', []))} 名 / 学生 {len(members.get('students', []))} 名")
    print(f"  業績        {len(pubs)} 件"
          f"（ジャーナル {counts['journal']} / 国際会議 {counts['intl']} /"
          f" 国内 {counts['domestic']} / preprint {counts['preprint']}）")

    if notes:
        print("\n── 気になる点 ──")
        for n in notes:
            print(f"  ・{n}")

    if problems:
        print("\n── 直すべき点 ──")
        for p in problems:
            print(f"  × {p}")
        raise SystemExit(1)

    print("\n問題は見つかりませんでした．")


# ---------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="labsite", description="研究室HPの更新ツール")
    sub = ap.add_subparsers(dest="group", required=True)

    # news
    news = sub.add_parser("news", help="お知らせ").add_subparsers(dest="cmd", required=True)
    n_add = news.add_parser("add", help="お知らせを追加")
    n_add.add_argument("--title", required=True, help="見出し")
    n_add.add_argument("--cat", default="lab", help=f"種類（{' / '.join(NEWS_CATS)}．既定 lab）")
    n_add.add_argument("--date", help="YYYY-MM-DD（既定は今日）")
    n_add.add_argument("--sub", help="補足の一文")
    n_add.add_argument("--url", help="リンク先URL")
    n_add.set_defaults(func=cmd_news_add)
    news.add_parser("list", help="一覧を番号付きで表示").set_defaults(func=cmd_news_list)
    n_rm = news.add_parser("rm", help="番号を指定して削除")
    n_rm.add_argument("index", type=int)
    n_rm.set_defaults(func=cmd_news_rm)

    # photo
    photo = sub.add_parser("photo", help="写真").add_subparsers(dest="cmd", required=True)
    p_add = photo.add_parser("add", help="写真を縮小して images/ に登録")
    p_add.add_argument("file", help="元の画像ファイル")
    p_add.add_argument("--as", dest="as_name", help="保存名（既定は元のファイル名）")
    p_add.add_argument("--max-side", type=int, default=1600, dest="max_side", help="長辺の上限px（既定1600）")
    p_add.add_argument("--quality", type=int, default=82, help="JPEG品質（既定82）")
    p_add.add_argument("--force", action="store_true", help="既存ファイルを上書き")
    p_add.set_defaults(func=cmd_photo_add)
    photo.add_parser("list", help="images/ の一覧").set_defaults(func=cmd_photo_list)

    # member
    member = sub.add_parser("member", help="教員").add_subparsers(dest="cmd", required=True)
    m_ph = member.add_parser("photo", help="教員の顔写真を設定")
    m_ph.add_argument("path", help="images/xxx.jpg")
    m_ph.add_argument("--name", help="対象の氏名の一部（省略時は先頭の教員）")
    m_ph.set_defaults(func=cmd_member_photo)

    # student
    student = sub.add_parser("student", help="学生").add_subparsers(dest="cmd", required=True)
    s_add = student.add_parser("add", help="学生を追加（同学年の「（準備中）」枠があれば置換）")
    s_add.add_argument("--grade", required=True, help="M2 / M1 / B4 など")
    s_add.add_argument("--name", required=True)
    s_add.add_argument("--theme", help="研究テーマ")
    s_add.set_defaults(func=cmd_student_add)
    student.add_parser("clear", help="学生を全て消す").set_defaults(func=cmd_student_clear)

    # pubs
    pubs = sub.add_parser("pubs", help="業績データ").add_subparsers(dest="cmd", required=True)
    pb_c = pubs.add_parser("clean", help="表記をそろえ，pub_overrides.json の手直しを再適用")
    pb_c.add_argument("--dry-run", action="store_true", help="書き込まずに差分だけ見る")
    pb_c.add_argument("--show", type=int, default=10, help="表示する件数（既定10）")
    pb_c.set_defaults(func=cmd_pubs_clean)

    # check
    sub.add_parser("check", help="データの整合性を検査").set_defaults(func=cmd_check)

    return ap


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
