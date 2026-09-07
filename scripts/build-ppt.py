#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-ppt.py —— 为《开源软件与新技术》实验01 生成展示 PPT（.pptx）
运行：py scripts/build-ppt.py
输出：docs/slides/实验01_开源博客二次开发_展示.pptx
依赖：python-pptx  (pip install python-pptx)
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

INK = RGBColor(0x1A, 0x1A, 0x1A)
ACCENT = RGBColor(0xC0, 0x39, 0x2B)
GREY = RGBColor(0x55, 0x52, 0x4D)
LIGHT = RGBColor(0xF5, 0xF2, 0xEC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "微软雅黑"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def _set(run, size=18, bold=False, color=INK, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    r = run._r
    ea = r.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}rPr")
    return run


def box(slide, x, y, w, h, fill=None):
    shp = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill if fill else LIGHT
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def txt(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for ln in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if isinstance(ln, tuple):
            text, size, bold, color, bullet = ln
        else:
            text, size, bold, color, bullet = ln, 18, False, INK, False
        prefix = "• " if bullet else ""
        run = p.add_run()
        run.text = prefix + text
        _set(run, size, bold, color)
    return tb


def header(slide, kicker, title, sub=None):
    bar = box(slide, 0, 0, 13.333, 0.14, ACCENT)
    txt(slide, 0.55, 0.42, 12, 0.4, [(kicker, 13, True, ACCENT, False)])
    txt(slide, 0.55, 0.78, 12, 0.9, [(title, 30, True, INK, False)])
    if sub:
        txt(slide, 0.57, 1.62, 12, 0.4, [(sub, 13, False, GREY, False)])


def bullets(slide, items, y=2.1, size=17, gap=0.42):
    lines = [(t, size, False, INK, True) for t in items]
    txt(slide, 0.7, y, 12, 5.0, lines)


def cover():
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, 13.333, 7.5, INK)
    box(s, 0, 5.55, 13.333, 0.06, ACCENT)
    txt(s, 0.8, 1.5, 11.7, 1.8, [("开源个人博客系统的二次开发", 44, True, WHITE, False)], PP_ALIGN.LEFT)
    txt(s, 0.82, 3.1, 11, 0.6, [("—— 基于 TryGhost/Ghost 6.62.0（Docker 本地部署）", 22, False, RGBColor(0xE8, 0xE0, 0xD4), False)])
    txt(s, 0.82, 5.8, 11, 1.2, [
        ("《开源软件与新技术》实验01 · 期末展示", 16, False, WHITE, False),
        ("汇报人：sjk    仓库：github.com/daodaoq/oss-blog    版本：v1.0-lab", 14, False, RGBColor(0xC9, 0xC4, 0xBB), False),
    ])


def section(num, title, sub=""):
    s = prs.slides.add_slide(BLANK)
    header(s, f"PART {num}", title, sub)


def simple(title, items, note=None, **kw):
    s = prs.slides.add_slide(BLANK)
    header(s, "实验01 · 二次开发展示", title)
    bullets(s, items, **kw)
    if note:
        txt(s, 0.7, 6.7, 12, 0.5, [(note, 12, False, GREY, False)])
    return s


def end():
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, 13.333, 7.5, INK)
    txt(s, 0.8, 2.7, 11.7, 1, [("谢谢观看 · 欢迎提问", 40, True, WHITE, False)], PP_ALIGN.LEFT)
    txt(s, 0.8, 4.0, 11.7, 0.6, [("谢谢大家", 18, False, RGBColor(0xD8, 0xD0, 0xC4), False)])


YELLOW = RGBColor(0xFF, 0xF3, 0xC4)


def shot_slide(no, title, fname, how, extra_note=""):
    """截图占位页：黄框占位 + 该怎么截的步骤说明（同步写入幻灯片备注）"""
    s = prs.slides.add_slide(BLANK)
    header(s, "截图证据页", f"截图 {no}｜{title}", "在下方黄框里放入你自己的实拍截图（怎么截见下方与本页备注）")
    box(s, 2.15, 1.9, 9.03, 2.7, YELLOW)
    txt(s, 2.3, 2.05, 8.7, 0.6, [("📷 [ 在此放入截图 ]", 20, True, INK, False)], PP_ALIGN.CENTER)
    txt(s, 2.3, 2.75, 8.7, 0.5, [(f"建议保存为 docs/screenshots/{fname}", 14, False, GREY, False)], PP_ALIGN.CENTER)
    lines = [(t, 14, False, INK, True) for t in how]
    txt(s, 0.7, 5.05, 12.0, 2.1, lines)
    notes = "📸 截图方法：\n" + "\n".join("- " + t for t in how)
    if extra_note:
        notes += "\n备注：" + extra_note
    s.notes_slide.notes_text_frame.text = notes
    return s


# ==================== 页面内容 ====================
cover()

