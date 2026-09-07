# 现场 Live Demo 脚本（5–10 分钟）

> 原则：**真实本地软件演示**，不用 PPT/录屏顶替；有离线预案、不依赖外网 CDN。

## 演示前检查清单（提前 10 分钟做）
- [ ] `cd runtime && docker compose ps` → ghost/mail-sink 均 healthy
- [ ] 浏览器前台 http://localhost:2368 首屏正常
- [ ] 后台 http://localhost:2368/ghost 可登录（owner 邮箱+密码）
- [ ] 演示数据在位：`node tests/scripts/search-smoke.js` 全 PASS
- [ ] 关掉 Wi-Fi 也能演示的模块已验证（搜索/浏览走同源；会员邮件走本地 mail-sink）

## 流程（对着做，每步一句讲解）

| 段 | 时间 | 动作 | 讲解点 |
|---|---|---|---|
| 开场 | 0:30 | 打开前台，展示杂志首页/头版头条+栅格 | 这是基于 Casper 二次开发的 sjk-journal 主题 |
| 会员搜索 | 1:00 | 点 🔍 或按 `/`，输入"二次开发"→ 看高亮 | 自研全文搜索：同源 /rss/ 索引，零 CDN |
| 无结果态 | 0:30 | 输入乱词 `xyz` → 显示"未找到…"建议 | 失败状态友好，符合验收 AS-4 |
| 内容展示 | 1:00 | 点进一篇代码块文章 + 超长标题文章 | 详情页面包屑/排版/响应式 |
| 管理员发布 | 1:30 | 后台新建文章绑标签并发布 → 前台刷新可见 | Ghost Admin 原生能力（复用上游） |
| 会员评论 | 1:30 | 用已登录会员(或现场走 OTC)在文章评论 | 会员制 + 评论权限；mail-sink 演示无邮箱也能验证 |
| 自研扩展 | 1:00 | 强调搜索扩展的用户价值/非目标/边界 | 为何做主题层不改 Ghost 核心 |
| 数据不丢 | 1:00 | `docker compose restart ghost` 后刷新 | 文章/评论仍在（持久化） |
| Git 证据 | 1:00 | 展示 GitHub 提交历史 / PR / Issue / gscan 输出 | Feature 分支、自我 Code Review 记录 |
| 收尾 | 0:30 | 展示 README 一键复现 + 备份命令 | 换台电脑照 README 能跑 |

## 离线预案（断网也能讲）
- 页面无 jsdelivr 依赖部分（搜索走本站 /rss/）；Portal/Sodo 由 CDN 注入的会员弹层
  在断网时会降级 —— 改走 **mail-sink 的 OTC/magic link 直接登录**（`node scripts/member-login.js <email>` 可自动化），
  或演示前把浏览器会话登录好，演示时只做"刷新 + 评论"。
- 演示用本机浏览器缓存的站点，避免现场样式依赖外网字体；主题字体用系统字体栈。

## 可能被问到（准备回答）
- 为什么主题/上层扩展而不是改 Ghost 核心？→ 升级不被覆盖、边界清晰、可上游合入（见 docs/requirements.md §2）
- 会员为什么收不到邮件？→ 本地 mail-sink，邮件在 runtime/mail/*.eml
- 服务端全文搜索要不要做？→ 见 docs/requirements.md 思考题 3：一致性/隐私/部署复杂度
