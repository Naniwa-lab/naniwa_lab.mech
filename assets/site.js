/* 共通スクリプト：モバイルメニュー / News・メンバーの読み込み */
(function () {
  "use strict";

  /* ---- モバイルメニュー ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- ユーティリティ ---- */
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  window.__esc = esc;

  function fmtDate(d) {
    var m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(d || "");
    if (!m) return esc(d);
    return m[3] ? m[1] + "." + m[2] + "." + m[3] : m[1] + "." + m[2];
  }

  var CAT_LABEL = { paper: "論文", award: "受賞", event: "イベント", lab: "研究室" };

  /* ---- News ---- */
  var newsBoxes = document.querySelectorAll("[data-news]");
  if (newsBoxes.length) {
    fetch("data/news.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (all) {
        all.sort(function (a, b) { return (b.date || "").localeCompare(a.date || ""); });
        Array.prototype.forEach.call(newsBoxes, function (box) {
          var limit = parseInt(box.getAttribute("data-news"), 10);
          var items = limit > 0 ? all.slice(0, limit) : all;
          if (!items.length) { box.innerHTML = '<p class="muted">お知らせはまだありません．</p>'; return; }
          var html = '<ul class="news-list">';
          items.forEach(function (n) {
            var cat = n.cat || "lab";
            var body = n.url
              ? '<a href="' + esc(n.url) + '" target="_blank" rel="noopener">' + esc(n.title) + "</a>"
              : esc(n.title);
            html +=
              "<li>" +
              '<span class="news-date">' + fmtDate(n.date) + "</span>" +
              '<span class="news-cat ' + esc(cat) + '">' + esc(CAT_LABEL[cat] || cat) + "</span>" +
              '<span class="news-body">' + body +
              (n.sub ? '<span class="sub">' + esc(n.sub) + "</span>" : "") +
              "</span></li>";
          });
          html += "</ul>";
          box.innerHTML = html;
        });
      })
      .catch(function () {
        Array.prototype.forEach.call(newsBoxes, function (box) {
          box.innerHTML = '<p class="muted">お知らせを読み込めませんでした．</p>';
        });
      });
  }

  /* ---- メンバー ---- */
  var facBox = document.querySelector("[data-faculty]");
  var stuBox = document.querySelector("[data-students]");
  if (facBox || stuBox) {
    fetch("data/members.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (facBox) {
          facBox.innerHTML = (d.faculty || []).map(function (m) {
            var photo = m.photo
              ? '<img class="member-photo" src="' + esc(m.photo) + '" alt="' + esc(m.name) + '">'
              : '<div class="member-photo photo-ph">写真を<br>準備中です</div>';
            var links = (m.links || []).map(function (l) {
              return '<a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label) + "</a>";
            }).join(" ／ ");
            var dl = "";
            if (m.degree) dl += "<dt>学位</dt><dd>" + esc(m.degree) + "</dd>";
            if (m.affiliation) dl += "<dt>所属</dt><dd>" + esc(m.affiliation) + "</dd>";
            if (m.field) dl += "<dt>専門分野</dt><dd>" + esc(m.field) + "</dd>";
            if (m.email) dl += "<dt>連絡先</dt><dd>" + esc(m.email) + "</dd>";
            if (links) dl += "<dt>リンク</dt><dd>" + links + "</dd>";
            return (
              '<div class="member-lead">' + photo + "<div>" +
              '<h2 class="member-name mt0">' + esc(m.name) +
              (m.name_en ? '<span class="en">' + esc(m.name_en) + "</span>" : "") + "</h2>" +
              '<p class="member-role">' + esc(m.role || "") + "</p>" +
              (m.bio || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("") +
              '<dl class="dl">' + dl + "</dl>" +
              "</div></div>"
            );
          }).join('<hr class="hr">');
        }
        if (stuBox) {
          var s = d.students || [];
          if (!s.length) { stuBox.innerHTML = '<p class="muted">準備中です．</p>'; return; }
          stuBox.innerHTML = '<ul class="roster">' + s.map(function (m) {
            return "<li>" +
              '<span class="grade">' + esc(m.grade) + "</span>" +
              '<span class="who">' + esc(m.name) + "</span>" +
              (m.theme ? '<span class="theme">' + esc(m.theme) + "</span>" : "") +
              "</li>";
          }).join("") + "</ul>";
        }
      })
      .catch(function () {
        if (facBox) facBox.innerHTML = '<p class="muted">メンバー情報を読み込めませんでした．</p>';
      });
  }

  /* ---- トップページの業績サマリ ---- */
  var statBox = document.querySelector("[data-pubstats]");
  if (statBox) {
    fetch("data/publications.json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (p) {
        var n = function (c) { return p.filter(function (x) { return x.cat === c; }).length; };
        var years = p.map(function (x) { return x.year; }).filter(Boolean);
        statBox.innerHTML =
          '<div class="stat"><div class="n">' + n("journal") + '</div><div class="l">学術論文（ジャーナル）</div></div>' +
          '<div class="stat"><div class="n">' + n("intl") + '</div><div class="l">国際会議</div></div>' +
          '<div class="stat"><div class="n">' + n("domestic") + '</div><div class="l">国内学会発表</div></div>' +
          '<div class="stat"><div class="n">' + (Math.max.apply(null, years) - Math.min.apply(null, years) + 1) +
          '</div><div class="l">年分の業績を掲載</div></div>';
      })
      .catch(function () { statBox.innerHTML = ""; });
  }
})();
