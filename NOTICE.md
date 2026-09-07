# NOTICE · 上游来源与第三方资源许可证

本仓库是在开源软件基础上做的二次开发。按开源合规要求，逐项登记所有被引用/再分发的
上游项目、作者、来源链接与许可证。凡标注「上游」，版权归原作者/项目所有；「本项目新增」为 sjk 原创。

| 组件 | 来源 / 作者 | 仓库链接 | 许可证 | 用途与本仓库位置 |
|---|---|---|---|---|
| Ghost（运行应用） | TryGhost / Ghost Foundation | https://github.com/TryGhost/Ghost | MIT | 博客基线应用（6.62.0）；仅以官方 Docker 镜像运行，**未修改源码** |
| Casper（主题基线） | TryGhost / Ghost Foundation | https://github.com/TryGhost/Casper | MIT | 自定义主题 sjk-journal 的模板基线，见 `theme/`（保留其 LICENSE） |
| Ghost 官方 Docker 镜像 | Ghost / Docker Official Images | https://hub.docker.com/_/ghost | MIT（随上游） | `runtime/docker-compose.yml` 使用 `ghost:6.62.0` |
| python:3.11-slim 基础镜像 | Python 官方 / Docker Official Images | https://hub.docker.com/_/python | PSF License | mail-sink 收信服务基础镜像（`runtime/mail-sink/Dockerfile`） |
| gscan（主题校验工具） | TryGhost | https://github.com/TryGhost/gscan | MIT | 开发期校验主题（不随仓库分发，见 `docs/gscan-theme-output.txt`） |
| 默认站点图标/素材 | Ghost 初始化内容 | — | 随 Ghost | 运行时 `content/` 生成，已 gitignore |

## 本项目新增（sjk 原创，随仓库以 MIT 分发）
- `theme/assets/css/journal.css`、`theme/assets/js/search.js`、`theme/index.hbs` 杂志首页
  及对 `theme/default.hbs`、`theme/package.json` 等的二次修改；
- `runtime/mail-sink/`（Python SMTP 收信，基于 Python 标准库 smtpd）；
- `scripts/`、`tests/`、`docs/`（本实验文档与测试）。

## 分发说明
- 本仓库不捆绑 Ghost/Casper 之外的可执行二进制或商业化闭源素材；
- 主题 zip（`theme-packages/sjk-journal-1.0.0.zip`）内含 Casper 上游 MIT 源码片段，保留其版权声明；
- 复刻 Ghost 本身的部署，请遵循其许可证并保留其官方出处说明。

> 联系方式：sjk（仓库维护者）。如认为本登记有遗漏，欢迎提 Issue 指正。
