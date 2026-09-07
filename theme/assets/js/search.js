/*!
 * search.js —— 自研站内搜索（二次开发）
 * 方案说明：为不依赖外部 CDN / 不需管理 Content API Key，
 * 主题直接从本站 /rss/ 拉取全部已发布文章作为本地索引，在前端做关键词检索。
 * 支持：命中高亮 <mark>、无结果提示与建议、Esc/背景点击关闭、键盘 Enter 快速跳转。
 */
(function () {
    'use strict';

    var items = null;        // 索引缓存
    var idx = document.getElementById('mz-search');
    var input = document.getElementById('mz-search-input');
    var results = document.getElementById('mz-search-results');
    var form = document.getElementById('mz-search-form');
    var closeBtn = document.getElementById('mz-search-close');

    if (!idx || !input || !results) return;

    function esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    // 命中高亮（先转义再包 <mark>，避免注入）
    function mark(text, term) {
        var safe = esc(text);
        if (!term) return safe;
        try {
            var re = new RegExp('(' + term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
            return safe.replace(re, '<mark>$1</mark>');
        } catch (e) {
            return safe;
        }
    }

    function loadIndex() {
        if (items) return Promise.resolve(items);
        return fetch('/rss/')
            .then(function (r) { return r.text(); })
            .then(function (xml) {
                var doc = new DOMParser().parseFromString(xml, 'text/xml');
                var entries = doc.querySelectorAll('item');
                items = Array.prototype.map.call(entries, function (it) {
                    var cat = it.querySelector('category');
                    return {
                        title: (it.querySelector('title') || {}).textContent || '',
                        link: (it.querySelector('link') || {}).textContent || '',
                        desc: (it.querySelector('description') || {}).textContent || '',
                        tag: cat ? cat.textContent : ''
                    };
                });
                return items;
            })
            .catch(function () {
                items = [];
                return items;
            });
    }

    function render(list, term) {
        results.innerHTML = '';
        if (!list.length) {
            var empty = document.createElement('div');
            empty.className = 'mz-search-empty';
            empty.innerHTML =
                '<strong>未找到与「' + esc(term) + '」相关的文章</strong>' +
                '<span class="r-hint">试试更短的关键词，或换一个词再搜。</span>';
            results.appendChild(empty);
            return;
        }
        var frag = document.createDocumentFragment();
        list.forEach(function (it) {
            var a = document.createElement('a');
            a.className = 'mz-search-result';
            a.href = it.link;
            var tag = it.tag ? '<span class="r-tag">' + esc(it.tag) + '</span>' : '';
            a.innerHTML = tag + '<div class="r-title">' + mark(it.title, term) + '</div>';
            frag.appendChild(a);
        });
        results.appendChild(frag);
    }

    function search(term) {
        var q = (term || '').trim().toLowerCase();
        return loadIndex().then(function () {
            if (!q) { render([], ''); return; }
            var hits = items.filter(function (it) {
                return (it.title + ' ' + it.desc + ' ' + it.tag).toLowerCase().indexOf(q) !== -1;
            });
            render(hits.slice(0, 20), q);
        });
    }

    function open() {
        idx.hidden = false;
        idx.classList.add('is-open');
        document.body.style.overflow = 'hidden';
        setTimeout(function () { input.focus(); }, 30);
    }
    function close() {
        idx.hidden = true;
        idx.classList.remove('is-open');
        document.body.style.overflow = '';
    }

    // 接管所有搜索按钮（class .gh-search / data-ghost-search），阻止默认(可能触发外部 sodo)
    document.addEventListener('click', function (e) {
        var t = e.target.closest ? e.target.closest('.gh-search, [data-ghost-search]') : null;
        if (t) {
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();
            open();
        }
    }, true);

    form && form.addEventListener('submit', function (e) { e.preventDefault(); search(input.value); });
    input && input.addEventListener('input', function () { search(input.value); });
    closeBtn && closeBtn.addEventListener('click', close);
    idx && idx.addEventListener('click', function (e) { if (e.target === idx) close(); });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !idx.hidden) { close(); return; }
        var shortcut = e.key === '/' || ((e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey));
        if (shortcut && !/input|textarea|select/i.test(document.activeElement.tagName)) {
            e.preventDefault();
            open();
        }
    });
})();
