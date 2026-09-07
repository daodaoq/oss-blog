#!/usr/bin/env node
/**
 * fix-site-settings.js —— 修复站点标题/描述乱码（BUG-003）
 *
 * 成因：Windows 控制台(GBK)用 curl 创建 owner 时提交了中文 blogTitle，
 * 站点标题/描述等被存成含 U+FFFD 的非法字符。Node fetch 保证 UTF-8 发送，
 * 通过 Admin API 重写这些 settings（以及默认 newsletter 名）。
 *
 * 用法：node scripts/fix-site-settings.js   （读取 runtime/.admin.env 或环境变量）
 * 幂等：重复执行只会把值再写一遍。
 */
const fs = require('fs');
const path = require('path');

const BASE = process.env.GHOST_URL || 'http://localhost:2368';
const EMAIL = process.env.GHOST_ADMIN_EMAIL;
const PASSWORD = process.env.GHOST_ADMIN_PASSWORD;

if (!EMAIL || !PASSWORD) {
  console.error('缺少 GHOST_ADMIN_EMAIL / GHOST_ADMIN_PASSWORD 环境变量');
  process.exit(1);
}

const GOOD = {
  title: 'sjk 的开源博客',
  description: '开源软件与新技术实验01 · 基于 Ghost 二次开发的个人博客',
  meta_title: 'sjk 的开源博客',
  meta_description: '基于 Ghost 6.62.0 二次开发的开源个人博客：写作、评论、搜索。',
  og_title: 'sjk 的开源博客',
  og_description: '基于 Ghost 6.62.0 二次开发的开源个人博客。',
};

async function login() {
  const res = await fetch(`${BASE}/ghost/api/admin/session/`, {
    method: 'POST',
    headers: { Origin: BASE, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(EMAIL)}&password=${encodeURIComponent(PASSWORD)}`,
  });
  if (!res.ok) throw new Error(`login failed ${res.status}`);
  const sc = res.headers.get('set-cookie');
  if (!sc) throw new Error('no session cookie');
  return sc.split(';')[0];
}

async function api(cookie, method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { Origin: BASE, 'Content-Type': 'application/json', Cookie: cookie },
    body: body ? JSON.stringify(body) : undefined,
  });
  const t = await res.text();
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status}: ${t.slice(0, 200)}`);
  return t ? JSON.parse(t) : null;
}

async function main() {
  const cookie = await login();
  await api(cookie, 'PUT', '/ghost/api/admin/settings/', { settings: Object.entries(GOOD).map(([key, value]) => ({ key, value })) });
  console.log('settings 已重写:', Object.keys(GOOD).join(', '));

  // 顺手把默认 newsletter 名（也曾在创建时被写坏）改成干净值
  const nl = await api(cookie, 'GET', '/ghost/api/admin/newsletters/?limit=all&fields=id,name');
  for (const n of (nl && nl.newsletters) || []) {
    if (/[�]/.test(n.name)) {
      await api(cookie, 'PUT', `/ghost/api/admin/newsletters/${n.id}/`, { newsletters: [{ id: n.id, name: 'sjk 的开源博客 简报' }] });
      console.log('newsletter 已修复:', n.id);
    }
  }
  console.log('完成。刷新前台即可看到正确中文标题。');
}

main().catch((e) => { console.error('失败:', e.message); process.exit(1); });