simple("目录 / Agenda", [
    "项目目标与验收场景（AS-1 ~ AS-6）",
    "技术选型：Ghost 路线 vs RealWorld 路线",
    "总体架构与运行环境（Docker + SQLite + mail-sink）",
    "系统功能演示：写作 / 会员 / 评论 / 搜索",
    "二次开发：sjk-journal 杂志风主题 + 自研全文搜索",
    "测试与数据恢复 / Git 开源过程 / 交付物",
])

simple("项目目标与验收场景", [
    "交付：一个本地可运行、可注册、可写作、可评论、可搜索的个人博客软件成品",
    "六条验收场景（AS）——来自基线 Issue #1：",
    "   AS-1 管理员写作发布并绑定标签",
    "   AS-2 管理员 + 普通会员两类账号，会员可登录",
    "   AS-3 会员可在文章下评论（空评论被拒）",
    "   AS-4 关键词搜索命中 + 无结果有友好提示",
    "   AS-5 首页/列表/详情/标签/登录/评论/搜索全站 + 移动端可用",
    "   AS-6 重启不丢数据，支持导出/导入恢复",
])

simple("技术选型：为什么用 Ghost，为什么不动它的核心", [
    "候选 A：RealWorld 规范 → 需自建认证/数据库/编辑器等全部核心（2学时难成MVP）",
    "候选 B：TryGhost/Ghost（MIT，Node 完整博客产品）→ 复用成熟核心，✅ 采用",
    "二次开发边界 = 自定义主题 + Content API/上层扩展；禁止改 Ghost core 源码",
    "收益：内核升级不被覆盖、许可证边界清晰、可用 Git diff 界定本人工作量",
    "（对应 PDF：不允许“仅启动原版/共用代码/只交报告”就算完成）",
])

section(2, "总体架构与运行环境")
s = prs.slides.add_slide(BLANK)
header(s, "总体架构", "浏览器 → Ghost 6.62.0（Docker）→ SQLite")
lines = [
    "前台渲染：自定义主题 content/themes/sjk-journal（Handlebars + 自研 JS/CSS）",
    "会员体系：Members 注册/登录（邮件验证码/魔法链接）",
    "评论：会员登录后评论；匿名无身份被拒（API 401）",
    "邮件：本地 mail-sink 接收（网页收件箱 :8025，可点击登录链接）",
    "数据：SQLite content/data/ghost.db（重启不丢，实测验证）",
    "运行：docker compose up -d → 前台 :2368 / 后台 :2368/ghost",
]
txt(s, 0.7, 2.1, 12, 4, [(t, 17, False, INK, True) for t in lines])
txt(s, 0.7, 6.4, 12, 0.6, [("关键点：二次开发全部落在主题与上层脚本，容器内 Ghost 内核只读未改。", 14, True, ACCENT, False)])

simple("功能演示（写作 / 会员 / 评论 / 搜索）", [
    "演示数据：9 篇文章（长标题 / 无封面 / 代码块 / 中文搜索词边界）+ 4 标签 + 2 会员",
    "管理员：后台写作→绑定标签→发布→前台可见",
    "会员：网页收件箱点登录链接（一键），即可评论",
    "搜索：按 / 或点 🔍，命中高亮 <mark>、无结果友好提示，离线可用",
    "数据不丢：docker compose restart ghost 后 9 篇文章仍在",
    "注：此处可替换为实拍截图（首页 / 文章 / 搜索 / 评论）",
])

section(3, "二次开发清单 · 主题")
simple("sjk-journal 主题（源自 Casper，明显重做）", [
    "首页：杂志式“头版头条 + 双栏栅格”（theme/index.hbs 重写）",
    "详情页：新增面包屑“首页/标签/正文”，与阅读栏对齐",
    "样式：自研 assets/css/journal.css（设计令牌/响应式/搜索弹层）",
    "导航/页脚：细黑边杂志头部 + 深色页脚重做",
    "证据：gscan 主题校验 ✓ 兼容 Ghost 6.x（docs/gscan-theme-output.txt）",
    "证据：主题相对上游 Casper 改动清单 docs/theme-diff-vs-casper.txt",
])

simple("自主扩展：站内全文搜索增强", [
    "用户价值：把已发布内容变成“可被找到”；反馈即时、离线可用",
    "实现：前端拉 /rss/ 建本地索引（标题+摘要+标签），同源、零 CDN",
    "能力：输入即搜、命中 <mark> 高亮、无结果给出建议、/ 或 Ctrl+K 唤起",
    "失败态：空输入不检索、RSS 异常显示空态不报错",
    "边界：全部在 theme/ 内，未改 Ghost 核心（git diff 可见）",
    "冒烟测试：tests/scripts/search-smoke.js 全 PASS",
])

