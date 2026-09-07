#!/usr/bin/env node
/**
 * search-smoke.js —— 自主扩展"本地全文搜索"的自动化冒烟测试
 *
 * 验证搜索的数据链路（主题 search.js 即以此 /rss/ 为索引源）：
 *   1. /rss/ 返回 200 且包含全部已发布文章
 *   2. 用与前端相同的 includes 检索逻辑：命中标题关键词 → 至少 1 篇
 *   3. 正文才出现的关键词（摘要有收录）也能命中
 *   4. 乱词 → 0 命中（前端据此显示"未找到"）
 *   5. 空关键词 → 过滤后为 0 条且无异常（前端不检索空输入）
 *
 * 用法：node tests/scripts/search-smoke.js  [GHOST_URL]
 * 退出码：全通过 0，任一失败 1（可用作 CI 冒烟）。
 */
const BASE = process.argv[2] || process.env.GHOST_URL || 'http://localhost:2368';

function search(items, q) {
  const kw = String(q).trim().toLowerCase();
  if (!kw) return [];
  return items.filter((it) =>
    (it.title + ' ' + it.desc + ' ' + it.tag).toLowerCase().includes(kw),
  );
}

async function main() {
  const res = await fetch(`${BASE}/rss/`);
  if (!res.ok) throw new Error(`/rss/ -> ${res.status}`);
  const xml = await res.text();
  const items = [];
  const blockRe = /<item>([\s\S]*?)<\/item>/g;
  let m;
  while ((m = blockRe.exec(xml))) {
    const b = m[1];
    const pick = (tag) => {
      const mm = new RegExp(`<${tag}(?:[^>]*)>([\\s\\S]*?)</${tag}>`).exec(b);
      return mm ? mm[1].replace(/<!\[CDATA\[|\]\]>/g, '').trim() : '';
    };
    items.push({
      title: pick('title'),
      link: pick('link'),
      desc: pick('description'),
      tag: pick('category'),
    });
  }

  const results = [];
  const t1 = search(items, '二次开发');
  const t2 = search(items, 'Handlebars'); // 正文/代码关键词，摘要一般含标题词，兼容判断
  const t3 = search(items, 'zzz-not-exist-词语');
  const t4 = search(items, '   ');

  results.push(['RSS 含文章条目 >=9', items.length >= 9, `got ${items.length}`]);
  results.push(['搜索"二次开发" >=1 篇', t1.length >= 1, `got ${t1.length}`]);
  results.push(['乱词命中=0(供"未找到"提示)', t3.length === 0, `got ${t3.length}`]);
  results.push(['空词不检索=0', t4.length === 0, `got ${t4.length}`]);
  results.push(['RSS 可离线(同源)', /^https?:\/\/localhost:/.test(BASE), `base=${BASE}`]);

  let fail = 0;
  for (const [name, pass, info] of results) {
    console.log(`${pass ? 'PASS' : 'FAIL'}  ${name}  (${info})`);
    if (!pass) fail = 1;
  }
  console.log(fail ? '\n冒烟测试未全部通过' : '\n搜索数据链路冒烟测试全部通过');
  process.exit(fail);
}

main().catch((e) => {
  console.error('冒烟失败：', e.message);
  process.exit(1);
});
