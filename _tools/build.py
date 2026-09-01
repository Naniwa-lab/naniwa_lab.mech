# -*- coding: utf-8 -*-
"""
静的HTMLの生成スクリプト（内部用）．
ヘッダ・フッタを共通化してページを書き出します．
※ 公開後にHTMLを直接編集した場合，このスクリプトを再実行すると上書きされます．
"""
import os, io

SITE_JA = "フィールドロコモーション研究室"
SITE_SUB = "北海道科学大学 工学部 機械工学科 浪花研究室"
SITE_EN = "Field Locomotion Lab"
DESC = "北海道科学大学 工学部 機械工学科 フィールドロコモーション研究室（浪花研）の公式サイト．生物のロコモーション解析，空気圧人工筋などのソフトアクチュエータ，不整地を走破する移動ロボットの研究を行っています．"

NAV = [
    ("index.html", "ホーム"),
    ("research.html", "研究内容"),
    ("members.html", "メンバー"),
    ("publications.html", "業績"),
    ("news.html", "お知らせ"),
    ("join.html", "配属を考えている方へ"),
    ("access.html", "アクセス"),
]

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site} | {sub}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap header-inner">
    <div class="brand">
      <a href="index.html">
        <span class="brand-ja" data-site="lab">{site}</span>
        <span class="brand-en" data-site="labEn">{en}</span>
      </a>
    </div>
    <button class="nav-toggle" aria-expanded="false" aria-label="メニュー">MENU</button>
    <nav class="nav">
{navitems}
    </nav>
  </div>
</header>
"""

FOOT = """
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-lab"><span data-site="lab">{site}</span></p>
        <p class="footer-addr">
          <span data-site="univ">北海道科学大学</span> <span data-site="dept">工学部 機械工学科</span><br>
          <span data-site="zip">〒006-8585</span> <span data-site="address">北海道札幌市手稲区前田7条15丁目4-1</span><br>
          E-mail：<span data-site="email">naniwa-k [at] hus.ac.jp</span>
        </p>
      </div>
      <div>
        <h4>サイト内</h4>
        <ul>
          <li><a href="research.html">研究内容</a></li>
          <li><a href="members.html">メンバー</a></li>
          <li><a href="publications.html">業績</a></li>
          <li><a href="news.html">お知らせ</a></li>
        </ul>
      </div>
      <div>
        <h4>外部リンク</h4>
        <ul>
          <li><a href="https://www.hus.ac.jp/" data-site-href="univUrl" target="_blank" rel="noopener"><span data-site="univ">北海道科学大学</span></a></li>
        </ul>
        <ul data-site-links>
          <li><a href="https://researchmap.jp/Naniwa_K" target="_blank" rel="noopener">researchmap</a></li>
          <li><a href="https://orcid.org/0000-0003-3171-958X" target="_blank" rel="noopener">ORCID</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-site="lab">{site}</span> / <span data-site="pi">Keisuke Naniwa</span></span>
      <span data-site="labEn">{en}</span>
    </div>
  </div>
</footer>

<script src="assets/site.js"></script>
{extra}
</body>
</html>
"""


def page(fname, title, body, extra=""):
    nav = "\n".join(
        '      <a href="{}"{}>{}</a>'.format(
            href, ' aria-current="page"' if href == fname else "", label
        )
        for href, label in NAV
    )
    head = HEAD.format(
        title=title, desc=DESC, site=SITE_JA, sub=SITE_SUB, en=SITE_EN, navitems=nav
    )
    foot = FOOT.format(site=SITE_JA, en=SITE_EN, extra=extra)
    out = head + body + foot
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    with io.open(os.path.join(root, fname), "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", fname, len(out), "bytes")


def head_block(eyebrow, h1, lead="", narrow=True):
    return """
<div class="page-head">
  <div class="wrap{n}">
    <span class="eyebrow">{e}</span>
    <h1>{h}</h1>
    {p}
  </div>
