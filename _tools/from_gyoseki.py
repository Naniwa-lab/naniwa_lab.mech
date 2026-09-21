#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手元の業績データ（研究業績リスト由来の JSON）から data/publications.json を作り直す．

使い方（このファイルがあるフォルダの1つ上で実行）：

    python3 _tools/from_gyoseki.py ~/Dropbox/浪花業績/業績データ_20260910.json

researchmap から直接取る fetch_researchmap.py と違い，こちらは
**手で整えた業績リスト（Excel）を正**とします．
受賞・特許も含むので，researchmap に未登録のものも載ります．

入力の想定（業績データ_YYYYMMDD.json）：
  records  … 論文・国際会議・国内学会・解説（種別で区別）
  awards   … 受賞
  patents  … 特許

出力する cat：
  journal  査読付学術論文
  intl     国際会議・国際シンポジウム
  domestic 国内学会
  review   解説・学会誌記事
  award    受賞
  patent   特許
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "publications.json"

# 種別（入力） → cat（出力）
def to_cat(kind: str) -> str:
    if kind.startswith("査読付学術論文"):
        return "journal"
    if kind.startswith("国際"):
        return "intl"
    if kind.startswith("国内学会"):
        return "domestic"
    if kind.startswith("解説"):
        return "review"
    return "domestic"


def split_authors(s):
    """著者欄を人名のリストにほぐす．

    入力は表記がかなり揺れている：
      「〇鈴木朱羅（東北大学），中西大輔（松江高専），浪花啓右（北海道科学大学）」
      「中西 大輔（松江高専）渡部 陽也（松江高専）浪花 啓右」   ← 区切り文字なし
      「北海道科学大学\u3000浪花\u3000啓右」                    ← 所属が前置
    """
    if not s:
        return []
    s = s.strip()
    # 先頭の登壇者マーク
    s = re.sub(r"^[○〇◯●\s]+", "", s)
    # 閉じ括弧の直後に区切りが無ければ補う（括弧が事実上の区切りになっている表記）
    s = re.sub(r"([）)])(?=[^\s,，、．;；])", r"\1,", s)
    # 所属の括弧を落とす
    s = re.sub(r"[（(][^（）()]*[）)]", "", s)

    out = []
    for name in re.split(r"[,，、．;；]+", s):
        name = name.replace("\u3000", " ").strip()
        name = re.sub(r"^[○〇◯●\s]+", "", name)
        # 「北海道科学大学 浪花 啓右」のように所属が前置されている場合は落とす
        name = re.sub(r"^\S*(大学|高等専門学校|高専|財団|研究所|機構)\s+", "", name)
        name = re.sub(r"[（）()]", "", name)
        name = re.sub(r"\s{2,}", " ", name).strip()
        if name:
            out.append(name)
    return out


def bare_doi(s):
    if not s:
        return ""
    m = re.search(r"doi\.org/(.+)$", s.strip())
    return m.group(1) if m else ""


def other_url(s):
    if not s or "doi.org" in s:
        return ""
    return s.strip() if s.strip().startswith("http") else ""


def award_year(s):
    m = re.search(r"(\d{4})\s*年", s or "")
    return int(m.group(1)) if m else None


def main():
    if len(sys.argv) < 2:
        sys.exit("使い方: python3 _tools/from_gyoseki.py <業績データ_YYYYMMDD.json>")
    src = Path(sys.argv[1]).expanduser()
    if not src.is_file():
        sys.exit(f"{src} が見つかりません．")

    d = json.loads(src.read_text(encoding="utf-8"))
    pubs = []

    for r in d.get("records", []):
        pubs.append({
            "cat": to_cat(r.get("種別", "")),
            "year": r.get("年"),
            "title": (r.get("題目") or "").strip(),
            "title_en": "",
            "authors": split_authors(r.get("著者")),
            "venue": (r.get("掲載誌・会議名") or "").strip(),
            "ref": (r.get("巻号ページ / 講演番号") or "").strip(),
            "doi": bare_doi(r.get("DOI / URL")),
            "url": other_url(r.get("DOI / URL")),
            "refereed": r.get("査読") == "有",
            "note": "",
            "gid": r.get("業績ID") or "",
        })

    for a in d.get("awards", []):
        pubs.append({
            "cat": "award",
            "year": award_year(a.get("受賞年月")),
            "title": (a.get("賞名") or "").strip(),
            "title_en": "",
            "authors": split_authors(a.get("受賞者")),
            "venue": (a.get("授与団体") or "").strip(),
            "ref": (a.get("受賞年月") or "").strip(),
            "doi": "",
            "url": "",
            "refereed": False,
            "note": (a.get("対象業績") or "").strip(),
            "gid": a.get("業績ID") or "",
        })

    for p in d.get("patents", []):
        pubs.append({
            "cat": "patent",
            "year": None,
            "title": (p.get("名称") or "").strip(),
            "title_en": "",
            "authors": split_authors(p.get("発明者")),
            "venue": (p.get("種別") or "").strip(),
            "ref": (p.get("番号") or "").strip(),
            "doi": "",
            "url": "",
            "refereed": False,
            "note": "",
            "gid": "",
        })

    order = {"journal": 0, "intl": 1, "domestic": 2, "review": 3, "award": 4, "patent": 5}
    pubs.sort(key=lambda p: (-(p["year"] or 0), order.get(p["cat"], 9), p["title"]))

    OUT.write_text(json.dumps(pubs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    n = {}
    for p in pubs:
        n[p["cat"]] = n.get(p["cat"], 0) + 1
    print(f"  {src.name} から {len(pubs)} 件を書き出しました → {OUT.relative_to(ROOT)}")
    for k in ["journal", "intl", "domestic", "review", "award", "patent"]:
        print(f"    {k:9s} {n.get(k, 0)}")
    miss = [p["title"][:40] for p in pubs if not p["title"]]
    if miss:
        print(f"  ※ 題目が空のレコードが {len(miss)} 件あります")


if __name__ == "__main__":
    main()
