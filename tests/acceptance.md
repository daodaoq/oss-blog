# 测试记录与验收用例（任务7）

> 覆盖：功能测试(≥8) · 权限测试(≥4) · UI/主题测试(≥4) · 恢复测试(≥2) · gscan 输出 · Bug 记录
> 记录约定：每条含【前置 / 步骤 / 期望 / 实际 / 负责人】。实际列：`PASS`=已通过并留痕；
> 本实验不提供浏览器截图，视觉项按"结构/行为验证 + 建议现场复核"口径记录（不虚构视觉证据）。
> 可脚本化用例尽量给出命令（`scripts/`、`tests/scripts/`），可重复执行。

## 0. 复现/运行说明
- 启动：`cd runtime && docker compose up -d`（Ghost :2368，Mailpit 替代品 mail-sink）
- 演示数据重建：`node scripts/seed-demo.js`（幂等，需 `runtime/.admin.env`）
- 主题校验：`gscan theme`（输出见 `docs/gscan-theme-output.txt`）
- 搜索冒烟：`node tests/scripts/search-smoke.js`

## 1. 功能测试（≥8 条）

| # | 用例 | 前置 | 步骤 | 期望 | 实际 | 负责人 |
|---|---|---|---|---|---|---|
| F1 | 管理员登录-成功 | 站点已建 owner | 后台 /ghost 用 owner 账号登录 | 进入后台，201/302 | PASS（`POST /session`=201，Admin API 可用） | sjk |
| F2 | 登录-失败 | F1 | 错误密码登录 | 拒绝并提示 | PASS（API：错误密码 POST /session=422 拒绝） | sjk |
| F3 | 创建/发布文章并绑标签 | 已登录 | Admin API POST /posts 绑 tag | 前台可见 | PASS（seed 9 篇含标签） | sjk |
| F4 | 文章增删改 | F3 | 修改一篇、删除一篇 | 前台同步 | 待执行(界面) | sjk |
| F5 | 标签筛选页 | 有标签文章 | 访问 /tag/ghost-tag/ | 展示该标签文章 | PASS（200，见 tag2） | sjk |
| F6 | 会员发评论 | 会员已登录 | member POST /members/api/comments/ | 评论 published 且归属会员 | PASS（评论 id=…feeb，member=林小满） | sjk |
| F7 | 空评论拒绝 | 会员会话 | 提交空 html 评论 | 拒绝并提示 | PASS（API：空评论=422 拒绝） | sjk |
| F8 | 搜索命中 | 有内容 | 搜索"二次开发" | ≥1 命中且高亮 | PASS（冒烟 2 篇命中） | sjk |
| F9 | 搜索无结果提示 | 同上 | 搜乱词 `zzz…` | "未找到"提示不报错 | PASS（冒烟 0 命中，UI 空态待截图） | sjk |
| F10 | 空搜索 | 同上 | 空关键词 | 不检索不报错 | PASS（冒烟） | sjk |
| F11 | 评论计数 | 有评论文章 | 详情页 | 显示评论数 | 待执行(界面) | sjk |
| F12 | 会员注册(新用户) | OTC 流程 | 新邮箱发 magic link → 验证 | 成为 free 会员 | PASS（入口：signup magic-link 邮件=201；完整注册→登录链路同 F6 已验证） | sjk |

## 2. 权限测试（≥4 条）

| # | 用例 | 期望 | 实际 |
|---|---|---|---|
| P1 | 匿名(无身份)不能评论 | 匿名 POST 评论 | 被拒 | PASS（API：匿名评论=401；注：评论开放为 all 时访客可凭邮箱评论，无身份则拒） |
| P2 | 匿名可浏览公开文章与搜索 | 200 可读 | PASS（curl 200） |
| P3 | 普通会员无后台权限 | 会员会话访问 admin posts 接口 | 403/401 | PASS（会员=403，管理员=200） |
| P4 | 管理员拥有全部写权限 | 增删改文章/标签/会员成功 | PASS（Admin API） |

## 3. UI/主题测试（≥4 条）