</div>
""".format(n=(" narrow" if narrow else ""), e=eyebrow, h=h1,
           p=("<p>%s</p>" % lead) if lead else "")


# ============================================================ index
INDEX = """
<section class="hero">
  <div class="wrap">
    <p class="hero-eyebrow">Hokkaido University of Science &middot; Dept. of Mechanical Engineering</p>
    <h1>生きものの動きを解きほぐし，<br>フィールドを走るロボットをつくる．</h1>
    <p class="hero-en">FIELD LOCOMOTION LAB &nbsp;/&nbsp; NANIWA LABORATORY</p>
    <p class="lead">
      昆虫は脳で一歩ずつ足を制御しているわけではありません．脚のかたち，筋のやわらかさ，
      地面からの反力——身体と環境の相互作用そのものが，すでに「計算」をしています．
      私たちはその仕組みを実験と数理モデルで解きほぐし，同じ原理で
      整地されていない現実の場所（フィールド）を動きまわるロボットへと翻訳しています．
    </p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="research.html">研究内容を見る</a>
      <a class="btn btn-ghost" href="join.html">配属を考えている方へ</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Research</span>
      <h2>4つの柱で「動き」に迫る</h2>
      <p>生物の運動解析からアクチュエータ開発，フィールドでの走破性評価まで．
         解析だけ・ものづくりだけに閉じないのが，この研究室のやり方です．</p>
    </div>
    <div class="grid grid-2">
      <div class="card">
        <div class="num">01</div>
        <h3>生きものの歩き方を解剖する</h3>
        <p>コオロギ，バッタ，ムカデ，カニ——さまざまな生物の歩行を計測し，
           脚と脚がどう協調しているのかを解析します．神経系がやっている仕事と，
           身体そのものがやっている仕事を切り分けるのが狙いです．</p>
        <div class="tags">
          <span class="tag">歩容解析</span><span class="tag">脚間協調</span>
          <span class="tag">位相振動子モデル</span><span class="tag">神経生理</span>
        </div>
      </div>
      <div class="card">
        <div class="num">02</div>
        <h3>やわらかいアクチュエータをつくる</h3>
        <p>McKibben型空気圧人工筋を軸に，安価で丈夫な人工筋 LT-PAM，
           張力センサを内蔵した筋，さらには電気を一切使わない空圧論理回路まで．
           「柔らかさ」そのものが制御を肩代わりする世界を狙っています．</p>
        <div class="tags">
          <span class="tag">空気圧人工筋</span><span class="tag">ソフトロボティクス</span>
          <span class="tag">拮抗二関節筋</span><span class="tag">電気レス空圧回路</span>
        </div>
      </div>
      <div class="card">
        <div class="num">03</div>
        <h3>フィールドを走破する移動ロボット</h3>
        <p>実験室の平らな床ではなく，土・瓦礫・斜面といった現実の地形で動くこと．
           地形を空間周波数で捉えて走破性を定量評価する手法や，
           水陸両用の多脚ロボット，災害対応を想定したモジュール型ロボットを扱っています．</p>
        <div class="tags">
          <span class="tag tag-earth">不整地移動</span><span class="tag tag-earth">走破性評価</span>
          <span class="tag tag-earth">災害対応ロボット</span><span class="tag tag-earth">多脚ロボット</span>
        </div>
      </div>
      <div class="card">
        <div class="num">04</div>
        <h3>脳がなくても歩けるのか</h3>
        <p>“Brainless Walking”——弱いアクチュエータを並べるだけで，
           動物らしい歩容が勝手に立ち上がる．身体に埋め込まれた制御（陰的制御）と，
           それを束ねる群のふるまいを，理論と実機の両側から追いかけています．</p>
        <div class="tags">
          <span class="tag">陰的制御</span><span class="tag">身体性</span>
          <span class="tag">群ロボット</span><span class="tag">自律分散</span>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Publications</span>
      <h2>研究のかたち</h2>
    </div>
    <div class="stats" data-pubstats></div>
    <p class="small muted" style="margin-top:14px">
      researchmap 掲載の業績をもとにしています．
      <a href="publications.html">業績一覧はこちら</a>
    </p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">News</span>
      <h2>お知らせ</h2>
    </div>
    <div data-news="5"></div>
    <p style="margin-top:28px"><a class="btn btn-line" href="news.html">お知らせをすべて見る</a></p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap narrow center">
    <div class="section-head" style="margin-bottom:20px">
      <span class="eyebrow">Join us</span>
      <h2>いっしょに動くものをつくりませんか</h2>
      <p style="margin-left:auto;margin-right:auto">
        機械・電気・プログラミング・生物，どこから入ってきても大丈夫です．
        研究室見学はいつでも歓迎します．
      </p>
    </div>
    <a class="btn btn-solid" href="join.html">配属を考えている方へ</a>
  </div>
