# 秦汉那些事儿：帝国初生的四百年

> 一部用现代白话拆解中华第一帝国兴衰的长篇历史书（全书六卷 · 二十四章完结）。从公元前 259 年赵国邯郸小巷里的秦国质子，讲到公元 220 年繁阳受禅台上的末代汉帝——叙事横跨近四百八十年（自前 221 年大秦一统算起，恰为四百四十年帝国周期），还原硬核史料背后的人性博弈、制度逻辑与家国悲欢。

**在线阅读（GitHub Pages）**：[yingwang.github.io/qinhan-book](https://yingwang.github.io/qinhan-book/)

**EPUB 全本电子书下载**：[点击下载 qinhan-book.epub](https://yingwang.github.io/qinhan-book/downloads/qinhan-book.epub) ｜ [GitHub Raw 备用直链](https://github.com/yingwang/qinhan-book/raw/main/docs/downloads/qinhan-book.epub)（支持 Apple 图书、微信读书、Kobo、Calibre 阅读，并可通过 Send to Kindle 发送至 Kindle）

---

## 全书目录（六卷 · 二十四章 · 全本完结）

- [x] [全书总纲与人物志](docs/00-outline.md)
- [x] **第一卷：铁血大秦（前 259 — 前 207）**
  - [x] [第 1 章 从邯郸肉票到千古一帝](docs/01-qin-shihuang.md)
  - [x] [第 2 章 失控的战车与沙丘鲍鱼](docs/02-shaqiu-collapse.md)
  - [x] [第 3 章 大泽乡的泥水与乱世合伙人](docs/03-dazexiang-uprising.md)
- [x] **第二卷：楚汉惊雷（前 207 — 前 195）**
  - [x] [第 4 章 鸿门宴上的微表情与暗度陈仓](docs/04-hongmen-chencang.md)
  - [x] [第 5 章 打不死的刘邦与韩信封神](docs/05-pengcheng-hanxin.md)
  - [x] [第 6 章 霸王别姬与未央宫的杀机](docs/06-gaixia-weiyang.md)
- [x] **第三卷：文景韬晦（前 195 — 前 141）**
  - [x] [第 7 章 吕后铁腕与代王进京](docs/07-lvhou-daiwang.md)
  - [x] [第 8 章 抠门天子与七国烽烟](docs/08-wenjing-qiguo.md)
- [x] **第四卷：汉武铁骑（前 141 — 前 48）**
  - [x] [第 9 章 少年刘彻的野心与独尊儒术](docs/09-liuche-weixing.md)
  - [x] [第 10 章 双星闪耀与封狼居胥](docs/10-weihuo-mobei.md)
  - [x] [第 11 章 凿空西域与算盘上的帝国](docs/11-zhangqian-shiji.md)
  - [x] [第 12 章 巫蛊血案与轮台罪己](docs/12-wugu-luntai.md)
  - [x] [第 13 章 权臣霍光与病已逆袭](docs/13-huoguang-xuandi.md)
- [x] **第五卷：日落西京与光武重光（前 48 — 公元 88）**
  - [x] [第 14 章 柔弱天子与王氏坐大](docs/14-yuandi-wangshi.md)
  - [x] [第 15 章 穿越者王莽的魔幻乌托邦](docs/15-wangmang-utopia.md)
  - [x] [第 16 章 庄稼汉刘秀与昆阳神迹](docs/16-liuxiu-kunyang.md)
  - [x] [第 17 章 云台将星与柔道治国](docs/17-yuntai-roudao.md)
  - [x] [第 18 章 明章之治与班超孤悬绝域](docs/18-mingzhang-banchao.md)
- [x] **第六卷：东京残照（公元 88 — 公元 220）**
  - [x] [第 19 章 短命皇帝与外戚宦官轮盘赌](docs/19-waiqi-huanguan.md)
  - [x] [第 20 章 清流热血与党锢绝响](docs/20-qingliu-danggu.md)
  - [x] [第 21 章 黄巾惊雷与董卓焚洛](docs/21-huangjin-dongzhuo.md)
  - [x] [第 22 章 长安废墟与许昌棋局](docs/22-changan-xuchang.md)
  - [x] [第 23 章 衣带诏之血与荀彧之死](docs/23-yidai-xunyu.md)
  - [x] [第 24 章 受禅台上的背影与四百年回响](docs/24-shouchantai-finale.md)

---

## 本地预览与构建 EPUB

```bash
pip install -r requirements.txt
mkdocs serve

# 重新生成封面与 EPUB 3.0 电子书（需安装 Pillow 与 Markdown）
python3 scripts/build_epub.py
```

---

## 仓库结构

```
qinhan-book/
├── docs/
│   ├── index.md                        首页导读与全书总目录
│   ├── 00-outline.md                   全书总纲与人物志
│   ├── 01-qin-shihuang.md              第一卷：第 1–3 章（铁血大秦）
│   ├── ...
│   ├── 24-shouchantai-finale.md        第六卷：第 19–24 章（东京残照）
│   ├── assets/cover.jpg                电子书封面
│   ├── downloads/qinhan-book.epub      全本 EPUB 3.0 电子书
│   └── stylesheets/                    排版与打印样式
├── scripts/
│   └── build_epub.py                   EPUB 3.0 与封面自动构建脚本
├── .github/
│   └── workflows/deploy.yml            GitHub Pages 自动部署工作流
├── mkdocs.yml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 版权声明

CC BY-NC-SA 4.0，非商业性使用、署名、以相同方式共享。
