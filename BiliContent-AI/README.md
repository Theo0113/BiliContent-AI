# BiliContent AI — B站内容智能提取与知识精炼平台

从B站视频/合集/UP主空间提取AI字幕，通过AI加工为排版字幕和结构化文章。

## 文件说明

| 文件 | 作用 |
|------|------|
| `SKILL.md` | 核心指令，AI按此流程执行 |
| `extract_videos.py` | 统一入口：单视频/合集/UP主空间 → eps.json |
| `download_subtitles.py` | 下载字幕 → SRT/TXT/VTT/ASS/JSON |
| `generate_report.py` | 生成HTML报告 |
| `bili_config.json` | 配置文件 |

## 快速开始

```bash
pip install requests

# 1. 提取视频列表
python extract_videos.py --source collection --html page.html -o eps.json

# 2. 下载字幕
python download_subtitles.py eps.json sub_urls.txt -o ./字幕

# 3. AI精炼（AI自行处理字幕内容）

# 4. 生成报告
python generate_report.py eps.json ./字幕 -o 提取报告.html
```

## 三种来源

```bash
# 单个视频
python extract_videos.py --source single --html page.html -o eps.json

# 合集
python extract_videos.py --source collection --html page.html -o eps.json

# UP主空间
python extract_videos.py --source space --html page.html -o eps.json
```

## 输出

- `字幕/` — 原始字幕（SRT/TXT/VTT/ASS/JSON）
- `AI排版字幕/` — AI格式化后的字幕
- `AI精炼文章/` — AI去口语化、层级化整理的文章
- `提取报告.html` — 可视化统计报告