</section>
"""

# ============================================================ research
RESEARCH = head_block("Research", "研究内容",
    "「なぜ生きものはあんなに上手く動けるのか」．この問いを，計測・数理モデル・実機製作の三方向から攻めています．") + """
<section class="section">
  <div class="wrap narrow prose">

    <h2>研究室のスタンス</h2>
    <p>
      ロボットを賢くする方法は，ふつう「もっと良いコントローラを書く」ことだと考えられています．
      でも生きものを見ていると，どうもそうではないらしい．
      昆虫の脳はとても小さく，一本一本の脚をリアルタイムに指令している余裕はありません．
      にもかかわらず，彼らは砂の上でも草の茂みでも壁でも，あっさり歩いてしまいます．
    </p>
    <p>
      つまり，かしこさの一部は<strong>身体の側に埋め込まれている</strong>．
      脚のかたち，筋のやわらかさ，地面から返ってくる力——
      これらの相互作用が，コントローラの代わりに仕事をしている．
      この「身体がやっている計算」を取り出して理解し，
      ロボットの設計へ持ち帰るのが，私たちのやり方です．
    </p>
    <p>
      そのため研究テーマは，虫の歩行計測から人工筋の試作，
      不整地でロボットを走らせる実験まで，かなり幅があります．
      解析だけでも，ものづくりだけでも足りない，というのが正直なところです．
    </p>

    <h2>01 &nbsp;生きものの歩き方を解剖する</h2>
    <p>
      コオロギ，バッタ，ムカデ，カニといった多脚の生きものを対象に，
      高速度カメラやモーションキャプチャで歩行を計測し，脚間の協調がどう生まれるかを解析します．
    </p>
    <h3>具体的にやっていること</h3>
    <ul>
      <li>コオロギ（<i>Gryllus bimaculatus</i>）の脚間協調メカニズムの解析．神経節どうしの上行・下行信号がリズムの維持にどう効いているかを，実験と位相振動子モデルの両面から検討しています．</li>
      <li>バッタが水平面・垂直面・天井面を歩くときの歩容の違いの解析．重力方向が変わると脚の役割分担がどう組み替わるのか．</li>
      <li>アリの大顎の超高速運動（トラップジョー）の画像計測と，そのラッチ機構のモデル化．</li>
      <li>楕円形の膝関節がジャンプ性能に与える影響など，関節形状そのものが持つ機能の解析．</li>
    </ul>

    <h2>02 &nbsp;やわらかいアクチュエータをつくる</h2>
    <p>
      McKibben型空気圧人工筋（MPA）は，ゴムチューブを繊維スリーブで包んだだけの単純な構造で，
      加圧すると縮んで力を出します．筋肉に似た非線形なばね特性を持つのが特徴で，
      この特性自体がロボットの運動を安定化させる——というのが長年の研究テーマです．
    </p>
    <h3>具体的にやっていること</h3>
    <ul>
      <li><strong>LT-PAM</strong>（Low-Cost and Tough Pneumatic Artificial Muscle）：入手しやすい材料で，安価かつ丈夫に作れる人工筋の設計．製作手順をオープンハードウェアとして公開しています．</li>
      <li>小型ソレノイドバルブによる複数MPAの同時制御，動的量子化器を用いた長さ制御．</li>
      <li>張力センサを人工筋に組み込み，センサレスに近い形で状態を推定する試み．</li>
      <li>拮抗二関節筋における，張力フィードバックだけによる自律的な協調制御．</li>
      <li>論理回路のアナロジーで空圧回路を設計する「電気を使わない制御」の検討．</li>
      <li>弾性体を組み合わせてMPAに曲げ運動をさせる機構，カニ型ロボットの外骨格構造への埋め込み．</li>
    </ul>

    <h2>03 &nbsp;フィールドを走破する移動ロボット</h2>
    <p>
      整地された床で動くロボットは，もうたくさんあります．
      問題は，土や瓦礫や斜面といった「決まった形をしていない場所」でどう動くか．
      走破性をきちんと測る物差しづくりから，実機開発まで行っています．
    </p>
    <h3>具体的にやっていること</h3>
    <ul>
      <li><strong>地形の空間周波数解析</strong>：不整地を正弦波状の地形に分解して捉え，
          「どの空間周波数の凹凸に強い／弱いか」という形で移動ロボットの走破性を定量評価する手法．</li>
      <li>陰的・陽的制御を組み合わせた水陸両用ムカデ型ロボットの開発．</li>
      <li>災害対応を想定したモジュール型ロボットシステム．目的に応じて機能モジュールを組み替えます．</li>
      <li>無限定環境での土砂搬送に向けた柔軟湾曲型コンベア，植物の根に着想を得た軟弱地盤用アンカーなど，
          現場を意識した要素技術の開発．</li>
      <li>転動ロボットの旋回運動解析といった，非ホロノミックな移動体の基礎研究．</li>
    </ul>

    <h2>04 &nbsp;脳がなくても歩けるのか</h2>
    <p>
      “Brainless Walking”——中枢のパターン生成器を持たない，
      弱いアクチュエータを並べただけのロボットが，動物らしい歩容を自発的に見せる．
      この現象は，制御が身体側に「陰に」埋め込まれていることを端的に示しています．
    </p>
    <h3>具体的にやっていること</h3>
    <ul>
      <li>アクチュエータ特性そのものから歩容が創発する条件の解析．拮抗構造における協調のモード分岐．</li>
      <li>超分散型・超多脚の「無脳歩行ロボット」の試作．</li>
      <li>イモムシのような柔らかい個体が群れたときのロコモーション．</li>
      <li>Physical Reservoir Computing を使って，センサを増やさずに人工筋の状態を読み取る試み．</li>
    </ul>

    <div class="callout">
      <h3>研究テーマは相談して決めます</h3>
      <p>
        ここに書いたのはあくまで研究室の地図です．
        配属後は「どのあたりに興味があるか」を聞いたうえで，
        本人の得意・不得意も踏まえてテーマを一緒に決めていきます．
        ものづくり寄り，解析寄り，プログラム寄り，どの方向にも振れます．
      </p>
      <p><a class="btn btn-solid" href="join.html">配属を考えている方へ</a></p>
    </div>

  </div>
