#!/usr/bin/env node
/**
 * seed-demo.js —— 构造任务4演示数据（可重复执行）
 *
 * 用 Ghost Admin API（会话登录方式）幂等地创建：
 *   - 4 个标签（tag）
 *   - 9 篇已发布文章（覆盖长标题 / 无封面 / 代码块 / 中文搜索词 / 邀请评论 等边界）
 *   - 2 个普通会员（member）
 *
 * 用法：
 *   1) 复制 runtime/.admin.env.example 为 runtime/.admin.env 并填入真实口令（该文件已被 gitignore）
 *   2) node scripts/seed-demo.js
 *
 * 依赖：Node >= 18（内置 fetch），无第三方依赖。
 */

const BASE = process.env.GHOST_URL || 'http://localhost:2368';
const EMAIL = process.env.GHOST_ADMIN_EMAIL;
const PASSWORD = process.env.GHOST_ADMIN_PASSWORD;

if (!EMAIL || !PASSWORD) {
  console.error('缺少 GHOST_ADMIN_EMAIL / GHOST_ADMIN_PASSWORD 环境变量');
  process.exit(1);
}

let cookie = '';
const H = { Origin: BASE, 'Content-Type': 'application/json' };

async function api(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: Object.assign({}, H, cookie ? { Cookie: cookie } : {}),
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`${method} ${path} -> ${res.status}: ${t.slice(0, 200)}`);
  }
  const setCookie = res.headers.get('set-cookie');
  if (setCookie) cookie = setCookie.split(';')[0];
  const ct = res.headers.get('content-type') || '';
  return ct.includes('json') ? res.json() : null;
}

