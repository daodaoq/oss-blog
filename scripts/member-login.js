#!/usr/bin/env node
/**
 * member-login.js —— 会员无密码登录（OTC 验证码方式），用于演示与自动化测试
 *
 * 流程（与 Ghost Portal 完全一致）：
 *   1) GET  /members/api/integrity-token/          取 CSRF token
 *   2) POST /members/api/send-magic-link/           发登录邮件（邮件落在 mail-sink）
 *   3) 读 mail-sink 落盘的 .eml 里的 6 位 OTC 码
 *   4) POST /members/api/verify-otc/                用 otcRef+otc 换 redirectUrl
 *   5) GET  redirectUrl                             建立会员会话 cookie
 *
 * 用法：node scripts/member-login.js <email> [cookieFile]
 *   cookieFile 默认 runtime/.member.cookies
 */
const fs = require('fs');
const path = require('path');

const BASE = process.env.GHOST_URL || 'http://localhost:2368';
const MAIL_DIR = path.resolve(__dirname, '../runtime/mail');
const email = process.argv[2];
const cookieFile = process.argv[3] || path.resolve(__dirname, '../runtime/.member.cookies');

if (!email) {
  console.error('usage: node scripts/member-login.js <email>');
  process.exit(1);
}

async function jsonOrText(res) {
  const t = await res.text();
  try { return { res, body: JSON.parse(t) }; } catch { return { res, body: t }; }
}

async function main() {
  // 1) integrity token
  const it = (await (await fetch(`${BASE}/members/api/integrity-token/`)).text()).trim();
  if (!it) throw new Error('integrity token empty');

  // 2) 发送 magic link
  const send = await fetch(`${BASE}/members/api/send-magic-link/`, {
    method: 'POST',
    headers: { Origin: BASE, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, emailType: 'signin', autoRedirect: false, integrityToken: it }),
  });
  const sendBody = send.status === 200 || send.status === 201 ? await send.json() : null;
  if (!send.ok) throw new Error(`send-magic-link -> ${send.status} ${JSON.stringify(sendBody)}`);
  const otcRef = sendBody?.otcRef;
  console.log('send-magic-link ok', send.status, 'body:', JSON.stringify(sendBody).slice(0, 200));
  if (!otcRef) throw new Error('响应中未返回 otcRef，无法继续');

  // 3) 读最新邮件里的 6 位 OTC
  await new Promise((r) => setTimeout(r, 2500));
  const files = fs.readdirSync(MAIL_DIR).filter((f) => f.endsWith('.eml')).sort();
  if (!files.length) throw new Error('没有收到邮件');
  const latest = path.join(MAIL_DIR, files[files.length - 1]);
  const raw = fs.readFileSync(latest, 'utf8');
  const codes = raw.match(/\b(\d{6})\b/g);
  const otc = codes && codes[codes.length - 1];
  if (!otc) throw new Error(`未在邮件中找到 6 位验证码: ${latest}`);
  console.log('OTC:', otc, 'from', latest);

  // 4) verify OTC -> redirectUrl
  const verify = await fetch(`${BASE}/members/api/verify-otc/`, {
    method: 'POST',
    headers: { Origin: BASE, 'Content-Type': 'application/json' },
    body: JSON.stringify({ otc, otcRef }),
  });
  const vbody = await verify.json();
  if (!verify.ok) throw new Error(`verify-otc -> ${verify.status} ${JSON.stringify(vbody)}`);
  const redirectUrl = vbody.redirectUrl;
  console.log('redirectUrl:', redirectUrl);

  // 5) 访问 redirectUrl 建立会员会话
  const final = await fetch(redirectUrl, { redirect: 'manual', headers: { Origin: BASE } });
  const setCookies = final.headers.get('set-cookie') || '';
  if (setCookies) fs.writeFileSync(cookieFile, setCookies.split(';')[0]);
  console.log('magic-link visit http', final.status, '| cookie saved:', fs.existsSync(cookieFile) ? cookieFile : '(none)');
}

main().catch((e) => { console.error('member-login 失败:', e.message); process.exit(1); });