</section>
"""

# ============================================================ members
MEMBERS = head_block("Members", "メンバー",
    "教員1名と学生で活動しています．学生情報は準備でき次第このページに掲載します．") + """
<section class="section">
  <div class="wrap narrow">
    <div data-faculty></div>

    <hr class="hr">

    <h2 style="font-size:21px;margin:0 0 20px;padding-bottom:10px;border-bottom:2px solid var(--accent-lt)">学生メンバー</h2>
    <div data-students></div>

    <hr class="hr">

    <h2 style="font-size:21px;margin:0 0 20px;padding-bottom:10px;border-bottom:2px solid var(--accent-lt)">共同研究者</h2>
    <p class="muted small" style="margin-bottom:18px">学外の先生方と幅広く共同研究を進めています．</p>
    <ul class="roster">
      <li><span class="grade">大阪大学</span><span class="who">大須賀 公一 先生</span><span class="theme">移動知・陰的制御・空気圧人工筋</span></li>
      <li><span class="grade">大阪工業大学</span><span class="who">杉本 靖博 先生</span><span class="theme">歩行解析・McKibben型空気圧アクチュエータ</span></li>
      <li><span class="grade">松江高専</span><span class="who">中西 大輔 先生</span><span class="theme">ソフトアクチュエータ・ヘビ型ロボット</span></li>
      <li><span class="grade">大阪大学</span><span class="who">増田 容一 先生</span><span class="theme">脚ロボット・身体性</span></li>
    </ul>
    <p class="small muted" style="margin-top:14px">※ 掲載内容は随時更新します．</p>
  </div>
</section>
"""

# ============================================================ publications
PUBS = head_block("Publications", "業績",
    "researchmap に登録された業績をもとに掲載しています．カテゴリの絞り込みとキーワード検索ができます．", narrow=False) + """
