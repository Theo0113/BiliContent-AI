# BiliContent AI 🎬

<div align="center">

**B站内容智能提取与AI知识精炼流水线**

从B站视频/合集/UP主空间批量提取AI字幕，输出SRT/TXT/VTT/ASS/JSON五种格式，并通过LLM进一步精炼为排版字幕和结构化文章。


---

## 📖 项目介绍

B站上有大量优质的教学、评测、分享类视频内容，但这些内容存在一个核心问题：**视频是线性的，知识是结构化的**。

- 🙅‍♂️ 想看某个UP主的全部视频，需要一个一个点开
- 🙅‍♂️ 想找某款产品的所有评测视频，需要手动搜索和筛选
- 🙅‍♂️ 视频里的字幕只能看，不能导出、搜索、复用
- 🙅‍♂️ 一小时的视频，想要提取核心信息，必须从头看到尾

**BiliContent AI 解决的正是这个"视频内容到知识资产"的转化问题。**

---

## ✨ 功能特性

| 特性  | 说明  |
| --- | --- |
| **多源内容接入** | 支持单视频 / 合集 / UP主主页三种来源，自动解析视频列表 |
| **智能分批策略** | 专为B站120秒授权窗口设计，分批提取+即时下载，高成功率 |
| **质量检测修复** | 自动修复重叠时间轴、移除空白行、合并重复字幕 |
| **多格式输出** | SRT / TXT / VTT / ASS / JSON五种格式，满足不同需求 |
| **AI知识精炼** | 生成排版字幕（保留时间轴+修正格式）和精炼文章（去口水词+层级化） |
| **增量提取** | 已下载视频自动跳过，支持断点续提，不重复劳动 |
| **可视化报告** | 自动生成HTML统计报告，包含成功率、字幕条数、总时长 |
| **配置化输出** | 输出格式、质量检测、AI处理均可配置，适应不同场景 |

---

## 🎯 适用场景

| 场景  | 说明  |
| --- | --- |
| **内容创作者** | 分析竞品UP主的视频内容结构，生成文字稿 |
| **产品经理** | 集中收集某款产品的B站评测视频，快速提取核心观点 |
| **学习者** | 将教学视频的字幕导出为文章，便于复习和检索 |
| **研究员** | 批量抓取特定主题的B站内容，建立知识库 |

---

## 🔧 架构流程

```
用户输入（URL/UP主/关键词）
        │
        ▼
┌─────────────────┐
│  内容源识别器     │  单视频 / 合集 / UP主主页
│  extract_videos   │
└────────┬────────┘
         │ eps.json（统一格式的视频列表）
         ▼
┌─────────────────┐
│  字幕提取引擎     │  分批获取字幕URL → 即时下载
│  download_subs    │  质量检测 → 5格式输出
└────────┬────────┘
         │ SRT / TXT / VTT / ASS / JSON
         ▼
┌─────────────────┐
│  AI内容精炼器     │  排版字幕 → 结构化文章
│  (LLM驱动)        │
└────────┬────────┘
         │ AI排版字幕 / AI精炼文章
         ▼
┌─────────────────┐
│  HTML报告生成器   │  统计看板 + 详情列表
│  generate_report  │
└─────────────────┘
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install requests
```

### 使用流程

#### 1. 提取视频列表

根据内容来源类型，运行对应命令：

```bash
# 单个视频
python extract_videos.py --source single --html page.html -o eps.json

# 合集
python extract_videos.py --source collection --html page.html -o eps.json

# UP主空间
python extract_videos.py --source space --html page.html -o eps.json
```

**通过浏览器提取（推荐）**：导航到目标页面后执行以下JavaScript代码，复制结果保存为 `eps.json`：

```javascript
// 单视频/合集/空间三种页面都支持
JSON.stringify(JSON.parse(document.body.innerText.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});/s)[1]))
```

#### 2. 分批获取字幕URL

B站字幕URL的 `auth_key` 有效期约2分钟，必须**提取一批 → 立即下载一批**。