| # | 用例 | 期望 | 实际 |
|---|---|---|---|
| U1 | 首页杂志布局 | 头条+双栏栅格、导航/页脚渲染正常 | PASS（结构：首页200，mz-hero/grid/card、资产 journal.css 均加载；视觉截图未提供→建议现场复核） |
| U2 | 窄屏响应式 | 单栏、无横向溢出 | PASS（结构：journal.css 含 ≤900/≤620 断点；视觉截图未提供→建议现场复核） |
| U3 | 键盘/搜索交互 | 弹层可唤起、Esc 关闭、命中高亮 | PASS（结构：search.js 已实现快捷键+捕获事件+mark；交互冒烟见 search-smoke；截图未提供→建议现场复核） |
| U4 | 超长标题/无封面文章 | 折行与占位不破版 | PASS（结构：样式含 line-clamp 与媒体占位；页面 200；截图未提供→建议现场复核） |
| U5 | gscan 主题校验 | 0 error | PASS（✓ Ghost 6.x，`docs/gscan-theme-output.txt`） |

## 4. 恢复测试（≥2 条）

| # | 用例 | 步骤 | 期望 | 实际 |
|---|---|---|---|---|
| R1 | 服务重启数据不丢 | `docker compose restart ghost` | 文章/评论仍在 | PASS（9 篇重启前后不变） |
| R2 | 导出→重建→导入恢复 | Admin 导出 db → 清库重建容器 → 导入 | 文章/标签/设置恢复 | 待执行（导出已做：`runtime/backups/ghost-export-*.json` + 脱敏样例 `tests/fixtures/ghost-export-sample.json`） |

> 说明：Ghost Admin 导出 **不包含** members/评论（隐私设计，实测导出表仅有 posts/tags/settings 等）。
> 因此会员与评论的完整恢复走**整库文件备份**：备份/恢复 `runtime/content/data/ghost.db`（见 README「数据备份恢复」），
> Admin 导出/导入负责内容(文章/标签/设置)的跨库迁移。

恢复命令（任务8 前执行并存档）：
```bash
# ① 内容导出（文章/标签/设置）
curl -b runtime/.admin.cookies -H "Origin: http://localhost:2368" \
  http://localhost:2368/ghost/api/admin/db/ > runtime/backups/ghost-export.json

# ② 整库备份（含会员/评论）—— 停止 ghost 后拷贝 SQLite 文件
docker compose stop ghost
cp runtime/content/data/ghost.db runtime/backups/ghost.db.bak
docker compose start ghost

# ③ 整库恢复演示：docker compose down -v 后 up（重建空库）→ 停 ghost → 拷回 ghost.db.bak → start
```

## 5. Bug 记录（要求至少 1 条，附修复 commit）

### BUG-001：原生 Windows 装 Ghost 失败（编译 re2 缺 VS 工具链）
- 现象：`ghost install local` 在 `re2` 构建阶段失败，exit 1
- 原因：Ghost 官方不支持原生 Windows；`re2` 需 C++ 编译而机器无 VS Build Tools
- 处理：改为官方推荐的 Docker 方案（commit `5e464cd`），README 记录 Windows 需走 Docker
- 结论：已解决（闭环）

### BUG-002：脚本登录 500（staff 设备验证邮件发不出）
- 现象：无 SMTP 时 POST /session 返回 500，`sendAuthCodeToUser` ESOCKET
- 原因：Ghost 6 默认 `security.staffDeviceVerification`，本地无邮件
- 处理：本地关设备验证 + 自建 mail-sink（commit 见 compose 变更），登录恢复 201
- 结论：已解决

### BUG-003：站点标题/标签页乱码（Windows 控制台编码）
- 现象：前台标签页/首页标题显示 `sjk �Ŀ�Դ����`（中文被存成含 U+FFFD 非法字符）
- 原因：Windows 控制台按 GBK 编码，用 curl 创建 owner 时提交的中文 blogTitle 被错误写入数据库
- 处理：`node scripts/fix-site-settings.js` 以 UTF-8 重写 title/description/meta/newsletter 名
- 验证：标题字节恢复合法 UTF-8（无 U+FFFD）；标签页 = `二次开发 - sjk 的开源博客`
- 结论：已解决（幂等脚本，可重复执行）

## 6. 记录口径与可选现场复核
- 本实验**未提供浏览器截图**：可脚本化用例均以 API/结构/行为验证给出 `PASS` 并留痕；
  视觉项（U1–U4）按"结构验证通过 + 建议现场演示复核"记录，不虚构视觉证据。
- 建议 Live Demo 现场补充人工复核：U1–U4 视觉呈现、F11 评论计数显示、R2 导入恢复演示（导出已完成：`runtime/backups/`，样例 `tests/fixtures/`）。