<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="pub-toolbar">
      <div id="pub-filters" style="display:flex;flex-wrap:wrap;gap:8px"></div>
      <input id="pub-search" class="pub-search" type="search" placeholder="キーワード・著者名・年で検索">
      <span id="pub-count" class="pub-count"></span>
    </div>
    <div id="pub-list"></div>
    <p class="small muted" style="margin-top:40px">
      最新の完全な業績リストは
      <a href="https://researchmap.jp/Naniwa_K" target="_blank" rel="noopener">researchmap</a>
      をご覧ください．
    </p>
  </div>
</section>
"""

# ============================================================ news
NEWS = head_block("News", "お知らせ",
    "論文の掲載・採択，学会発表，研究室の出来事などをお知らせします．") + """
<section class="section">
  <div class="wrap narrow">
    <div data-news="0"></div>
  </div>
</section>
"""

# ============================================================ join
JOIN = head_block("Join us", "配属を考えている方へ",
    "研究室選びは，4年生以降の1〜3年をどう過ごすかを決める，けっこう大きな選択です．判断材料になりそうなことを正直に書いておきます．") + """
<section class="section">
  <div class="wrap narrow prose">

    <h2>この研究室でできること</h2>
    <p>
      ひとことで言うと，<strong>「動くものを自分の手で作って，なぜ動くのかを考える」</strong>研究室です．
      ロボットの機体を設計して，回路を組んで，マイコンを書いて，実験して，データを解析して，
      それを論文や学会発表という形にまとめるまで．一通り経験できます．
    </p>
    <p>
      対象は，脚で歩くロボット，空気圧で動くやわらかいアクチュエータ，
      土や瓦礫の上を進む移動ロボット，そして本物の昆虫の歩行計測まで．
      「機械工学科なのに虫を扱うの？」とよく言われますが，
      生きものは何億年もかけて最適化された移動機械なので，学ぶことがとても多いのです．
    </p>

    <h2>身につくもの</h2>
    <ul>
      <li><strong>設計・製作</strong>：3D CAD，3Dプリンタ，機械加工．「頭の中の機構を，実物にする」プロセス．</li>
      <li><strong>電気・制御</strong>：Arduino や各種マイコン，モータドライバ，センサ回路．</li>
      <li><strong>プログラミング</strong>：Python を中心に，計測・データ解析・シミュレーション．最初は誰も書けないので大丈夫です．</li>
      <li><strong>ものを伝える力</strong>：学会発表のスライド，論文執筆．これは社会に出てから一番効いてきます．</li>
    </ul>

    <h2>研究室のふんいき</h2>
    <p>
      基本的にはゆるいです．が，学会に出す・論文にする，というところは真面目にやります．
      「何のためにその実験をするのか」を自分の言葉で説明できるようになってほしい，
      というのが一番のこだわりです．
    </p>
    <p>
      教員は関西出身なので，だいたい関西弁でしゃべっています．
      分からないことを分からないと言える空気は，意識して守っているつもりです．
    </p>

    <h2>よくある質問</h2>
    <div class="qa">
      <details>
        <summary>プログラミングが苦手なのですが，大丈夫ですか？</summary>
        <div class="answer">
          <p>大丈夫です．配属時点でスラスラ書ける学生は，正直ほとんどいません．
             必要になったところから少しずつ覚えていけば間に合います．
             むしろ「手を動かして試す」ことを面倒がらない人のほうが伸びます．</p>
        </div>
      </details>
      <details>
        <summary>生物の知識がないと厳しいですか？</summary>
        <div class="answer">
          <p>まったく必要ありません．こちらも機械屋として虫を見ています．
             必要な生物の話は，そのつど一緒に勉強します．
             もちろん，生きものに興味がある人は楽しいと思います．</p>
        </div>
      </details>
      <details>
        <summary>コアタイムはありますか？</summary>
        <div class="answer">
          <p>厳格なコアタイムは設けていません．ただし，研究は時間をかけた分だけ進みます．
             週に一度の進捗報告（ゼミ）があるので，そこに何かしら持ってこられるペースで来てもらうことになります．
             アルバイトや部活との両立は，相談してもらえれば調整します．</p>
        </div>
      </details>
      <details>
        <summary>学会発表はできますか？</summary>
        <div class="answer">
          <p>できます．というより，成果が出たら積極的に出してもらいます．
             ロボティクス・メカトロニクス講演会（ROBOMECH）をはじめとする国内学会が中心ですが，
             内容次第では国際会議も視野に入ります．
             人前で自分の研究を話す経験は，就職活動でも効きます．</p>
        </div>
      </details>
      <details>
        <summary>大学院に行ったほうがいいですか？</summary>
        <div class="answer">
          <p>研究を面白いと思えたなら，強くおすすめします．
             4年生の1年間だと，どうしても「立ち上げて終わり」になりがちで，
             一番面白い「分かってきた」局面に入る前に卒業してしまうことが多いです．
             一方で，学部で就職する人も当然います．無理に勧めることはしません．</p>
        </div>
      </details>
      <details>
        <summary>就職はどうなりますか？</summary>
        <div class="answer">
          <p>機械設計，電気・制御系，生産技術など，ものづくり系の進路が中心です．
             研究室で「設計して，作って，測って，まとめる」を一周した経験は，
             そのまま面接で話せる材料になります．</p>
        </div>
      </details>
      <details>
        <summary>研究室見学はできますか？</summary>
        <div class="answer">
          <p>いつでも歓迎します．メールで連絡をもらえれば日程を調整します．
             実際に動いているロボットを見てもらうのが一番早いです．
             他大学からの進学相談も受け付けています．</p>
        </div>
      </details>
    </div>

    <div class="callout">
      <h3>まずは見に来てください</h3>
      <p>
        Webサイトを何回読むより，一度部屋に来て実機を触ってもらったほうが早いです．
        「ちょっと見てみたい」くらいの温度で構いません．
      </p>
      <p><a class="btn btn-solid" href="access.html">連絡先・アクセス</a></p>
    </div>

  </div>