每次在浏览器中执行：

```javascript
// 每次处理不超过10个
const pairs = [[aid1, cid1], [aid2, cid2], ...];
const out = [];
for (const [aid, cid] of pairs) {
    const r = await fetch(`https://api.bilibili.com/x/player/wbi/v2?aid=${aid}&cid=${cid}`, {credentials: 'include'});
    const j = await r.json();
    const subs = (j.data?.subtitle?.subtitles) || [];
    out.push(subs.length ? aid + ' ' + subs[0].subtitle_url : aid + ' NOSUBS');
}
JSON.stringify(out)
```

将结果写入 `sub_urls.txt`，格式：每行 `aid //aisubtitle.hdslb.com/...` 或 `aid NOSUBS`。

#### 3. 下载并转换字幕

```bash
python download_subtitles.py eps.json sub_urls.txt -o ./字幕 --config bili_config.json
```

#### 4. AI内容精炼

字幕下载完成后，对每个视频的TXT文件进行AI处理：

- **排版字幕**：保留时间轴，修正标点，统一格式，分段清晰 → 输出到 `AI排版字幕/`
- **精炼文章**：保留全部信息，去除口水词，按主题层级化组织 → 输出到 `AI精炼文章/`

#### 5. 生成报告

```bash
python generate_report.py eps.json ./字幕 -o 提取报告.html
```

#### 6. 重复步骤2-5

处理完一批后继续下一批，直到全部完成。

---

## ⚙️ 配置说明

编辑 `bili_config.json`：

```json
{
  "output_dir": "./字幕",
  "formats": ["srt", "txt", "vtt", "ass", "json"],
  "quality_check": true,
  "separate_folders": true,
  "ai_format": true,
  "ai_article": true
}
```

| 配置项 | 说明  |
| --- | --- |
| `output_dir` | 输出目录 |
| `formats` | 需要输出的字幕格式 |
| `quality_check` | 是否启用质量检测（修复重叠、合并重复、移除空白） |
| `separate_folders` | 是否按格式分文件夹存放 |
| `ai_format` | 是否生成AI排版字幕 |
| `ai_article` | 是否生成AI精炼文章 |

---

## 📦 输出目录结构

```
./
├── eps.json                 # 视频列表
├── sub_urls.txt             # 字幕URL
├── 字幕/                    # 原始字幕
│   ├── SRT/
│   ├── TXT/
│   ├── VTT/
│   ├── ASS/
│   └── JSON/
├── AI排版字幕/              # AI格式化后的字幕
├── AI精炼文章/              # AI去口语化整理的文章
└── 提取报告.html            # 可视化统计报告
```

---

## ❓ 常见问题

| 问题  | 原因  | 处理  |
| --- | --- | --- |
| 403 Forbidden | auth_key过期 | 重新提取该批URL |
| 返回空字幕 | 该视频没有AI字幕 | 标记 NOSUBS 跳过 |
| 搜索无结果 | 关键词不匹配 | 尝试模糊搜索或换关键词 |

---

## 💡 技术亮点

| 亮点  | 说明  |
| --- | --- |
| **分批抗过期策略** | B站字幕URL的auth_key有效期仅2分钟，设计分批提取+即时下载机制，保证高成功率 |
| **AI语义处理** | 利用AI的自然语言理解能力处理字幕内容，而非规则匹配，适应各种语言风格 |
| **增量无损** | 已下载视频自动跳过，支持断点续提，不重复劳动 |
| **配置化输出** | 输出格式、质量检测、AI处理均可配置，适应不同场景 |

---

## 📝 免责声明

- 本项目仅供**个人学习研究**使用，禁止用于商业用途
- 本项目与 Bilibili 无任何关联
- 使用本项目所产生的任何法律纠纷由使用者自行承担
- 请勿用于非法下载、侵犯版权等违法行为

---

## 📄 许可证

[MIT License](LICENSE) © BiliContent AI Contributors

---

