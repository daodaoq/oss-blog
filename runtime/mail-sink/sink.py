#!/usr/bin/env python3
"""
mail-sink —— 本地 SMTP 收信 + 网页"收件箱"（双服务，仅用 Python 标准库）

- SMTP  :1025  接收 Ghost 发出的邮件，原样写入 /mail/<时间戳>-<hash>.eml
- HTTP  :8025  一个迷你网页收件箱：自动解码 .eml（base64/quoted-printable），
                把每封邮件渲染成"收件人 / 标题 / 验证码 / 登录链接(可点击)"，
                再也不用手拆 .eml。点"登录"链接即在本机浏览器完成会员登录。

浏览器打开 http://localhost:8025
"""
import asyncore
import base64
import datetime
import email
import email.header
import hashlib
import http.server
import os
import re
import smtpd
import socketserver
import threading
import urllib.parse

MAIL_DIR = "/mail"
HTTP_PORT = 8025
GHOST_BASE = "http://localhost:2368"


# ---------------- SMTP 接收 ----------------
class SinkHandler(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        os.makedirs(MAIL_DIR, exist_ok=True)
        h = hashlib.md5(data).hexdigest()[:8]
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        fname = os.path.join(MAIL_DIR, f"{stamp}-{h}.eml")
        with open(fname, "wb") as f:
            f.write(data)
        print(f"SAVED {fname} to={rcpttos}", flush=True)


# ---------------- 解码工具 ----------------
def esc(s):
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def decode_header_value(v):
    if not v:
        return ""
    out = []
    for chunk, charset in email.header.decode_header(v):
        if isinstance(chunk, bytes):
            out.append(chunk.decode(charset or "utf-8", "replace"))
        else:
            out.append(chunk)
    return "".join(out)


def read_mails():
    if not os.path.isdir(MAIL_DIR):
        return []
    files = [f for f in os.listdir(MAIL_DIR) if f.endswith(".eml")]
    files.sort(reverse=True)
    result = []
    for fn in files:
        path = os.path.join(MAIL_DIR, fn)
        raw = open(path, "rb").read()
        try:
            msg = email.message_from_bytes(raw)
        except Exception:
            continue
        texts, htmls = [], []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                p = part.get_payload(decode=True)
                if p:
                    texts.append(p.decode("utf-8", "replace"))
            elif part.get_content_type() == "text/html":
                p = part.get_payload(decode=True)
                if p:
                    htmls.append(p.decode("utf-8", "replace"))
        body = "\n".join(texts) + "\n" + "\n".join(htmls)
        links = sorted(
            set(re.findall(r"https?://localhost:2368/members/\?token=[^\s\"'<>]+", body))
        )
        # 验证码：只取带 code/verification 语义附近的 6 位数字；html 部分优先 <h2> 内大号码
        code = None
        m = re.search(r"(?:code|verification)[^\d]{0,50}(\d{6})", body, re.I)
        if m:
            code = m.group(1)
        if not code:
            m = re.search(r"<h2[^>]*>\s*(\d{6})\s*</h2>", "\n".join(htmls), re.I)
            if m:
                code = m.group(1)
        result.append(
            {
                "file": fn,
                "to": decode_header_value(msg.get("To", "")),
                "from": decode_header_value(msg.get("From", "")),
                "subject": decode_header_value(msg.get("Subject", "")),
                "date": msg.get("Date", "")[:30],
                "code": code,
                "links": links,
                "text": "\n".join(texts)[:3000],
            }
        )
    return result


# ---------------- HTTP 收件箱 ----------------
def render_list(mails):
    rows = ""
    for m in mails:
        rows += (
            f'<tr><td>{esc(m["date"])}</td><td>{esc(m["to"])}</td>'
            f'<td><a href="/view/{urllib.parse.quote(m["file"])}">{esc(m["subject"])}</a></td>'
            f'<td>{esc(m["code"]) if m["code"] else "-"}</td></tr>'
        )
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>本地收件箱 · mail-sink</title>
<style>
 body{{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#f5f4f0;margin:0}}
 h1{{font-size:20px}} main{{max-width:860px;margin:24px auto;padding:0 16px}}
 table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}}
 th,td{{padding:10px 12px;border-bottom:1px solid #eee;text-align:left;font-size:14px}}
 th{{background:#1a1a1a;color:#fff}}
 a{{color:#c0392b;text-decoration:none}}
 .badge{{background:#1a1a1a;color:#fff;border-radius:6px;padding:1px 8px;font-size:12px}}
</style></head><body><main>
<h1>📬 本地收件箱 <span class="badge">{len(mails)} 封</span></h1>
<p style="color:#666">最新邮件在上面。点标题查看验证码和登录链接。</p>
<table><tr><th>时间</th><th>收件人</th><th>主题</th><th>验证码</th></tr>{rows}</table>
</main></body></html>"""


def render_view(m, files):
    code_box = f'<div style="font-size:44px;letter-spacing:8px;font-weight:700;background:#f0ece2;border:1px dashed #c0392b;border-radius:10px;padding:18px;text-align:center;margin:16px 0">{esc(m["code"])}</div>' if m["code"] else ""
    links = ""
    for i, link in enumerate(m["links"]):
        links += (
            f'<p><a class="btn" href="{esc(link)}" target="_blank">🔑 点击登录（第{i+1}个链接）</a></p>'
        )
    if not links:
        links = '<p style="color:#999">本邮件没有可点击的登录链接。</p>'
    list_link = ""
    if files:
        list_link = f'<p><a href="/">&larr; 返回收件箱</a>（下一封：<a href="/view/{urllib.parse.quote(files[0])}">最新</a>）</p>'
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>邮件 · {esc(m["subject"])}</title>
<style>
 body{{font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#f5f4f0;margin:0;color:#1a1a1a}}
 main{{max-width:720px;margin:28px auto;padding:0 16px}}
 .card{{background:#fff;border-radius:12px;padding:28px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
 h1{{font-size:22px;margin-top:0}}
 .meta{{color:#888;font-size:13px;margin:4px 0}}
 .btn{{display:inline-block;background:#c0392b;color:#fff;padding:12px 22px;border-radius:8px;text-decoration:none;font-size:15px}}
 pre{{white-space:pre-wrap;background:#faf7f1;padding:14px;border-radius:8px;font-size:14px;color:#333}}
</style></head><body><main><div class="card">
{list_link}
<p class="meta">发件人：{esc(m["from"])}</p>
<p class="meta">收件人：{esc(m["to"])}</p>
<p class="meta">时间：{esc(m["date"])}</p>
<h1>{esc(m["subject"])}</h1>
{code_box}
{links}
<hr>
<h3>正文预览</h3>
<pre>{esc(m["text"])}</pre>
</div></main></body></html>"""


class MailboxHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        mails = read_mails()
        if parsed.path == "/":
            body = render_list(mails).encode("utf-8")
        elif parsed.path.startswith("/view/"):
            fn = urllib.parse.unquote(parsed.path[len("/view/"):])
            cur = next((m for m in mails if m["file"] == fn), None)
            if not cur:
                self.send_response(404)
                self.end_headers()
                return
            others = [m["file"] for m in mails if m["file"] != fn]
            body = render_view(cur, others).encode("utf-8")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_http():
    with socketserver.ThreadingTCPServer(("0.0.0.0", HTTP_PORT), MailboxHandler) as httpd:
        print(f"mailbox web UI listening on :{HTTP_PORT}", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run_http, daemon=True).start()
    SinkHandler(("0.0.0.0", 1025), None)
    print("mail-sink listening on :1025", flush=True)
    asyncore.loop()