section(4, "测试 · Git 过程 · 交付")
simple("测试与数据恢复", [
    "验收用例 tests/acceptance.md：功能 12 + 权限 4 + UI 5 + 恢复 2（含 Bug 记录×3）",
    "已自动化留痕：错误密码拒绝、匿名评论 401、空评论 422、会员越权 403",
    "数据导出/导入 + 整库备份双通道（导出含 20 表，样例已脱敏）",
    "Bug 闭环：Windows 原生编译失败→Docker（BUG-001）；登录 500→本地关设备验证+mail-sink（BUG-002）；标题乱码→UTF-8 重写（BUG-003）",
])
simple("Git 开源过程与协作证据", [
    "Feature 分支工作流：feature/custom-theme（主题+搜索）、feature/lab-finishing（收尾）",
    "GitHub：Issue #1（基线）、#2（搜索扩展）均已 CLOSED；PR #4 已 MERGED（Closes #1 #2）",
    "合并前自我 Code Review：docs/self-code-review.md",
    "≥5 条有意义 commit，标签 v1.0-lab",
    "NOTICE.md 登记上游（Ghost / Casper MIT）与本仓库原创部分",
])
simple("交付物与一键复现", [
    "仓库：github.com/daodaoq/oss-blog（main @ v1.0-lab）",
    "全新电脑复现：README §四 —— clone → docker compose up -d → 创建管理员 → seed",
    "主题可安装包：theme-packages/sjk-journal-1.0.0.zip（后台上传可装）",
    "脚本：seed-demo（重建数据）、member-login（会员登录）、fix-site-settings（编码修复）",
    "PPT 内截图处：可直接替换为你现场的浏览器实拍，效果更佳",
])

simple("总结 / 心得体会", [
    "在不改核心的前提下做出“像样”的产品：主题 + 上层扩展足够撑起可见的二次开发",
    "踩坑即学习：原生 Windows 装 Ghost → Docker；会员邮件 → 自建收件箱；中文 → 编码陷阱",
    "全程留痕：Issue/PR/commit/测试/文档，让“哪些是上游、哪些是我做的”一目了然",
])

# ---- 截图占位页清单（每个需要放实拍图的地方：黄框 + 怎么截）----
shot_slide(1, "首页 · 桌面端", "U1-home-desktop.png", [
    "打开浏览器访问 http://localhost:2368（先确保 docker compose ps 里 ghost 为 healthy）",
    "把窗口最大化（F11）",
    "Windows 截图：Win + Shift + S → 框选整个页面 → 粘贴保存为 U1-home-desktop.png",
    "（或 F12 开发者工具 → 右上 ⋮ → Capture full size screenshot，可截整页含滚动）",
], "这张最能体现杂志风首页：头版头条大图 + 双栏栅格 + 顶部细黑边导航。")
shot_slide(2, "首页 · 手机窄屏（响应式）", "U2-home-mobile.png", [
    "在首页按 F12 打开开发者工具",
    "左上角点“手机图标”（或 Ctrl+Shift+M）切换设备模拟",
    "设备选 iPhone 12 / 375×812（或任意 <420px 宽度）",
    "Win + Shift + S 框选截图保存为 U2-home-mobile.png",
], "验证移动端单栏、无横向滚动条（验收用例 U2）。")
shot_slide(3, "文章详情页（面包屑 + 无封面/长标题边界）", "U3-article.png", [
    "点击任一篇“无封面”或“超长标题”文章进入详情",
    "确认标题上方有面包屑“首页 / 标签 / 正文”，且与正文对齐",
    "Win + Shift + S 框选首屏（含面包屑与标题）保存为 U3-article.png",
], "演示文章可用：超长标题 / 无封面 各截一张最好。")
shot_slide(4, "自研搜索 · 命中高亮", "U4-search-hit.png", [
    "前台按 / 或点右上角 🔍 唤起搜索弹层",
    "输入“二次开发”并回车",
    "截图：结果标题里命中词被黄色 <mark> 高亮 → U4-search-hit.png",
], "对应验收 AS-4 与自主扩展 Issue #2 的“命中高亮”。")
shot_slide(5, "自研搜索 · 无结果提示", "U5-search-empty.png", [
    "再次按 / 唤起搜索",
    "输入一个乱词，如 zzz 不存在关键词",
    "截图：出现“未找到与…相关的文章”+ 建议文案 → U5-search-empty.png",
], "对应验收 AS-4“无搜索结果要有提示”。")
shot_slide(6, "会员评论", "U6-comment.png", [
    "网页收件箱 http://localhost:8025 打开最新邮件 → 点“点击登录”以会员身份登录（如 林小满）",
    "回到某篇文章底部评论区，写一条评论并提交",
    "截图：显示该会员头像/昵称的评论 → U6-comment.png",
    "（想展示“空评论被拒”，再空提交一次截报错提示）",
], "登录前需先在站点对该会员邮箱触发一次“登录”，邮件才会出现在 :8025。")
shot_slide(7, "后台写作发布（可选加分）", "U7-admin-editor.png", [
    "打开 http://localhost:2368/ghost 并用管理员登录",
    "新建文章 → 写标题/正文 → 右侧选一个标签 → 点“发布”",
    "截后台编辑器画面 → U7-admin-editor.png",
], "证明“管理员可写作并绑定标签”为真实演示而非截图搬运。")

end()

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "slides")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "实验01_开源博客二次开发_展示_v2.pptx")
prs.save(out)
print("PPT saved:", os.path.abspath(out), "slides:", len(prs.slides._sldIdLst))
