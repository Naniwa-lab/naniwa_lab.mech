/* 業績ページ：カテゴリ絞り込み・検索・年別表示 */
(function () {
  "use strict";

  var ME = ["浪花 啓右", "浪花啓右", "Keisuke Naniwa", "NANIWA Keisuke", "Naniwa K."];
  var CATS = [
    { key: "all", label: "すべて" },
    { key: "journal", label: "学術論文（ジャーナル）" },
    { key: "intl", label: "国際会議" },
    { key: "domestic", label: "国内学会発表" },
    { key: "preprint", label: "プレプリント" }
  ];

  var esc = window.__esc;
  var listEl = document.getElementById("pub-list");
  var barEl = document.getElementById("pub-filters");
  var countEl = document.getElementById("pub-count");
  var searchEl = document.getElementById("pub-search");
  if (!listEl) return;

  var all = [];
  var state = { cat: "all", q: "" };

  function isMe(name) {
    var n = name.replace(/\s+/g, "");
    return ME.some(function (m) { return m.replace(/\s+/g, "") === n; });
  }

  function authorHtml(list) {
    return (list || []).map(function (a) {
      return isMe(a) ? '<span class="me">' + esc(a) + "</span>" : esc(a);
    }).join(", ");
  }

  function render() {
    var q = state.q.trim().toLowerCase();
    var items = all.filter(function (p) {
      if (state.cat !== "all" && p.cat !== state.cat) return false;
      if (!q) return true;
      var hay = [p.title, p.title_en, p.venue, (p.authors || []).join(" "), String(p.year)]
        .join(" ").toLowerCase();
      return hay.indexOf(q) !== -1;
    });

    countEl.textContent = items.length + " 件";

    if (!items.length) {
      listEl.innerHTML = '<p class="muted" style="padding:40px 0">該当する業績が見つかりませんでした．</p>';
      return;
    }

    var byYear = {};
    items.forEach(function (p) {
      var y = p.year || "年不明";
      (byYear[y] = byYear[y] || []).push(p);
    });
    var years = Object.keys(byYear).sort(function (a, b) { return b - a; });

    listEl.innerHTML = years.map(function (y) {
      return '<h2 class="pub-year">' + esc(y) + "</h2>" +
        '<ul class="pub-list">' + byYear[y].map(function (p) {
          var meta = [];
          if (p.refereed) meta.push('<span class="badge">査読付</span>');
          if (p.cat === "journal") meta.push('<span class="badge">Journal</span>');
          if (p.cat === "intl") meta.push('<span class="badge">Intl. Conf.</span>');
          if (p.doi) {
            meta.push('<a class="badge badge-doi" href="https://doi.org/' + esc(p.doi) +
              '" target="_blank" rel="noopener">DOI: ' + esc(p.doi) + "</a>");
          }
          var vol = [];
          if (p.volume) vol.push("vol. " + esc(p.volume));
          if (p.number) vol.push("no. " + esc(p.number));
          if (p.pages) vol.push("pp. " + esc(p.pages));
          return '<li class="pub-item">' +
            '<span class="t">' + esc(p.title) + "</span>" +
            (p.title_en ? '<span class="a" style="display:block">' + esc(p.title_en) + "</span>" : "") +
            '<span class="a">' + authorHtml(p.authors) + "</span><br>" +
            '<span class="v">' + esc(p.venue) + "</span>" +
            (vol.length ? '<span class="v">, ' + vol.join(", ") + "</span>" : "") +
            (p.year ? '<span class="v">, ' + esc(p.year) + "</span>" : "") +
            (meta.length ? '<span class="meta">' + meta.join("") + "</span>" : "") +
            "</li>";
        }).join("") + "</ul>";
    }).join("");
  }

  function buildFilters() {
    barEl.innerHTML = CATS.filter(function (c) {
      return c.key === "all" || all.some(function (p) { return p.cat === c.key; });
    }).map(function (c) {
      var n = c.key === "all" ? all.length : all.filter(function (p) { return p.cat === c.key; }).length;
      return '<button class="filter-btn' + (c.key === state.cat ? " active" : "") +
        '" data-cat="' + c.key + '">' + c.label + " (" + n + ")</button>";
    }).join("");

    Array.prototype.forEach.call(barEl.querySelectorAll(".filter-btn"), function (b) {
      b.addEventListener("click", function () {
        state.cat = b.getAttribute("data-cat");
        Array.prototype.forEach.call(barEl.querySelectorAll(".filter-btn"), function (x) {
          x.classList.toggle("active", x === b);
        });
        render();
      });
    });
  }

  if (searchEl) {
    searchEl.addEventListener("input", function () { state.q = searchEl.value; render(); });
  }

  fetch("data/publications.json", { cache: "no-cache" })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      all = d;
      buildFilters();
      render();
    })
    .catch(function () {
      listEl.innerHTML = '<p class="muted">業績データを読み込めませんでした．</p>';
    });
})();
