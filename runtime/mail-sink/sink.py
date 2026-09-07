#!/usr/bin/env python3
"""
mail-sink —— 本地 SMTP 收信器（替代 Mailpit 的极简实现，无需第三方依赖）
把收到的每一封邮件原样写入 /mail/<时间戳>-<hash>.eml，供读取 magic link / 截图。
Python 3.11 内置 smtpd（3.12 起移除，因此基础镜像固定 python:3.11-slim）。
"""
import asyncore
import datetime
import hashlib
import os
import smtpd


class SinkHandler(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        outdir = "/mail"
        os.makedirs(outdir, exist_ok=True)
        h = hashlib.md5(data).hexdigest()[:8]
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        fname = os.path.join(outdir, f"{stamp}-{h}.eml")
        with open(fname, "wb") as f:
            f.write(data)
        print(f"SAVED {fname} to={rcpttos}", flush=True)


if __name__ == "__main__":
    SinkHandler(("0.0.0.0", 1025), None)
    print("mail-sink listening on :1025", flush=True)
    asyncore.loop()
