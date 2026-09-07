# 极简本地 SMTP 收信器，无第三方依赖，基于 python:3.11-slim（保留 smtpd 模块）
FROM python:3.11-slim

WORKDIR /srv
COPY sink.py /srv/sink.py

EXPOSE 1025
CMD ["python", "/srv/sink.py"]
