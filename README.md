# フィールドロコモーション研究室（浪花研）Webサイト

北海道科学大学 工学部 機械工学科 浪花研究室の公式サイトです．
ビルド不要の静的サイトなので，GitHub Pages にそのまま置けば公開できます．

**公開URL**: <https://jignoah.github.io/naniwa_lab.mech/>
**リポジトリ**: <https://github.com/jignoah/naniwa_lab.mech>

> 公開はすでに済んでいます．普段の更新は **§2.5 のコマンド** が一番早いです．
> §1 は初回セットアップの記録として残してあります．

---

## 1. 公開のしかた（初回だけ・記録用）

### ステップ1：リポジトリを作る

1. [github.com](https://github.com) にログイン（アカウントがなければ作成）
2. 右上の **＋** → **New repository**
3. 設定する項目
   - **Repository name**：`naniwa-lab`（好きな名前でOK）
   - **Public** を選択（Pages を無料で使うために必要）
   - Add a README file は **チェックしない**
4. **Create repository**

### ステップ2：ファイルを上げる

作られたリポジトリの画面で **uploading an existing file** をクリックし，
このフォルダの中身を **フォルダごとドラッグ＆ドロップ** します．

上げるもの：

```
index.html  research.html  members.html  publications.html
news.html   join.html      access.html
assets/     data/          images/       .nojekyll
```

`_tools/` と `README.md` は上げても上げなくても動きます．

下の **Commit changes** ボタンを押せばアップロード完了です．

> ⚠️ `.nojekyll` は「ファイル名がドットで始まる」ためドラッグでは上がらないことがあります．
> 上がらなかった場合は **Add file → Create new file** でファイル名に `.nojekyll` と入れ，
> 中身は空のまま Commit すればOKです．

### ステップ3：Pages を有効にする

1. リポジトリの **Settings** タブ
2. 左メニューの **Pages**
3. Source を **Deploy from a branch**
4. Branch を **main** ／ フォルダを **/ (root)** にして **Save**
5. 1〜2分待つと，画面上部に公開URLが出ます

```
https://<GitHubのユーザー名>.github.io/naniwa-lab/
```

これで公開完了です．

---

## 2. 更新のしかた（ここが本番）

**ほとんどの更新は `data/` の中の JSON ファイルを書き換えるだけ**で済みます．
GitHubのWeb画面上で直接編集できるので，PCに何もインストールする必要はありません．

編集手順：
リポジトリでファイルを開く → 右上の **鉛筆マーク（Edit）** → 書き換える → 下の **Commit changes**
→ 1分ほどでサイトに反映されます．

### 研究室名・所属・連絡先を変える → `data/site.json`

ここを直すと，**全ページのヘッダ・フッタが一括で変わります**．

```json
{
 "lab": "フィールドロコモーション研究室",
 "univ": "北海道科学大学",
 "dept": "工学部 機械工学科",
 "address": "北海道札幌市手稲区前田7条15丁目4-1",
 "email": "naniwa-k [at] hus.ac.jp"
}
```

（ブラウザのタブに出るタイトルだけは各HTMLの `<title>` にあります）

### お知らせを追加する → `data/news.json`

いちばん上に，カンマ区切りで追記します．

```json
[
 {
  "date": "2026-10-15",
  "cat": "award",
  "title": "○○くんが△△講演会で優秀講演賞を受賞しました",
  "sub": "補足があれば書く．なければ空文字 \"\" でOK．",
  "url": "https://example.com/リンク先（なければ空文字）"
 },
 ...以下，既存の項目...
]
```

`cat` に指定できるのは4種類（色分けされます）：

| 値 | 表示 |
|---|---|
| `paper` | 論文 |
| `award` | 受賞 |
| `event` | イベント |
| `lab` | 研究室 |

> **JSONの注意点**：項目と項目の間には必ず `,` が要ります．
> ただし **最後の項目のうしろには `,` を付けない**でください．ここだけ間違えやすいです．

### メンバーを更新する → `data/members.json`

- `faculty`：教員．`photo` に `"images/naniwa.jpg"` のように書けば顔写真が出ます
  （`images/` フォルダに画像を上げてから）．空文字なら「写真を準備中です」と表示されます．
- `students`：学生．`grade`（M2 / B4 など），`name`，`theme`（研究テーマ）を書きます．
- `alumni`：卒業生．使うときは `students` と同じ形式で書いてください．

### 業績を更新する → `data/publications.json`

現在，researchmap から取得した **104件** が入っています．

```json
{
 "cat": "journal",
 "year": 2026,
 "title": "論文タイトル",
 "title_en": "英語タイトル（なければ空文字）",
 "authors": ["浪花 啓右", "共著者名"],
 "venue": "掲載誌名・学会名",
 "volume": "12", "number": "3", "pages": "45–56",
 "doi": "10.1234/xxxx",
 "refereed": true
}
```

`cat` は `journal`（学術論文） / `intl`（国際会議） / `domestic`（国内学会） / `preprint` のいずれか．
著者名を `"浪花 啓右"` と書くと，サイト上で自動的に太字になります．

**researchmap を更新したあと，一括で入れ直せます．**
手元のPCでこのフォルダに移動して，以下を実行してください．

```bash
python3 _tools/fetch_researchmap.py Naniwa_K
```

researchmap から論文・講演を全件取得し，カテゴリを自動判定して
`data/publications.json` を作り直します（元のファイルは `.bak` として残ります）．
あとはそのファイルを GitHub に上げ直すだけです．
分類がおかしいものがあれば `"cat"` を手で直してください．

### 本文を書き換えたい（研究内容・配属ページなど）

`research.html` や `join.html` を直接編集してください．
HTMLですが，日本語の文章部分を書き換えるだけなら難しくありません．
`<p>ここが本文</p>` の「ここが本文」を差し替えるイメージです．

### 色やデザインを変えたい

`assets/style.css` の先頭にある `:root { ... }` の色コードを変えると，サイト全体に反映されます．

```css
--accent:   #14556e;   /* メインの色（濃い青緑） */
--earth:    #a8621f;   /* 差し色（土っぽいオレンジ） */
--bg-deep:  #10222e;   /* トップのヒーロー背景 */
```

---

## 2.5 コマンドでまとめて更新する（おすすめ）

`_tools/labsite.py` を使うと，JSONを手で開かずに更新できます．
書式ミスやカンマの付け忘れが起きないので，こちらのほうが安全です．

`uv` が入っていれば必要なライブラリを勝手に用意してくれます．

```bash
cd ~/Dropbox/研究室HP/lab-site
```

### お知らせを追加する

```bash
uv run _tools/labsite.py news add \
  --title "○○くんが△△講演会で優秀講演賞を受賞しました" \
  --cat award \
  --sub "補足があれば．なくてもOK" \
  --url "https://example.com"
```

`--cat` は `paper`（論文）/ `award`（受賞）/ `event`（イベント）/ `lab`（研究室）．
`--date` を省くと今日の日付になります．追加後は自動で日付降順に並びます．

```bash
uv run _tools/labsite.py news list      # 番号付きで一覧
uv run _tools/labsite.py news rm 3      # 3番を削除
```

### 写真を追加する

長辺1600pxに縮小し，スマホ写真の向きも直したうえで `images/` に入れます．

```bash
uv run _tools/labsite.py photo add ~/Desktop/IMG_1234.jpg --as naniwa.jpg
uv run _tools/labsite.py member photo images/naniwa.jpg   # 教員の顔写真に設定
uv run _tools/labsite.py photo list
```

### 学生を追加する

同じ学年に「（準備中）」の枠があれば，そこに入ります．

```bash
uv run _tools/labsite.py student add --grade B4 --name "山田 太郎" --theme "不整地走破性の評価"
uv run _tools/labsite.py student clear   # 全部消す
```

### 公開前に検査する

JSONの書式，カテゴリの綴り，参照している画像の有無などをまとめて確認します．

```bash
uv run _tools/labsite.py check
```

### GitHubに反映する

検査 → コミット → push をまとめて行います．

```bash
./_tools/deploy.sh "お知らせを1件追加"
```

1〜2分で公開サイトに反映されます．

> このフォルダが git リポジトリになっていない場合は，先に一度だけ
> `git clone https://github.com/jignoah/naniwa_lab.mech.git` した中で作業してください．

---

## 3. ファイル構成

```
index.html          トップページ
research.html       研究内容
members.html        メンバー
publications.html   業績（絞り込み・検索つき）
news.html           お知らせ一覧
join.html           配属を考えている方へ（Q&Aつき）
access.html         アクセス・お問い合わせ

assets/
  style.css         共通スタイル
  site.js           メニュー・News・メンバーの描画
  publications.js   業績の絞り込みと検索

data/
  site.json         研究室名・所属・連絡先（ヘッダ／フッタに反映）
  news.json         お知らせ      ← よく触る
  members.json      メンバー      ← よく触る
  publications.json 業績（104件） ← たまに触る

images/             写真置き場（現在は空）
_tools/
  labsite.py             お知らせ・写真・メンバーの更新ツール ← よく使う
  deploy.sh              検査してGitHubへ反映
  fetch_researchmap.py   researchmapから業績を取り直すスクリプト
  build.py               HTMLを生成した内部スクリプト（通常は使いません）
.gitignore          .DS_Store や *.bak をコミットしないための設定
.nojekyll           GitHub Pagesで必要（消さないこと）
```

> `_tools/build.py` は初回にHTMLを組み立てたスクリプトです．
> **HTMLを直接編集したあとにこれを実行すると，その編集が上書きされます**ので，
> 基本的には触らないでください．

---

## 4. 手元で確認したいとき

このフォルダで以下を実行し，ブラウザで `http://localhost:8000` を開きます．

```bash
python3 -m http.server 8000
```

（`file://` で直接開くと JSON の読み込みがブラウザにブロックされ，
お知らせや業績が表示されません．必ずこの方法で確認してください．）

---

## 5. 独自ドメインを使いたい場合

`example.com` のような独自ドメインを当てることもできます．
リポジトリ直下に `CNAME` というファイルを作ってドメイン名を1行書き，
DNS側で GitHub Pages 向けのレコードを設定します．
必要になったら手順を用意します．
