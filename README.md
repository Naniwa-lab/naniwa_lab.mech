# フィールドロコモーション研究室 ウェブサイト

公開URL: <https://naniwa-lab.github.io/naniwa_lab.mech/>

ビルド不要の静的サイトです．`data/*.json` を書き換えて push すれば反映されます．

---

## よくやる作業

### ★ 業績を更新する

**`業績を更新.command` をダブルクリックするだけ．**

`~/Dropbox/浪花業績/` の一番新しい `業績データ_YYYYMMDD.json` を自動で探して
業績ページを作り直し，GitHub に反映します．

ターミナル派の人は同じことが次のコマンドでできます：

```bash
cd ~/Dropbox/研究室HP/lab-site
./業績を更新.command
```

業績データそのもの（Excel／JSON）の作り方は `~/Dropbox/浪花業績/` 側の話です．
このリポジトリは出来上がった JSON を読むだけです．

### お知らせを追加する

```bash
./_tools/labsite.py news add --title "◯◯で発表しました" --cat event
./_tools/deploy.sh "お知らせを追加"
```

`--cat` は `paper` / `award` / `event` / `lab` のいずれか．

### 学生を追加する

```bash
./_tools/labsite.py student add --grade B4 --name "山田 太郎" --theme "不整地走破性の評価"
./_tools/deploy.sh "学生を追加"
```

**メンバーの人数が変わったら `members.html` 冒頭の説明文も手で直してください**
（「教員1名と学生19名（M2 2名・…）で活動しています．」の行）．

### 写真を追加する

```bash
./_tools/labsite.py photo add ~/Desktop/robot.jpg --as robot.jpg   # 縮小・向き補正して images/ へ
./_tools/labsite.py member photo images/naniwa.jpg                 # 教員の顔写真に設定
```

### とりあえず確認だけしたい

```bash
./_tools/labsite.py check      # データの検査（push はしない）
python3 -m http.server 8000    # → http://localhost:8000 で表示確認
```

`file://` で直接開くと JSON が読めずお知らせ・業績が出ません．必ずサーバー経由で．

---

## ファイルの地図

| 場所 | 中身 |
|---|---|
| `index.html` ほか7ページ | 本体．ヘッダ・フッタは `data/site.json` から流し込み |
| `assets/style.css` | 色は先頭の `:root` の変数でまとめて変えられます |
| `assets/site.js` | メニュー・お知らせ・メンバー・業績サマリの描画 |
| `assets/publications.js` | 業績ページの絞り込みと検索 |
| `data/publications.json` | **自動生成．手で編集しないこと**（`業績を更新.command` が作ります） |
| `data/news.json` `members.json` `site.json` | ここは手で，または `labsite.py` で編集 |
| `_tools/` | 更新用のスクリプト群 |
| `.nojekyll` | GitHub Pages 用．消さないこと |

`_tools/fetch_researchmap.py` `_tools/pubclean.py` `data/pub_overrides.json` は
researchmap から直接業績を取っていた頃の名残で，**いまは使っていません**．

---

## 困ったとき

- **push できない（403）** … `~/Dropbox/研究室HP/github-token.md` のトークンが切れています．
  GitHub → Settings → Developer settings → Fine-grained tokens で
  **Resource owner を `Naniwa-lab`**，対象は このリポジトリ，権限 Contents: Read and write で
  作り直して，ファイルの中身を差し替えてください．（現行トークンの期限：2027-09-22）
- **サイトに反映されない** … GitHub Pages の反映に1〜2分かかります．
  ブラウザのキャッシュも疑って，URL の末尾に `?v=2` などを付けて再読込を．
- **業績の件数がおかしい** … `./_tools/labsite.py check` が内訳を出します．