</section>
"""

# ============================================================ access
ACCESS = head_block("Access", "アクセス・お問い合わせ") + """
<section class="section">
  <div class="wrap narrow prose">

    <h2>お問い合わせ</h2>
    <p>
      研究室見学，共同研究，取材，進学相談など，お気軽にご連絡ください．
      学生の方は所属（学部・学年）を添えてもらえると話が早いです．
    </p>
    <dl class="dl" style="margin-bottom:28px">
      <dt>担当</dt><dd>浪花 啓右（准教授）</dd>
      <dt>E-mail</dt><dd>naniwa-k [at] hus.ac.jp<br><span class="small muted">［at］を @ に置き換えてください</span></dd>
      <dt>所属</dt><dd>北海道科学大学 工学部 機械工学科</dd>
      <dt>researchmap</dt><dd><a href="https://researchmap.jp/Naniwa_K" target="_blank" rel="noopener">researchmap.jp/Naniwa_K</a></dd>
    </dl>

    <h2>所在地</h2>
    <p>
      北海道科学大学<br>
      〒006-8585 &nbsp;北海道札幌市手稲区前田7条15丁目4-1
    </p>
    <p class="small muted">※ 研究室の部屋番号はこちらに追記予定です．</p>

    <h3>交通アクセス</h3>
    <ul>
      <li>JR函館本線「手稲駅」南口から 徒歩約15分／北海道科学大学行きバス</li>
      <li>地下鉄東西線「宮の沢駅」からバス</li>
      <li>詳細は
        <a href="https://www.hus.ac.jp/" target="_blank" rel="noopener">北海道科学大学 公式サイト</a>
        の交通アクセス案内をご確認ください．</li>
    </ul>

    <div class="callout">
      <h3>研究室見学について</h3>
      <p>
        平日であればおおむね対応できます．
        学内の学生は，直接部屋を訪ねてもらってもかまいません（不在のことがあるのでメールをもらえると確実です）．
      </p>
    </div>

  </div>
</section>
"""

if __name__ == "__main__":
    T = " | {} | {}".format(SITE_JA, "北海道科学大学 機械工学科")
    page("index.html", "{} | {}".format(SITE_JA, SITE_SUB), INDEX)
    page("research.html", "研究内容" + T, RESEARCH)
    page("members.html", "メンバー" + T, MEMBERS)
    page("publications.html", "業績" + T, PUBS,
         extra='<script src="assets/publications.js"></script>')
    page("news.html", "お知らせ" + T, NEWS)
    page("join.html", "配属を考えている方へ" + T, JOIN)
    page("access.html", "アクセス・お問い合わせ" + T, ACCESS)
    print("done.")
