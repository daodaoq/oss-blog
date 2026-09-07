# 测试记录与验收用例（任务7）

> 覆盖：功能测试(≥8) · 权限测试(≥4) · UI/主题测试(≥4) · 恢复测试(≥2) · gscan 输出 · Bug 记录
> 记录约定：每条含【前置 / 步骤 / 期望 / 实际 / 负责人】。实际列：`PASS`=已通过并留痕，`待执行(界面)`=需浏览器人工验证后补截图。
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
| F2 | 登录-失败 | F1 | 错误密码登录 | 拒绝，401/提示 | 待执行(界面) | sjk |
| F3 | 创建/发布文章并绑标签 | 已登录 | Admin API POST /posts 绑 tag | 前台可见 | PASS（seed 9 篇含标签） | sjk |
| F4 | 文章增删改 | F3 | 修改一篇、删除一篇 | 前台同步 | 待执行(界面) | sjk |
| F5 | 标签筛选页 | 有标签文章 | 访问 /tag/ghost-tag/ | 展示该标签文章 | PASS（200，见 tag2） | sjk |
| F6 | 会员发评论 | 会员已登录 | member POST /members/api/comments/ | 评论 published 且归属会员 | PASS（评论 id=…feeb，member=林小满） | sjk |
| F7 | 空评论拒绝 | 评论框 | 不输入直接提交 | 不允许，提示 | 待执行(界面，UI 校验) | sjk |
| F8 | 搜索命中 | 有内容 | 搜索"二次开发" | ≥1 命中且高亮 | PASS（冒烟 2 篇命中） | sjk |
| F9 | 搜索无结果提示 | 同上 | 搜乱词 `zzz…` | "未找到"提示不报错 | PASS（冒烟 0 命中，UI 空态待截图） | sjk |
| F10 | 空搜索 | 同上 | 空关键词 | 不检索不报错 | PASS（冒烟） | sjk |
| F11 | 评论计数 | 有评论文章 | 详情页 | 显示评论数 | 待执行(界面) | sjk |
| F12 | 会员注册(新用户) | Portal/OTC | 新邮箱发 magic link→验证 | 成为 free 会员 | 待执行(界面，链路脚本可用 member-login) | sjk |

## 2. 权限测试（≥4 条）

| # | 用例 | 期望 | 实际 |
|---|---|---|---|
| P1 | 匿名访客不能评论（需登录） | 评论接口/UI 引导登录 | 待执行(界面) |
| P2 | 匿名可浏览公开文章与搜索 | 200 可读 | PASS（curl 200） |
| P3 | 普通会员无后台写权限 | 访问 /ghost 被拒 | 待执行(界面) |
| P4 | 管理员拥有全部写权限 | 增删改文章/标签/会员成功 | PASS（Admin API） |

## 3. UI/主题测试（≥4 条）

| # | 用例 | 期望 | 实际 |
|---|---|---|---|
| U1 | 首页杂志布局（桌面 ≥1280） | 头条+双栏栅格、导航/页脚正常 | 待执行(界面·截图) |
| U2 | 移动端窄屏（≤420） | 单栏、无横向溢出 | 待执行(界面·截图) |
| U3 | 键盘访问搜索（`/` 或 `Ctrl+K`） | 弹层获得焦点、Esc 关闭 | 待执行(界面) |
| U4 | 超长标题/无封面文章渲染 | 折行正常、占位不破版 | 待执行(界面·截图) |
| U5 | gscan 主题校验 | 0 error | PASS（✓ Ghost 6.x，`docs/gscan-theme-output.txt`） |

## 4. 恢复测试（≥2 条）

| # | 用例 | 步骤 | 期望 | 实际 |
|---|---|---|---|---|
| R1 | 服务重启数据不丢 | `docker compose restart ghost` | 文章/评论仍在 | PASS（9 篇重启前后不变） |
| R2 | 导出→重建→导入恢复 | Admin 导出 db → 清库重建容器 → 导入 | 数据完整恢复 | 待执行（导出已可做，见下） |

恢复命令（任务8 前执行并存档）：
```bash
# 导出
curl -b runtime/.admin.cookies -H "Origin: http://localhost:2368" \
  http://localhost:2368/ghost/api/admin/db/ > runtime/backups/ghost-export.json
# 清库恢复演示：docker compose down -v 后 up，再用 Admin 后台 Settings→导出/导入导入该文件
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

## 6. 遗留（界面人工项）清单
F2/F4/F7/F11/F12、P1/P3、U1–U4、R2 —— 需要你在浏览器操作并截图，我会据此把 `待执行` 改为 `PASS(证据)`。
