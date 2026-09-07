# Ghost 项目结构与二次开发边界（任务3）

> 本文基于实际运行中的 Ghost 6.62.0（Docker 部署）整理，配合 `runtime/docker-compose.yml` 复现。

## 1. 目录地图

运行方式：Ghost 官方镜像 `ghost:6.62.0`，主进程代码位于容器镜像内 `/var/lib/ghost/versions/6.62.0`（由 `current` 符号链接指向）；**内容层（数据/主题/图片/日志）挂载到宿主机 `runtime/content/`**。

| 目录（容器内） | 宿主机对应 | 内容 | 可否修改 |
|---|---|---|---|
| `current/core/` | 镜像内（只读） | **Ghost 内核源码**：路由、数据库、权限、Admin API 等 | ❌ **禁止修改**（升级即被覆盖；改它即“改内核”） |
| `current/core/frontend/` | 镜像内（只读） | 前台渲染、Handlebars 引擎、内置 Content API 服务 | ❌ 禁止修改 |
| `content/themes/casper` | 通过符号链接指向内核内置 Casper | Ghost 官方默认主题（基线参考） | ⚠️ 参考为主，不直接改 |
| `content/themes/source` | 同上 | Ghost 官方 Source 主题 | ⚠️ 参考为主 |
| `content/themes/<自定义>/` | `runtime/content/themes/<自定义>/` | **学生自定义主题（开发落点 1）** | ✅ 允许（新增目录） |
| `content/data/ghost.db` | `runtime/content/data/ghost.db` | SQLite 数据库（文章/会员/设置/评论） | ⚠️ 数据文件，运行时写入，**不入 Git** |
| `content/images|files|media/` | `runtime/content/...` | 上传的图片、文件、媒体 | ✅ 运行写入，**不入 Git** |
| `content/logs/*.log` | `runtime/content/logs/` | Ghost 运行日志（http/错误） | ⚠️ 只读查阅，**不入 Git** |
| `content/settings/` | `runtime/content/settings/` | 站点路由/重定向等设置（yaml） | ✅ 运行写入 |
| `content/apps/` | `runtime/content/apps/` | 第三方集成 | ⚠️ 谨慎 |
| `content/public/` | `runtime/content/public/` | 生成的静态产物 / admin | 运行生成 |

> 依赖包 `node_modules`（pnpm 布局）位于容器 `current/` 内，属内核运行依赖，不修改、不提交。

## 2. 二次开发边界（红线）

实验核心：**只改自定义主题 + Content API 上层调用 + 扩展模块，禁止直接改 Ghost core 源码**。因此：

- ✅ 允许：`content/themes/<自定义主题>/` 里的 `.hbs`/`.css`/`.js`（主题层）
- ✅ 允许：在主题中编写基于 **Ghost Content API** 的前端脚本/组件（上层扩展，例如站内搜索、相关推荐）
- ✅ 允许：独立新增 Node 服务或上层脚本（放在仓库 `extensions/` 或主题内），通过公开 API 与 Ghost 交互
- ❌ 禁止：修改 `current/core/**`（数据库结构、认证、Admin、编辑器源码）
- ✅ 推荐：所有二次开发代码放在仓库 `theme/`、`extensions/` 并 git 追踪，运行时拷贝进容器挂载目录

> 这样做的原因与升级影响，见 `docs/requirements.md §2`：内核升级时二次开发成果挂在稳定接口上，不会被覆盖、可长期维护。

## 3. 一次完整浏览请求的数据流

```
访客浏览器
   │  GET /            (宿主机 :2368 → 容器 2368)
   ▼
Ghost 前台渲染层  current/core/frontend  (读取 content/themes/<主题>/*.hbs + data)
   │  主题模板通过模板上下文请求内容
   ▼
Ghost 内容服务  (current/core/server/services  — members/comments/posts)
   │
   ▼
Ghost Content/Admin API   (/ghost/api/content/* 公开只读、/ghost/api/admin/* 鉴权)
   │
   ▼
SQLite  content/data/ghost.db
```

- 访客浏览 / 搜索命中 → Content API（只读，走主题渲染）
- 登录 / 写作 / 评论 / 上传 → Admin API（会话 Cookie 鉴权）
- 会员体系（注册、评论者）→ Members 服务，登录验证邮件经 Mailpit 投递

## 4. Content API / Admin API 位置速查

| 接口 | 前缀 | 鉴权 | 用途 |
|---|---|---|---|
| Content API | `http://localhost:2368/ghost/api/content/` | Content API Key（只读） | 前台取文章/标签/作者，自定义扩展常用 |
| Admin API | `http://localhost:2368/ghost/api/admin/` | 会话 Cookie / Admin Key | 管理端全部写操作 |

> 后续任务会用 Admin API（携带会话 Cookie）脚本化创建演示数据，保证可重复测试（见 `tests/`）。

## 5. 版本与复现

- Ghost 内核版本：`6.62.0`（容器 `current/package.json` 实际读取确认）
- 运行载体：`ghost:6.62.0` 镜像，Compose 编排（`runtime/docker-compose.yml`）
- 数据层全部在 `runtime/content/`，删除容器重建不丢数据；备份=导出 json + 拷贝 content/（任务7验证）
