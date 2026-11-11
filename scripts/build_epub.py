#!/usr/bin/env python3
"""Build publication-grade EPUB 3.0 for 《秦汉那些事儿：帝国初生的四百年》."""

import datetime
import html
import os
import random
import re
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import markdown
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
COVER_PATH = DOCS_DIR / "assets" / "cover.jpg"
EPUB_PATH = DOCS_DIR / "downloads" / "qinhan-book.epub"

BOOK_UUID = "urn:uuid:8f4e2c1a-9b7d-4e3f-a6c5-202611110440"
BOOK_TITLE = "秦汉那些事儿：帝国初生的四百年"
BOOK_SUBTITLE = "帝国初生的四百年"
BOOK_MAIN_TITLE = "秦汉那些事儿"
BOOK_AUTHOR = "Ying Wang"
BOOK_LANG = "zh-CN"
BOOK_DESC = (
    "一部用现代白话拆解中华第一帝国兴衰的长篇历史叙事（全书六卷二十四章完结）。"
    "从公元前259年邯郸小巷里的秦国质子，讲到公元220年繁阳受禅台上的末代汉帝——"
    "叙事横跨近四百八十年（自前221年大秦一统算起恰为四百四十年帝国周期），"
    "还原硬核史料背后的人性博弈、制度逻辑与家国悲欢。"
)

VOLUMES = [
    {
        "id": "vol01",
        "num": "第一卷",
        "title": "铁血大秦",
        "era": "公元前 259 年 — 公元前 207 年",
        "desc": "超级帝国的狂飙、沙丘惊变与大泽乡烽火",
        "chapters": [
            ("ch01", "01-qin-shihuang.md", "第一章 从邯郸肉票到千古一帝"),
            ("ch02", "02-shaqiu-collapse.md", "第二章 失控的战车与沙丘鲍鱼"),
            ("ch03", "03-dazexiang-uprising.md", "第三章 大泽乡的泥水与乱世合伙人"),
        ],
    },
    {
        "id": "vol02",
        "num": "第二卷",
        "title": "楚汉惊雷",
        "era": "公元前 207 年 — 公元前 195 年",
        "desc": "鸿门宴、暗度陈仓、背水破赵与霸王别姬",
        "chapters": [
            ("ch04", "04-hongmen-chencang.md", "第四章 鸿门宴上的微表情与暗度陈仓"),
            ("ch05", "05-pengcheng-hanxin.md", "第五章 打不死的刘邦与韩信封神"),
            ("ch06", "06-gaixia-weiyang.md", "第六章 霸王别姬与未央宫的杀机"),
        ],
    },
    {
        "id": "vol03",
        "num": "第三卷",
        "title": "文景韬晦",
        "era": "公元前 195 年 — 公元前 141 年",
        "desc": "吕后铁腕、文帝治国智慧与七国之乱",
        "chapters": [
            ("ch07", "07-lvhou-daiwang.md", "第七章 吕后铁腕与代王进京"),
            ("ch08", "08-wenjing-qiguo.md", "第八章 抠门天子与七国烽烟"),
        ],
    },
    {
        "id": "vol04",
        "num": "第四卷",
        "title": "汉武铁骑",
        "era": "公元前 141 年 — 公元前 48 年",
        "desc": "卫霍封狼居胥、张骞凿空、巫蛊血案与昭宣中兴",
        "chapters": [
            ("ch09", "09-liuche-weixing.md", "第九章 少年刘彻的野心与独尊儒术"),
            ("ch10", "10-weihuo-mobei.md", "第十章 双星闪耀与封狼居胥"),
            ("ch11", "11-zhangqian-shiji.md", "第十一章 凿空西域与算盘上的帝国"),
            ("ch12", "12-wugu-luntai.md", "第十二章 巫蛊血案与轮台罪己"),
            ("ch13", "13-huoguang-xuandi.md", "第十三章 权臣霍光与病已逆袭"),
        ],
    },
    {
        "id": "vol05",
        "num": "第五卷",
        "title": "日落西京与光武重光",
        "era": "公元前 48 年 — 公元 88 年",
        "desc": "穿越者王莽改制、昆阳神迹、云台将星与班超定西域",
        "chapters": [
            ("ch14", "14-yuandi-wangshi.md", "第十四章 柔弱天子与王氏坐大"),
            ("ch15", "15-wangmang-utopia.md", "第十五章 穿越者王莽的魔幻乌托邦"),
            ("ch16", "16-liuxiu-kunyang.md", "第十六章 庄稼汉刘秀与昆阳神迹"),
            ("ch17", "17-yuntai-roudao.md", "第十七章 云台将星与柔道治国"),
            ("ch18", "18-mingzhang-banchao.md", "第十八章 明章之治与班超孤悬绝域"),
        ],
    },
    {
        "id": "vol06",
        "num": "第六卷",
        "title": "东京残照",
        "era": "公元 88 年 — 公元 220 年",
        "desc": "外戚宦官轮盘赌、党锢悲歌、董卓焚洛与汉室落幕",
        "chapters": [
            ("ch19", "19-waiqi-huanguan.md", "第十九章 短命皇帝与外戚宦官轮盘赌"),
            ("ch20", "20-qingliu-danggu.md", "第二十章 清流热血与党锢绝响"),
            ("ch21", "21-huangjin-dongzhuo.md", "第二十一章 黄巾惊雷与董卓焚洛"),
            ("ch22", "22-changan-xuchang.md", "第二十二章 长安废墟与许昌棋局"),
            ("ch23", "23-yidai-xunyu.md", "第二十三章 衣带诏之血与荀彧之死"),
            ("ch24", "24-shouchantai-finale.md", "第二十四章 受禅台上的背影与四百年回响"),
        ],
    },
]

