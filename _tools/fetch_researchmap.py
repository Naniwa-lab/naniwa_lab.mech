#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
researchmap から業績を取得して data/publications.json を作り直すスクリプト．

使い方（このファイルがあるフォルダの1つ上で実行）：

    python3 _tools/fetch_researchmap.py Naniwa_K

引数は researchmap のマイポータルURLの末尾（permalink）です．
    https://researchmap.jp/Naniwa_K  →  Naniwa_K
    https://researchmap.jp/read0012345 → read0012345

必要なもの：Python 3.7以上だけ．外部ライブラリは不要です．

取得するもの：
  published_papers（論文）と misc（講演・口頭発表など）
  それぞれを journal / intl / domestic / preprint に自動分類します．
  分類がおかしいものは，出来上がった publications.json の "cat" を手で直してください．
"""

import json
import re
import sys
import os
import unicodedata
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubclean import clean_all          # 表記の整形＋手直しの再適用

API = "https://researchmap.jp"
UA = "Mozilla/5.0 (lab-site publication fetcher)"

# 国内学会・研究会と判定するための手がかり
DOMESTIC_HINTS = ["講演会", "講演概要集", "予稿集", "大会", "シンポジウム",
                  "研究会", "コンファレンス", "部門講演会", "学術講演"]
# 会議録ではなく和文ジャーナルと判定するための手がかり
JP_JOURNAL_HINTS = ["論文誌", "学会誌", "Transactions of the Society of Instrument",
                    "Transactions of the JSME", "Nonlinear Theory and Its Applications"]


def get(path, params=None):
    url = "%s/%s" % (API.replace("researchmap.jp", "api.researchmap.jp"), path)
    if params:
        url += "?" + "&".join("%s=%s" % kv for kv in params.items())
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_all(permalink, kind):
    """ページングしながら全件取得する"""
    items, start, total = [], 1, None
    while True:
        d = get("%s/%s" % (permalink, kind), {"limit": 100, "start": start})
        total = d.get("total_items", 0)
        got = d.get("items", [])
        if not got:
            break
        items += got
        start += len(got)
        if len(items) >= total:
            break
    print("  %-18s %d 件" % (kind, len(items)))
    return items


def pick(d, *keys):
    if not isinstance(d, dict):
        return ""
    for k in keys:
        if d.get(k):
            return d[k]
    return ""


def clean(s):
    if not isinstance(s, str):
        return ""
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^\s*\d[A-Z]\d[-–][A-Z0-9]+\s+", "", s)   # 先頭のセッション番号を落とす
    return s.strip()


def authors(a):
    if not isinstance(a, dict):
        return []
    out = []
    for x in (a.get("ja") or a.get("en") or []):
        n = x.get("name", "") if isinstance(x, dict) else str(x)
        n = re.sub(r"\s+", " ", n).strip()
        if n:
            out.append(n)
    return out


def year_of(s):
    m = re.match(r"(\d{4})", str(s or ""))
    return int(m.group(1)) if m else 0


def pages_of(it):
    a = str(it.get("starting_page") or "").strip('" ')
    b = str(it.get("ending_page") or "").strip('" ')
    return "%s–%s" % (a, b) if (a and b and a != b) else a


def categorize(rec, rm_type):
    v = rec["venue"]
    if "bioRxiv" in v or "arXiv" in v:
        return "preprint"
    if rm_type == "scientific_journal":
        return "journal"
    if any(h in v for h in JP_JOURNAL_HINTS):
        return "journal"
    if rm_type == "international_conference_proceedings":
        return "intl"
    if any(h in v for h in DOMESTIC_HINTS):
        return "domestic"
    has_jp = bool(re.search(r"[ぁ-んァ-ヶ一-龥]", v))
    if rec["refereed"] and not has_jp and re.search(r"[A-Za-z]", v):
        return "intl"
    return "domestic" if has_jp else ("intl" if v else "domestic")


def normalize(it):
    t_ja = clean(pick(it.get("paper_title"), "ja"))
    t_en = clean(pick(it.get("paper_title"), "en"))
    ids = it.get("identifiers") or {}
    rec = {
        "cat": "",
        "year": year_of(it.get("publication_date")),
        "title": t_ja or t_en,
        "title_en": t_en if (t_ja and t_en and t_en != t_ja) else "",
        "authors": authors(it.get("authors")),
        "venue": clean(pick(it.get("publication_name"), "ja", "en")),
        "volume": str(it.get("volume") or ""),
        "number": str(it.get("number") or ""),
        "pages": pages_of(it),
        "doi": (ids.get("doi") or [""])[0],
        "refereed": bool(it.get("referee")),
    }
    rec["cat"] = categorize(rec, it.get("published_paper_type") or "")
    return rec


def dedupe(recs):
    seen = {}
    for r in recs:
        key = unicodedata.normalize(
            "NFKC",
            re.sub(r"[\s　\"“”'’,\.\-–—_（）()]+", "", (r["title"] or r["title_en"]).lower()))
        if key not in seen or len(json.dumps(r, ensure_ascii=False)) > len(json.dumps(seen[key], ensure_ascii=False)):
            seen[key] = r
    return list(seen.values())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    permalink = sys.argv[1].rstrip("/").split("/")[-1]

    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    out_path = os.path.join(root, "data", "publications.json")

    print("researchmap から取得中： %s" % permalink)
    try:
        raw = fetch_all(permalink, "published_papers") + fetch_all(permalink, "misc")
    except urllib.error.HTTPError as e:
        print("エラー：researchmap から取得できませんでした（HTTP %s）" % e.code)
        print("permalink が正しいか，researchmap 側で業績が公開設定になっているか確認してください．")
        sys.exit(1)

    recs = dedupe([normalize(it) for it in raw])

    # 表記をそろえ，data/pub_overrides.json の手直しを再適用する
    recs, n_over, unused = clean_all(recs)
    if n_over:
        print("  手直しを %d 件のレコードに再適用しました（data/pub_overrides.json）" % n_over)
    for ov in unused:
        print("  注意：当たらなかった手直しがあります → %s" % json.dumps(ov.get("match"), ensure_ascii=False))

    recs.sort(key=lambda r: (-r["year"], r["title"]))

    if os.path.exists(out_path):
        os.replace(out_path, out_path + ".bak")
        print("既存ファイルを publications.json.bak に退避しました．")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)

    n = {}
    for r in recs:
        n[r["cat"]] = n.get(r["cat"], 0) + 1
    print("\n書き出し完了： data/publications.json（%d 件）" % len(recs))
    for k, label in [("journal", "学術論文"), ("intl", "国際会議"),
                     ("domestic", "国内学会発表"), ("preprint", "プレプリント")]:
        if n.get(k):
            print("  %-12s %d 件" % (label, n[k]))
    print("\n分類が違うものがあれば publications.json の \"cat\" を手で直してください．")


if __name__ == "__main__":
    main()
