#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publications.json の表記ゆれをそろえ，手直しを再取得後も維持するための処理．

`fetch_researchmap.py`（取得時）と `labsite.py pubs clean`（既存ファイルの手直し）が
このモジュールを共有するので，どちらを通しても同じ結果になる．

## なぜ必要か

2026-08-27 に researchmap から再取得したとき，それ以前に手で直していた
誌名・ページ番号・タイトルが生データで上書きされてしまった．
「取得 → 自動整形 → 手直しの再適用」の3段にして，同じことが起きないようにする．

## やっていること

1. 引用符をASCIIにそろえる（“ ” ‘ ’ ′′ ″ → " '）
2. ページ番号のゴミを落とす
     1P1–G10(1)"-"1P1-G10(3)  →  1P1-G10
     _2P2-K05_1–_2P2-K05_2    →  2P2-K05
     1A1–E10                  →  1A1-E10
   数字だけのページ範囲（47–57）は学術表記としてEnダッシュのまま残す
3. 巻・号の "0" → 空文字（researchmapが号なしを0で返すことがある）
4. 総大文字の英文会議名 → 見出し語だけ大文字
5. `data/pub_overrides.json` の手直しを最後に上書き適用
"""

from __future__ import annotations

import json
import re
from pathlib import Path

OVERRIDES_PATH = Path(__file__).resolve().parent.parent / "data" / "pub_overrides.json"

# ---------------------------------------------------------------- 1. 引用符

_QUOTE_MAP = {
    "“": '"', "”": '"',      # “ ”
    "‘": "'", "’": "'",      # ‘ ’
    "〝": '"', "〞": '"',      # 〝 〞
    "″": '"',                     # ″
}


def clean_text(s) -> str:
    """引用符をASCIIにそろえ，前後・連続の空白を整える．"""
    if not isinstance(s, str):
        return ""
    s = s.replace("′′", '"')      # ′′（プライム2つ）を先に処理
    for a, b in _QUOTE_MAP.items():
        s = s.replace(a, b)
    return re.sub(r"[ \t　]+", " ", s).strip()


# ---------------------------------------------------------------- 2. ページ

# 講演会のセッション番号（1P1-G10, 2A1-A04, 1A1-E10 など）
_SESSION = re.compile(r"\d[A-Z]\d-[A-Z]\d{2,}")
# 数字だけのページ範囲
_NUM_RANGE = re.compile(r"^(\d+)\s*[–—-]\s*(\d+)$")


def _session_from(side: str) -> str:
    """`_2P2-K05_1` や `1P1–G10(1)` のような断片からセッション番号を取り出す．"""
    s = re.sub(r"\(\d+\)", "", side)                    # 枝番 (1) を落とす
    s = s.replace("–", "-").replace("—", "-")  # – — → -
    candidates = [p for p in re.split(r"_+", s) if p]
    for c in candidates + [s]:
        c = c.strip().replace(" ", "")
        m = _SESSION.fullmatch(c)
        if m:
            return c
    return s.strip("_ -")


def clean_pages(s) -> str:
    """ページ欄のゴミを落とす．数字のページ範囲はEnダッシュのまま残す．"""
    if not isinstance(s, str):
        return ""
    s = clean_text(s).strip('" ')
    if not s:
        return ""

    marked = s.replace('"-"', "|")

    # 区切り記号を含まない単体の値
    if "|" not in marked and "_" not in marked:
        plain = marked.replace("–", "-").replace("—", "-").replace(" ", "")
        if _SESSION.fullmatch(plain):
            return plain                                # 1A1–E10 → 1A1-E10
        if _NUM_RANGE.match(marked):
            return marked                               # 47–57 はそのまま
        return marked

    # 範囲表記になっているもの
    if "|" in marked:
        sides = marked.split("|")
    else:
        sides = re.split(r"[–—]", marked)

    reduced = [_session_from(p) for p in sides if p.strip(" _-")]
    reduced = [r for r in reduced if r]
    if not reduced:
        return ""
    if all(r == reduced[0] for r in reduced):
        return reduced[0]                               # 同じ番号の重複 → 1つに
    return reduced[0]


# ---------------------------------------------------------------- 3. 巻・号

def clean_number(s) -> str:
    """号・巻が 0 や空相当なら空文字にする．"""
    s = "" if s is None else str(s)
    s = s.strip()
    return "" if s in ("0", "00", "-", "—") else s


# ---------------------------------------------------------------- 4. 会議名

_ACRONYMS = {
    "IEEE", "RSJ", "IROS", "ICRA", "JSME", "SICE", "SI", "AI", "IEICE", "SII",
    "ROBOMECH", "DARS", "CLAWAR", "AMAM", "IFAC", "ASME", "USA", "UK",
    "CD-ROM", "DVD", "LNCS", "EMG", "PAM", "CPG",
}
_STOPWORDS = {
    "of", "on", "and", "the", "in", "for", "to", "a", "an", "at", "by",
    "with", "from", "its", "into", "as",
}


def clean_venue(s) -> str:
    """総大文字の英文会議名だけ見出し語を大文字にする．それ以外は触らない．"""
    s = clean_text(s)
    if not s:
        return ""

    letters = [c for c in s if c.isalpha()]
    if not letters:
        return s
    if sum(c.isascii() for c in letters) < len(letters) * 0.9:
        return s                                        # 和文混在は触らない
    if sum(c.isupper() for c in letters) / len(letters) < 0.8:
        return s                                        # もともと総大文字でない
    words = s.split()
    if len(words) < 4:
        return s                                        # 短い略称は触らない

    out = []
    for i, w in enumerate(words):
        core = w.strip("(),.:;")
        if not core:
            out.append(w)
        elif core.upper() in _ACRONYMS or "/" in core or any(ch.isdigit() for ch in core):
            out.append(w)
        elif i > 0 and core.lower() in _STOPWORDS:
            out.append(w.replace(core, core.lower()))
        else:
            out.append(w.replace(core, core.capitalize()))
    return " ".join(out)


# ---------------------------------------------------------------- 5. 手直し

def load_overrides(path: Path | None = None) -> list:
    """data/pub_overrides.json を読む．無ければ空リスト．"""
    p = path or OVERRIDES_PATH
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"エラー: {p} の JSON が壊れています（{e.lineno}行目付近）: {e.msg}")
    return data.get("overrides", []) if isinstance(data, dict) else data


def _matches(rec: dict, match: dict) -> bool:
    for k, v in match.items():
        if k == "title_contains":
            if v not in (rec.get("title") or ""):
                return False
        elif (rec.get(k) or "") != v:
            return False
    return True


def apply_overrides(recs: list, overrides: list | None = None) -> tuple:
    """手直しを適用し，(結果, 当たった件数, 当たらなかったルール) を返す．"""
    ovs = load_overrides() if overrides is None else overrides
    hits, unused = 0, []
    out = [dict(r) for r in recs]
    for ov in ovs:
        match, setter = ov.get("match") or {}, ov.get("set") or {}
        if not match or not setter:
            continue
        matched = False
        for r in out:
            if _matches(r, match):
                r.update(setter)
                matched, hits = True, hits + 1
        if not matched:
            unused.append(ov)
    return out, hits, unused


# ---------------------------------------------------------------- まとめ

def clean_record(rec: dict) -> dict:
    """1件分の自動整形．元の dict は書き換えない．"""
    r = dict(rec)
    for key in ("title", "title_en"):
        if key in r:
            r[key] = clean_text(r.get(key))
    if "venue" in r:
        r["venue"] = clean_venue(r.get("venue"))
    if "pages" in r:
        r["pages"] = clean_pages(r.get("pages"))
    for key in ("number", "volume"):
        if key in r:
            r[key] = clean_number(r.get(key))
    return r


def clean_all(recs: list) -> tuple:
    """自動整形 → 手直しの再適用．(結果, 当たった件数, 当たらなかったルール)"""
    return apply_overrides([clean_record(r) for r in recs])
