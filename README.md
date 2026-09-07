# sjk 的开源博客 · oss-blog

> 《开源软件与新技术》实验01：开源个人博客系统二次开发
> 基线：**[TryGhost/Ghost](https://github.com/TryGhost/Ghost)（MIT，Node.js 博客系统）**，固定版本 **6.62.0**
> 主题基线：**[TryGhost/Casper](https://github.com/TryGhost/Casper)**（MIT）→ 二次开发为「sjk-journal」杂志风主题

一个**本地可运行、可注册、可写作、可评论、可搜索**的个人博客软件成品。
二次开发边界严格限定在 **自定义主题 + Content API/上层扩展**，**未修改 Ghost 核心源码**。

---

## 一、项目简介与功能清单

| 类别 | 说明 |
|---|---|
| 前台 | 首页（杂志风：头版头条 + 双栏栅格）、文章列表/详情、标签页、会员注册/登录、评论区、搜索 |
| 后台 | Ghost Admin：写作/标签/会员/主题/设置（Ghost 原生） |
| 账号 | 管理员 owner + 普通会员（无密码、邮件 OTC/magic link 登录） |
| 评论 | 会员登录后可评论，匿名不可评论 |
| 搜索 | **自研站内全文搜索**：输入即搜、命中 `<mark>` 高亮、无结果友好提示、离线可用（`/` 或 `Ctrl+K` 唤起） |
| 主题 | sjk-journal：首页杂志栅格、导航与页脚重做、中文杂志排版、响应式（桌面/移动） |
| 邮件 | 本地 mail-sink（SMTP）接收会员登录/验证邮件，全程离线可演示 |
| 数据 | SQLite 持久化；Admin 导出/导入 + 整库文件备份两种恢复手段 |

预置演示数据：9 篇文章（含长标题 / 无封面 / 代码块 / 中文搜索词边界）、4 个标签、2 个会员账号（seed 脚本一键重建）。

---

## 二、技术栈与架构

```
浏览器 ──> Ghost 6.62.0（Docker 容器）
              ├─ 前台渲染  主题 content/themes/sjk-journal（Handlebars 模板 + 自研 JS/CSS）
              ├─ Members   注册/登录（OTC 邮件验证）→ 邮件落 mail-sink
              ├─ Comments  会员评论
              └─ 数据      SQLite：content/data/ghost.db
                          Content/Admin API（/ghost/api/content|admin/*）
```

- 运行载体：Docker Compose（`ghost:6.62.0` 官方镜像 + 自建 `mail-sink` 收信服务）
- 数据库：SQLite（本地零配置）
- 自定义主题：Handlebars + 原生 JS/CSS（无构建步骤）
- 辅助脚本：Node >= 18（仅用于 seed / 会员登录 / 冒烟测试）

> 为什么用 Docker：Ghost 官方**不支持原生 Windows**（原生安装依赖 C++ 编译会失败，见 `tests/acceptance.md BUG-001`），Windows 上官方推荐 Docker / WSL。

---

## 三、环境版本要求（"全新电脑复现"）

| 软件 | 版本 | 说明 |
|---|---|---|
| Docker | Desktop（任意较新版本） | 需要能 `docker compose`；Windows 建议 WSL2 后端 |
| Node.js | v18+（仅跑脚本用，运行博客不需要） | seed / 测试脚本 |

> 中国大陆网络：若拉取 Docker Hub 镜像慢，给 Docker 配置镜像源即可（本项目用的 `docker.m.daocloud.io`）。

---

## 四、安装与启停

```bash
# 1) 克隆
git clone git@github.com:daodaoq/oss-blog.git && cd oss-blog

# 2) 启动（首次会自动拉取 ghost:6.62.0 并初始化内容目录）
cd runtime
docker compose up -d          # 前台 http://localhost:2368 后台 http://localhost:2368/ghost
docker compose ps             # 查看健康状态

# 3) 首次使用：浏览器打开 http://localhost:2368/ghost 创建管理员 owner
#    （邮箱即登录名，密码自设，本地已关闭"设备验证邮件"）

# 4) （可选）重建演示数据：准备凭据
cp runtime/.admin.env.example runtime/.admin.env   # 填入上面的 owner 邮箱/密码
cd .. && node scripts/seed-demo.js                 # 幂等，可反复执行

# 停止 / 重启 / 查看日志
docker compose stop | start
docker compose logs -f ghost
```

端口：前台/后台 `2368`；本地邮件 `mail-sink`（容器内部 SMTP 1025，邮件落 `runtime/mail/*.eml`，Web 查看可自行配置 Mailpit 类工具）。

---

## 五、Demo 操作流程（5–10 分钟）

见 `docs/live-demo.md`。一句话版：会员登录搜索 → 管理员发布带标签文章 → 会员评论 → 演示自研搜索（含无结果提示）→ 展示 Git/PR 证据 → 演示数据重启不丢。

---

## 六、二次开发改动清单（本仓库相对上游）

**A. 主题 sjk-journal（源自 Casper，重做）** —— `theme/`
| 文件 | 改动 |
|---|---|
| `theme/package.json` | 主题身份、主题设置项精简（保留模板引用的 @custom） |
| `theme/default.hbs` | 引入自研样式 journal.css；加入**站内搜索弹层**；页脚语义保留 |
| `theme/index.hbs` | 首页重做为**杂志头条 + 双栏栅格**（`mz-hero/mz-grid/mz-card`） |
| `theme/assets/css/journal.css` | **自研样式表**：设计令牌、导航/首页/卡片/文章/搜索/响应式 |
| `theme/assets/js/search.js` | **自研搜索**：`/rss/` 本地索引、命中高亮、无结果建议、快捷键（扩展功能） |
| `partials/post-card.hbs` 等 | 保留 Casper 基础，配合新卡片样式 |

**B. 自主扩展：站内全文搜索增强** —— 见 `docs/extension-search.md`
**C. 运行层** —— `runtime/docker-compose.yml`、`runtime/mail-sink/`、`scripts/`、`tests/`
**未改动**：Ghost 内核（容器内只读，升级不冲突）。

---

## 七、测试方法

- 验收用例与结果记录：`tests/acceptance.md`（功能/权限/UI/恢复 + Bug 记录）
- 主题校验：`gscan theme`（输出见 `docs/gscan-theme-output.txt`）✓ Ghost 6.x
- 搜索冒烟：`node tests/scripts/search-smoke.js`
- 演示数据：`node scripts/seed-demo.js`（幂等）
- 会员登录自动化：`node scripts/member-login.js <email>`（读 mail-sink 里 OTC 完成登录）

---

## 八、数据备份与恢复

```bash
# 内容导出（文章/标签/设置；不包含会员/评论——Ghost 设计如此）
curl -b runtime/.admin.cookies -H "Origin: http://localhost:2368" \
  http://localhost:2368/ghost/api/admin/db/ > runtime/backups/ghost-export.json

# 整库备份（含会员/评论）——停 ghost 后拷贝 SQLite
docker compose stop ghost
cp runtime/content/data/ghost.db runtime/backups/ghost.db.bak
docker compose start ghost

# 整库恢复演示：docker compose down -v（清空）→ up 重建空库 → 停 ghost → 拷回 .bak → start
```
后台导入：`Settings → 全站 → 导出/导入`（导入 `ghost-export.json` 内容）。样例见 `tests/fixtures/ghost-export-sample.json`。

---

## 九、上游来源与许可证（详见 NOTICE.md）

| 组件 | 上游 | 许可证 |
|---|---|---|
| Ghost | [TryGhost/Ghost](https://github.com/TryGhost/Ghost) v6.62.0 | MIT |
| 主题基线 | [TryGhost/Casper](https://github.com/TryGhost/Casper) v5.x | MIT |
| 基础镜像 | docker `ghost:6.62.0` / `python:3.11-slim` | 见上游 |
| 本仓库二次开发 | sjk | MIT（见 LICENSE / NOTICE.md） |

---

## 十、安全注意事项

- 本地数据库、`.admin.env`、`ghost-keys.env`、`.admin.cookies` 均被 `.gitignore` 排除，**严禁提交**；
- 首次使用请在后台**修改/设置强密码**并关闭公开注册（`Settings → 会员`)到可控状态再对外；
- 本仓库为教学/个人演示用途，默认关闭 staff 设备验证与使用本地邮件接收器，**不建议直接公网部署**；
- 若对外部署，请参考 [Ghost 官方文档](https://ghost.org/docs/config/) 配置真实 SMTP、HTTPS 与备份。
