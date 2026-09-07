# 自我 Code Review 记录（合并前）

> 按实验要求：开 PR 前先做自我 Code Review，留下文字记录。本文件为 feature 分支合并前自查结论。

## PR 概览
- 分支：`feature/custom-theme`（主题二次开发 + 自主扩展搜索）→ 目标 `main`
- 涉及范围：`theme/`、`runtime/docker-compose.yml`、`runtime/mail-sink/`、`scripts/`、`tests/`、`docs/`
- 关联 Issue：#1（基线）、#2（搜索扩展）

## Review 清单与结论

### 正确性 / 功能
- [x] 主题通过 gscan（`docs/gscan-theme-output.txt`），无 error
- [x] 首页/文章/标签/404/搜索页均返回 200（curl 验证）
- [x] 搜索扩展冒烟测试全 PASS（`tests/scripts/search-smoke.js`）
- [x] 重启后数据不丢（9 篇文章前后一致）
- [ ] 交互(浏览器)项仍需人工验收（见 `tests/acceptance.md` U1–U4/F7 等）

### 边界与安全（"不改 Ghost 核心"红线）
- [x] 确认改动全部在 `theme/`、Compose、脚本、文档内；容器内 `current/core` 只读未动
- [x] 数据库/密钥/cookie/env 均在 .gitignore，未入库
- [x] 搜索做在主题层 + 公开 /rss/，无新增服务端攻击面
- [x] 搜索结果高亮先转义再插 `<mark>`，防 XSS 注入
- [x] search.js 对 RSS 拉取失败有兜底（不抛错、显示空态）

### 可维护性 / 升级友好
- [x] 主题保留 Ghost/Casper 原生模板结构，仅增量修改，后续跟随上游更新成本低
- [x] 自研样式/脚本独立文件（journal.css / search.js），回滚只需去掉引用
- [x] 脚本幂等（seed-demo.js 可重复执行）

### 自查发现并已修复的问题
1. **BUG(已修)**：`index.hbs` 栅格开关逻辑错误（用 @first 包 else 分支）→ 改用 `foreach from/limit` 拆分头条与其余（commit 内含）
2. **BUG(已修)**：gscan 报 `@custom` 未声明 / author.email 缺失 → 补回配置声明（commit `9cae776`）
3. **改进**：搜索快捷键 `/` 原先逻辑在已打开时不生效 → 改为任意时刻可开（Esc 单独关）
4. **已知限制（记录不隐藏）**：Ghost Admin 导出不含会员/评论 → 已文档化并给出整库文件备份方案（README §八 / acceptance R2）

## 结论
功能与边界自查通过，允许合并 `feature/custom-theme → main`；剩余人工 UI 项在浏览器验收后于
`tests/acceptance.md` 补 PASS 证据，不阻塞合并。合并后打 `v1.0-lab`。