// 登录需要 form 编码（fetch 不支持 form body 的简单 JSON），单独实现
async function login() {
  const res = await fetch(`${BASE}/ghost/api/admin/session/`, {
    method: 'POST',
    headers: { Origin: BASE, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(EMAIL)}&password=${encodeURIComponent(PASSWORD)}`,
  });
  if (!res.ok) throw new Error(`login failed: ${res.status}`);
  const sc = res.headers.get('set-cookie');
  if (!sc) throw new Error('no session cookie returned');
  cookie = sc.split(';')[0];
}

async function getList(path) {
  const data = await api('GET', `${path}?limit=all&fields=id,name,email,title`);
  return data ? Object.values(data)[0] : [];
}

async function ensure() {
  await login();

  // ---- 标签 ----
  const tags = [
    { name: 'Ghost', description: 'Ghost 博客平台与二次开发' },
    { name: '二次开发', description: '在成熟开源项目上做受控扩展' },
    { name: '开源软件', description: '开源文化、许可证与协作' },
    { name: '教程', description: '一步步上手的操作指南' },
  ];
  const existingTags = await getList('/ghost/api/admin/tags/');
  const tagNames = new Set(existingTags.map((t) => t.name));
  for (const t of tags) {
    if (!tagNames.has(t.name)) {
      await api('POST', '/ghost/api/admin/tags/', { tags: [t] });
      console.log(`+ tag: ${t.name}`);
    } else {
      console.log(`= tag(存在): ${t.name}`);
    }
  }

  // ---- 文章（按 published_at 交错，首页顺序更真实）----
  const day = (n) => new Date(Date.now() - n * 86400e3).toISOString();
  const posts = [
    {
      title: '用 Ghost 搭建个人博客：从零开始的完整指南',
      tag: 'Ghost', days: 1,
      html: '<p>从选择一个开源博客系统，到把它跑起来、写出一篇文章，本指南带你走完最小闭环。</p><h2>为什么选 Ghost？</h2><p>它内置了 Markdown 编辑器、会员与评论系统，我们只需要聚焦“内容”本身。</p>',
    },
    {
      title: '二次开发而不是从零造轮子：开源项目的正确打开方式',
      tag: '二次开发', days: 2,
      html: '<p>很多人拿到一个开源项目就想重写。真正有工程价值的方式，是搞清楚“上游能力”与“我的增量”之间的边界。</p><p>修改应当落在主题、上层 API 调用等独立模块，而不是入侵核心源码，这样才能跟上游长期同步升级。</p>',
    },
    {
      title: '把博客托管在自己手里：自建与 SaaS 的取舍',
      tag: '开源软件', days: 3,
      html: '<p>自建意味着掌控数据、掌控升级节奏，也意味着自己承担运维成本。本文比较两条路线的差异。</p>',
    },
    {
      // 边界：超长标题 —— 测试前台列表与详情页对超长标题的折行/截断处理
      title:
        '这是一篇用于测试超长标题显示效果的实验性文章：开源软件与新技术实验课的二次开发作业需要同时覆盖长标题、无封面、代码块、中文搜索词和空评论等多种边界场景，标题写得越长，越能暴露主题样式对极端文案的适应能力',
      tag: '教程', days: 4,
      html: '<p>如果这个标题在前台完整、可读地展示出来，说明主题对长标题的处理是合格的。</p>',
    },
    {
      // 边界：无封面
      title: '无封面也能很好看：没有特色图时的展示策略',
      tag: '教程', days: 5,
      feature_image: null,
      html: '<p>这篇文章没有设置封面图（feature_image 为空）。主题需要在没有特色图时提供优雅的占位与排版。</p>',
    },
    {
      title: 'Ghost 主题开发笔记：读懂 Handlebars 与模板上下文',
      tag: '教程', days: 6,
      html:
        '<p>Ghost 前台用 Handlebars 渲染。一个最小模板长这样：</p><pre><code>{{#foreach posts}}\n  &lt;article class=&quot;post-card&quot;&gt;\n    &lt;h2&gt;&lt;a href=&quot;{{url}}&quot;&gt;{{title}}&lt;/a&gt;&lt;/h2&gt;\n  &lt;/article&gt;\n{{/foreach}}</code></pre><p>data 上下文里带上了 posts、tags、pagination 等信息，二次开发的主战场就在这里。</p>',
    },
    {
      // 中文搜索词相关
      title: '中文全文搜索实测：这篇文章里有“搜索、评论、标签”等关键词',
      tag: 'Ghost', days: 7,
      html: '<p>想让中文搜索演示更可靠，正文里需要反复出现可被检索的词。关键词：搜索、评论、标签、二次开发、Ghost。</p>',
    },
    {
      title: '写给开源新手的十句话',
      tag: '开源软件', days: 8,
      html: '<p>读文档 > 提问；提问要带上复现步骤；贡献从小处开始；尊重许可证；先跑通再谈改代码。</p><p>如果你有同感，欢迎在下方评论区留言，我们一起聊聊。</p>',
    },
    {
      title: 'Ghost 6 的新变化速览',
      tag: 'Ghost', days: 9,
      html: '<p>Ghost 6 在主题、搜索与性能上持续演进。本实验固定 6.62.0 版本作为基线。</p>',
    },
  ];
  const existingPosts = await getList('/ghost/api/admin/posts/');
  const postTitles = new Set(existingPosts.map((p) => p.title));
  for (const p of posts) {
    if (!postTitles.has(p.title)) {
      await api('POST', '/ghost/api/admin/posts/', {
        posts: [
          {
            title: p.title,
            status: 'published',
            html: p.html,
            feature_image: p.feature_image !== undefined ? p.feature_image : null,
            tags: [{ name: p.tag }],
            published_at: day(p.days),
          },
        ],
      });
      console.log(`+ post: ${p.title.slice(0, 30)}...`);
    } else {
      console.log(`= post(存在): ${p.title.slice(0, 30)}...`);
    }
  }

  // ---- 普通会员 ----
  const members = [
    { name: '林小满', email: 'linxiaoman@example.com' },
    { name: '王一川', email: 'wangyichuan@example.com' },
  ];
  const existingMembers = await getList('/ghost/api/admin/members/');
  const memberEmails = new Set(existingMembers.map((m) => m.email));
  for (const m of members) {
    if (!memberEmails.has(m.email)) {
      await api('POST', '/ghost/api/admin/members/', { members: [m] });
      console.log(`+ member: ${m.name} <${m.email}>`);
    } else {
      console.log(`= member(存在): ${m.email}`);
    }
  }

  console.log('\n完成。前台 http://localhost:2368 刷新即可看到内容。');
}

ensure().catch((e) => {
  console.error('seed 失败：', e.message);
  process.exit(1);
});