MD_TO_XHTML = {"00-outline.md": "ch00-outline.xhtml"}
for vol in VOLUMES:
    for cid, md_name, _ in vol["chapters"]:
        MD_TO_XHTML[md_name] = f"{cid}.xhtml"


def load_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    songti = "/System/Library/Fonts/Supplemental/Songti.ttc"
    index_map = {"black": 0, "bold": 1, "light": 3, "regular": 6, "tc_bold": 2}
    if os.path.exists(songti):
        return ImageFont.truetype(songti, size, index=index_map.get(weight, 6))
    for fallback in [
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]:
        if os.path.exists(fallback):
            return ImageFont.truetype(fallback, size)
    return ImageFont.load_default()


def draw_centered_text(draw: ImageDraw.ImageDraw, width: int, y: int, text: str, font, fill, tracking: int = 0):
    if tracking <= 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) / 2, y), text, font=font, fill=fill)
        return
    chars = list(text)
    widths = [draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] for ch in chars]
    total_w = sum(widths) + tracking * (len(chars) - 1)
    x = (width - total_w) / 2
    for ch, cw in zip(chars, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += cw + tracking


def generate_cover(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    W, H = 1600, 2400
    img = Image.new("RGB", (W, H), (20, 18, 16))
    draw = ImageDraw.Draw(img)

    # Subtle vertical gradient + bamboo-slip ruling lines (秦汉简牍暗纹)
    for y in range(H):
        t = y / H
        r = int(24 - 8 * t)
        g = int(20 - 6 * t)
        b = int(18 - 5 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    for x in range(140, W - 120, 64):
        draw.line([(x, 120), (x, H - 120)], fill=(33, 28, 24), width=2)

    # Subtle top & bottom cinnabar glow bands
    for i in range(220):
        alpha = (220 - i) / 220.0
        y = 120 + i
        c_r = int(22 + 32 * alpha * 0.45)
        c_g = int(19 + 8 * alpha * 0.45)
        c_b = int(17 + 6 * alpha * 0.45)
        draw.line([(120, y), (W - 120, y)], fill=(c_r, c_g, c_b))

    gold = (198, 161, 91)
    gold_dim = (132, 106, 60)
    ivory = (244, 236, 224)
    ivory_muted = (195, 184, 168)
    cinnabar = (166, 38, 30)

    # Outer & inner classical Han borders
    m1 = 84
    m2 = 104
    draw.rectangle([m1, m1, W - m1, H - m1], outline=gold, width=4)
    draw.rectangle([m2, m2, W - m2, H - m2], outline=gold_dim, width=2)

    # Corner geometric motifs (汉砖回纹角花)
    cs = 38
    for cx, cy, sx, sy in [
        (m2, m2, 1, 1),
        (W - m2, m2, -1, 1),
        (m2, H - m2, 1, -1),
        (W - m2, H - m2, -1, -1),
    ]:
        draw.rectangle(
            [min(cx, cx + sx * cs), min(cy, cy + sy * cs), max(cx, cx + sx * cs), max(cy, cy + sy * cs)],
            outline=gold,
            width=2,
        )
        draw.rectangle(
            [
                min(cx + sx * 10, cx + sx * 24),
                min(cy + sy * 10, cy + sy * 24),
                max(cx + sx * 10, cx + sx * 24),
                max(cy + sy * 10, cy + sy * 24),
            ],
            fill=cinnabar,
        )

    # Top chronicle strapline
    font_strap = load_font(34, "regular")
    draw_centered_text(draw, W, 230, "公元前 259 — 公元 220  ·  全本六卷二十四章", font_strap, gold, tracking=6)
    draw.line([(W // 2 - 280, 298), (W // 2 + 280, 298)], fill=gold_dim, width=2)

    # Central title plaque (深玄底压纹牌匾，让主标题更稳重醒目)
    plaque_top, plaque_bot = 430, 1520
    draw.rectangle([200, plaque_top, W - 200, plaque_bot], fill=(18, 16, 14), outline=gold_dim, width=2)
    draw.rectangle([216, plaque_top + 16, W - 216, plaque_bot - 16], outline=(62, 50, 34), width=1)

    # Main title: 秦汉 / 那些事儿
    font_main_1 = load_font(186, "black")
    font_main_2 = load_font(148, "black")
    draw_centered_text(draw, W, 520, "秦汉", font_main_1, ivory, tracking=36)
    draw_centered_text(draw, W, 760, "那些事儿", font_main_2, ivory, tracking=18)

    # Cinnabar decorative rule + diamond
    rule_y = 1005
    draw.line([(340, rule_y), (W - 340, rule_y)], fill=cinnabar, width=5)
    cx = W // 2
    draw.polygon([(cx, rule_y - 16), (cx + 16, rule_y), (cx, rule_y + 16), (cx - 16, rule_y)], fill=gold)

    # Subtitle
    font_sub = load_font(68, "bold")
    draw_centered_text(draw, W, 1075, "帝国初生的四百年", font_sub, gold, tracking=14)

    # Classical Cinnabar Seal Stamp (朱文方印：秦漢長歌)
    seal_size = 156
    sx = (W - seal_size) // 2
    sy = 1245
    draw.rectangle([sx, sy, sx + seal_size, sy + seal_size], fill=cinnabar)
    draw.rectangle([sx + 8, sy + 8, sx + seal_size - 8, sy + seal_size - 8], outline=ivory, width=3)
    font_seal = load_font(54, "tc_bold")
    # 2x2 seal layout (traditional right-to-left columns: 秦漢 / 史鑑), centered per quadrant
    inner = seal_size - 16
    q = inner / 2
    quadrants = [
        ("秦", sx + 8 + q * 1.5, sy + 8 + q * 0.5),
        ("漢", sx + 8 + q * 1.5, sy + 8 + q * 1.5),
        ("史", sx + 8 + q * 0.5, sy + 8 + q * 0.5),
        ("鑑", sx + 8 + q * 0.5, sy + 8 + q * 1.5),
    ]
    for ch, qcx, qcy in quadrants:
        bb = draw.textbbox((0, 0), ch, font=font_seal)
        cw, ch_h = bb[2] - bb[0], bb[3] - bb[1]
        draw.text((qcx - cw / 2 - bb[0], qcy - ch_h / 2 - bb[1]), ch, font=font_seal, fill=ivory)
    # Subtle crosshair hairlines inside seal
    draw.line([(sx + seal_size // 2, sy + 16), (sx + seal_size // 2, sy + seal_size - 16)], fill=(195, 72, 62), width=1)
    draw.line([(sx + 16, sy + seal_size // 2), (sx + seal_size - 16, sy + seal_size // 2)], fill=(195, 72, 62), width=1)

    # Six-volume keywords showcase
    font_vol = load_font(34, "regular")
    draw_centered_text(
        draw, W, 1650, "铁血大秦  ·  楚汉惊雷  ·  文景韬晦", font_vol, ivory_muted, tracking=4
    )
    draw_centered_text(
        draw, W, 1716, "汉武铁骑  ·  光武重光  ·  东京残照", font_vol, ivory_muted, tracking=4
    )

    draw.line([(W // 2 - 160, 1840), (W // 2 + 160, 1840)], fill=gold_dim, width=2)

    # Tagline & Author
    font_tag = load_font(32, "light")
    draw_centered_text(draw, W, 1900, "硬核史料打底 · 现代白话拆解 · 算清制度与人心底账", font_tag, gold_dim, tracking=3)

    font_author = load_font(44, "bold")
    draw_centered_text(draw, W, 2060, f"{BOOK_AUTHOR}  著", font_author, ivory, tracking=6)

    font_pub = load_font(28, "regular")
    draw_centered_text(draw, W, 2165, "全本考订版 · 六卷二十四章完结本", font_pub, gold_dim, tracking=5)

    img.save(out_path, format="JPEG", quality=92, optimize=True)


EPUB_CSS = """\
@charset "UTF-8";

html, body {
  margin: 0;
  padding: 0;
  line-height: 1.82;
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", "PingFang SC", serif;
  -webkit-hyphens: auto;
  hyphens: auto;
}

body {
  padding: 0 4%;
}

h1 {
  font-size: 1.55em;
  line-height: 1.35;
  margin: 1.4em 0 1.1em 0;
  padding-bottom: 0.45em;
  border-bottom: 2px solid #9e241d;
  font-weight: bold;
}

h2 {
  font-size: 1.28em;
  line-height: 1.4;
  margin: 1.5em 0 0.75em 0;
  font-weight: bold;
}

h3 {
  font-size: 1.14em;
  line-height: 1.45;
  margin: 1.4em 0 0.65em 0;
  color: #8c231c;
  font-weight: bold;
}

h4 {
  font-size: 1.04em;
  line-height: 1.45;
  margin: 1.2em 0 0.5em 0;
  font-weight: bold;
}

p {
  margin: 0 0 0.95em 0;
  text-align: justify;
}

hr {
  border: none;
  border-top: 1px solid #c9b99b;
  width: 42%;
  margin: 1.8em auto;
}

blockquote {
  margin: 1.1em 0;
  padding: 0.55em 0.95em;
  border-left: 3px solid #9e241d;
  background-color: rgba(158, 36, 29, 0.05);
}

blockquote p {
  margin: 0.35em 0;
}

ul, ol {
  margin: 0.6em 0 1.05em 1.4em;
  padding: 0;
}

li {
  margin-bottom: 0.35em;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
  font-size: 0.9em;
}

th, td {
  border: 1px solid #bfb39f;
  padding: 0.45em 0.6em;
  text-align: left;
  vertical-align: top;
}

th {
  background-color: rgba(198, 161, 91, 0.16);
  font-weight: bold;
}

a {
  color: #8c231c;
  text-decoration: none;
}

/* Cover Page */
body.cover-page {
  padding: 0;
  margin: 0;
  text-align: center;
}

.cover-wrap {
  width: 100%;
  height: 98vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-wrap img {
  max-width: 100%;
  max-height: 98vh;
  width: auto;
  height: auto;
}

/* Title & Volume Divider Pages */
.title-box, .volume-box {
  margin-top: 14%;
  text-align: center;
  padding: 2em 1em;
  border-top: 2px solid #9e241d;
  border-bottom: 2px solid #9e241d;
}

.book-kicker, .vol-num {
  font-size: 0.95em;
  letter-spacing: 0.18em;
  color: #8c231c;
  margin-bottom: 0.7em;
  text-align: center;
}

.book-main-title, .vol-title {
  font-size: 1.9em;
  font-weight: bold;
  line-height: 1.3;
  margin: 0.25em 0;
  border: none;
  padding: 0;
  text-align: center;
}

.book-subtitle {
  font-size: 1.18em;
  margin: 0.45em 0 1.3em 0;
  color: #6e5835;
  text-align: center;
}

.vol-era {
  font-size: 0.95em;
  color: #6e5835;
  margin: 0.6em 0;
  text-align: center;
}

.vol-desc {
  font-size: 0.98em;
  margin-top: 1.1em;
  text-align: center;
}

.copyright-note {
  margin-top: 3em;
  font-size: 0.85em;
  color: #666666;
  text-align: center;
}

nav#toc ol {
  list-style-type: none;
  margin-left: 0;
  padding-left: 0;
}

nav#toc > ol > li {
  margin: 0.85em 0;
  font-weight: bold;
}

nav#toc > ol > li > ol {
  margin: 0.35em 0 0.6em 1.2em;
  font-weight: normal;
}

nav#toc li {
  line-height: 1.65;
}
"""


def xhtml_doc(title: str, body_inner: str, body_class: str = "", epub_ns: bool = False) -> str:
    ns_extra = ' xmlns:epub="http://www.idpf.org/2007/ops"' if epub_ns else ""
    cls_attr = f' class="{body_class}"' if body_class else ""
    doc = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE html>\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{BOOK_LANG}" lang="{BOOK_LANG}"{ns_extra}>\n'
        "<head>\n"
        '  <meta charset="UTF-8" />\n'
        f"  <title>{html.escape(title)}</title>\n"
        '  <link rel="stylesheet" type="text/css" href="styles/epub.css" />\n'
        "</head>\n"
        f"<body{cls_attr}>\n"
        f"{body_inner}\n"
        "</body>\n"
        "</html>\n"
    )
    # Strict XML parse check on every generated XHTML page
    ET.fromstring(doc.encode("utf-8"))
    return doc


def md_to_xhtml_body(md_text: str) -> str:
    # Rewrite internal chapter links (e.g., 01-qin-shihuang.md -> ch01.xhtml)
    for md_file, xhtml_file in MD_TO_XHTML.items():
        md_text = md_text.replace(f"]({md_file})", f"]({xhtml_file})")

    rendered = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="xhtml",
    )
    # Replace named HTML entities not in core XML if any appear
    rendered = rendered.replace("&nbsp;", "&#160;").replace("&mdash;", "—").replace("&ldquo;", "“").replace("&rdquo;", "”")
    return rendered


def build_preface_md() -> str:
    raw = (DOCS_DIR / "index.md").read_text(encoding="utf-8")
    # Extract title + lead quote + "## 这本书怎么写历史" section cleanly (skipping web-only download block)
    lines = []
    skip_web_box = False
    for line in raw.splitlines():
        if line.startswith("## 全书六卷目录"):
            break
        if line.startswith("<!-- WEB_DOWNLOAD_START -->"):
            skip_web_box = True
            continue
        if line.startswith("<!-- WEB_DOWNLOAD_END -->"):
            skip_web_box = False
            continue
        if skip_web_box:
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def build_epub() -> None:
    print("1. Generating classical Qin-Han cover artwork...")
    generate_cover(COVER_PATH)

    EPUB_PATH.parent.mkdir(parents=True, exist_ok=True)
    modified_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pages = []  # (item_id, filename, title, xhtml_content, properties, linear)

    # 1. Cover page
    cover_xhtml = xhtml_doc(
        "封面",
        '<div class="cover-wrap"><img src="images/cover.jpg" alt="秦汉那些事儿：帝国初生的四百年 封面" /></div>',
        body_class="cover-page",
    )
    pages.append(("cover-page", "cover.xhtml", "封面", cover_xhtml, "", "yes"))

    # 2. Title & Copyright page
    title_xhtml = xhtml_doc(
        BOOK_TITLE,
        f"""<div class="title-box">
  <p class="book-kicker">公元前 259 — 公元 220 · 中华第一帝国兴衰录</p>
  <h1 class="book-main-title">{html.escape(BOOK_MAIN_TITLE)}</h1>
  <p class="book-subtitle">{html.escape(BOOK_SUBTITLE)}</p>
  <p style="text-align:center; margin-top:1.5em;"><strong>{html.escape(BOOK_AUTHOR)}</strong> 著</p>
</div>
<div class="copyright-note">
  <p>全书共六卷 · 二十四章（考订完结本）</p>
  <p>叙事跨度：前 259 年嬴政生于邯郸 — 公元 220 年曹丕代汉（自前 221 年秦一统计四百四十年）</p>
  <p>在线阅读：<a href="https://yingwang.github.io/qinhan-book/">yingwang.github.io/qinhan-book</a></p>
  <p>开源仓库：<a href="https://github.com/yingwang/qinhan-book">github.com/yingwang/qinhan-book</a></p>
  <p>版权许可：CC BY-NC-SA 4.0（署名 - 非商业性使用 - 相同方式共享）</p>
</div>""",
    )
    pages.append(("title-page", "titlepage.xhtml", "书名与版权页", title_xhtml, "", "yes"))

    # 3. Preface (导读与体例说明)
    preface_xhtml = xhtml_doc("导读与体例说明", md_to_xhtml_body(build_preface_md()))
    pages.append(("preface", "preface.xhtml", "导读与体例说明", preface_xhtml, "", "yes"))

    # 4. Outline (全书总纲与人物志)
    outline_md = (DOCS_DIR / "00-outline.md").read_text(encoding="utf-8")
    outline_xhtml = xhtml_doc("全书总纲与人物志", md_to_xhtml_body(outline_md))
    pages.append(("ch00", "ch00-outline.xhtml", "全书总纲与人物志", outline_xhtml, "", "yes"))

    # 5. Six Volumes & 24 Chapters
    for vol in VOLUMES:
        vol_full_title = f"{vol['num']}：{vol['title']}"
        vol_xhtml = xhtml_doc(
            vol_full_title,
            f"""<div class="volume-box">
  <p class="vol-num">{html.escape(vol['num'])}</p>
  <h1 class="vol-title">{html.escape(vol['title'])}</h1>
  <p class="vol-era">{html.escape(vol['era'])}</p>
  <p class="vol-desc">{html.escape(vol['desc'])}</p>
</div>""",
        )
        pages.append((vol["id"], f"{vol['id']}.xhtml", vol_full_title, vol_xhtml, "", "yes"))

        for cid, md_name, ch_title in vol["chapters"]:
            ch_md = (DOCS_DIR / md_name).read_text(encoding="utf-8")
            ch_xhtml = xhtml_doc(ch_title, md_to_xhtml_body(ch_md))
            pages.append((cid, f"{cid}.xhtml", ch_title, ch_xhtml, "", "yes"))

    # Build EPUB 3 Navigation Document (nav.xhtml) and insert right after titlepage
    toc_vol_items = []
    for vol in VOLUMES:
        vol_full_title = f"{vol['num']}：{vol['title']}"
        sub_items = "\n".join(
            f'          <li><a href="{cid}.xhtml">{html.escape(ch_title)}</a></li>'
            for cid, _, ch_title in vol["chapters"]
        )
        toc_vol_items.append(
            f'      <li>\n        <a href="{vol["id"]}.xhtml">{html.escape(vol_full_title)}</a>\n'
            f"        <ol>\n{sub_items}\n        </ol>\n      </li>"
        )

    nav_body = f"""<nav epub:type="toc" id="toc">
  <h1>全书目录</h1>
  <ol>
    <li><a href="cover.xhtml">封面</a></li>
    <li><a href="titlepage.xhtml">书名与版权页</a></li>
    <li><a href="preface.xhtml">导读与体例说明</a></li>
    <li><a href="ch00-outline.xhtml">全书总纲与人物志</a></li>
{chr(10).join(toc_vol_items)}
  </ol>
</nav>
<nav epub:type="landmarks" hidden="hidden">
  <h2>导览地标</h2>
  <ol>
    <li><a epub:type="cover" href="cover.xhtml">封面</a></li>
    <li><a epub:type="toc" href="nav.xhtml">目录</a></li>
    <li><a epub:type="bodymatter" href="vol01.xhtml">正文开始</a></li>
  </ol>
</nav>"""
    nav_xhtml = xhtml_doc("全书目录", nav_body, epub_ns=True)
    pages.insert(2, ("nav", "nav.xhtml", "全书目录", nav_xhtml, "nav", "yes"))

    # Build EPUB 2 NCX for legacy e-readers
    play_order = 1
    ncx_points = []
    for pid, fname, ptitle in [
        ("cover-page", "cover.xhtml", "封面"),
        ("title-page", "titlepage.xhtml", "书名与版权页"),
        ("nav", "nav.xhtml", "全书目录"),
        ("preface", "preface.xhtml", "导读与体例说明"),
        ("ch00", "ch00-outline.xhtml", "全书总纲与人物志"),
    ]:
        ncx_points.append(
            f'    <navPoint id="np-{pid}" playOrder="{play_order}">\n'
            f"      <navLabel><text>{html.escape(ptitle)}</text></navLabel>\n"
            f'      <content src="{fname}" />\n'
            f"    </navPoint>"
        )
        play_order += 1

    for vol in VOLUMES:
        vol_full_title = f"{vol['num']}：{vol['title']}"
        v_order = play_order
        play_order += 1
        ch_nps = []
        for cid, _, ch_title in vol["chapters"]:
            ch_nps.append(
                f'      <navPoint id="np-{cid}" playOrder="{play_order}">\n'
                f"        <navLabel><text>{html.escape(ch_title)}</text></navLabel>\n"
                f'        <content src="{cid}.xhtml" />\n'
                f"      </navPoint>"
            )
            play_order += 1
        ncx_points.append(
            f'    <navPoint id="np-{vol["id"]}" playOrder="{v_order}">\n'
            f"      <navLabel><text>{html.escape(vol_full_title)}</text></navLabel>\n"
            f'      <content src="{vol["id"]}.xhtml" />\n'
            f"{chr(10).join(ch_nps)}\n"
            f"    </navPoint>"
        )

    toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{BOOK_UUID}" />
    <meta name="dtb:depth" content="2" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle><text>{html.escape(BOOK_TITLE)}</text></docTitle>
  <docAuthor><text>{html.escape(BOOK_AUTHOR)}</text></docAuthor>
  <navMap>
{chr(10).join(ncx_points)}
  </navMap>
</ncx>
"""
    ET.fromstring(toc_ncx.encode("utf-8"))

    # Build content.opf (EPUB 3.0)
    manifest_items = [
        '    <item id="css" href="styles/epub.css" media-type="text/css" />',
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />',
        '    <item id="cover-img" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image" />',
    ]
    spine_items = []
    for pid, fname, _, _, props, linear in pages:
        prop_attr = f' properties="{props}"' if props else ""
        manifest_items.append(
            f'    <item id="{pid}" href="{fname}" media-type="application/xhtml+xml"{prop_attr} />'
        )
        spine_items.append(f'    <itemref idref="{pid}" linear="{linear}" />')

    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{BOOK_LANG}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_UUID}</dc:identifier>
    <dc:title>{html.escape(BOOK_TITLE)}</dc:title>
    <dc:creator>{html.escape(BOOK_AUTHOR)}</dc:creator>
    <dc:language>{BOOK_LANG}</dc:language>
    <dc:description>{html.escape(BOOK_DESC)}</dc:description>
    <dc:subject>中国历史</dc:subject>
    <dc:subject>秦汉史</dc:subject>
    <dc:rights>CC BY-NC-SA 4.0</dc:rights>
    <meta property="dcterms:modified">{modified_utc}</meta>
    <meta name="cover" content="cover-img" />
  </metadata>
  <manifest>
{chr(10).join(manifest_items)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine_items)}
  </spine>
</package>
"""
    ET.fromstring(content_opf.encode("utf-8"))

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/epub+xml" />
  </rootfiles>
</container>
"""
    ET.fromstring(container_xml.encode("utf-8"))

    print("2. Packaging EPUB 3.0 archive...")
    with zipfile.ZipFile(EPUB_PATH, "w") as zf:
        # Spec requirement: mimetype MUST be first entry, uncompressed, no extra field
        mime_info = zipfile.ZipInfo("mimetype")
        mime_info.compress_type = zipfile.ZIP_STORED
        mime_info.extra = b""
        zf.writestr(mime_info, b"application/epub+zip")

        zf.writestr("META-INF/container.xml", container_xml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/content.opf", content_opf.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/toc.ncx", toc_ncx.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/styles/epub.css", EPUB_CSS.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.write(COVER_PATH, "OEBPS/images/cover.jpg", compress_type=zipfile.ZIP_DEFLATED)

        for _, fname, _, xhtml_str, _, _ in pages:
            zf.writestr(f"OEBPS/{fname}", xhtml_str.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)

    size_kb = EPUB_PATH.stat().st_size / 1024
    print(f"3. Done! Generated {EPUB_PATH} ({size_kb:.1f} KB) with {len(pages)} XHTML documents.")


if __name__ == "__main__":
    build_epub()
