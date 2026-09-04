<name>
BiliContent AI
</name>
<description>
B站内容智能提取与AI知识精炼流水线。从B站视频/合集/UP主空间批量提取AI字幕，输出SRT/TXT/VTT/ASS/JSON五种格式，并通过LLM进一步精炼为排版字幕和结构化文章。专为B站120秒授权窗口设计的分批抗过期策略，内置质量检测与修复机制，实现视频内容到知识资产的高效转化。
</description>

# BiliContent AI — B站内容智能提取与知识精炼

从B站视频中提取AI字幕，通过AI加工为结构化知识，实现视频内容到文本知识的高效转化。支持单视频、合集、UP主空间三种来源，内置质量检测与修复，输出5种字幕格式，并可通过LLM精炼为排版字幕和结构化文章。

## 能力全景

| 能力 | 说明 |
|------|------|
| **多源内容接入** | 支持单视频 / 合集 / UP主空间三种来源，自动解析视频列表，统一输出 |
| **智能字幕引擎** | 分批获取B站AI字幕，内置质量检测（重叠修复、空白移除、重复合并），输出5种格式 |
| **AI知识精炼** | 将字幕加工为排版字幕（保留时间轴+修正格式）和精炼文章（去口水词+层级化） |
| **可视化报告** | 自动生成HTML统计报告，包含成功率、字幕条数、总时长等维度 |
| **增量无损** | 已下载视频自动跳过，支持断点续提，不重复劳动 |
| **配置化输出** | 输出格式、质量检测、AI处理均可配置，适应不同场景 |

## 适用场景

| 场景 | 说明 |
|------|------|
| **内容创作者** | 分析竞品UP主的视频内容结构，生成文字稿 |
| **产品经理** | 集中收集某款产品的B站评测视频，快速提取核心观点 |
| **学习者** | 将教学视频的字幕导出为文章，便于复习和检索 |
| **研究员** | 批量抓取特定主题的B站内容，建立知识库 |

## 工作流程

```
用户需求 → 确定内容来源 → 提取视频列表 → 分批获取字幕URL → 下载转换 → AI精炼 → 报告
```

---

## 步骤1：确定内容来源

根据用户需求判断来源类型：

| 用户说 | 来源类型 | 操作 |
|--------|----------|------|
| "这个视频的字幕下载一下" | `single` | 打开视频页 |
| "这个合集帮我提取全部字幕" | `collection` | 打开合集页 |
| "搜索XXUP主关于XX的视频" | `space` | 打开UP主空间页 |

---

## 步骤2：提取视频列表

### 方式A：通过浏览器（推荐）

导航到目标页面后执行：

```javascript
// 提取 __INITIAL_STATE__ 并保存到 eps.json
// 单视频/合集/空间三种页面都支持
JSON.stringify(JSON.parse(document.body.innerText.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});/s)[1]))
```

### 方式B：通过HTML文件

保存页面HTML后运行：

```bash
# 单个视频
python extract_videos.py --source single --html page.html -o eps.json

# 合集
python extract_videos.py --source collection --html page.html -o eps.json

# UP主空间
python extract_videos.py --source space --html page.html -o eps.json
```

### 搜索与筛选（UP主空间场景）

提取视频列表后，根据用户需求进行筛选：

- **精确搜索**：直接判断标题是否包含关键词
- **模糊搜索**：判断标题是否与关键词相关（AI擅长的语义匹配）
- **分Part识别**：识别"Part 1/2/3"、"上/中/下"等模式，自动归组

筛选结果仍保存为 `eps.json`。

---

## 步骤3：分批获取字幕URL

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

---

## 步骤4：下载并转换字幕

提取完一批后立即执行：

```bash
python download_subtitles.py eps.json sub_urls.txt -o ./字幕 --config bili_config.json
```

输出文件：
- `字幕/SRT/*.srt` — 标准字幕
- `字幕/TXT/*.txt` — 纯文本
- `字幕/VTT/*.vtt` — Web字幕
- `字幕/ASS/*.ass` — 高级字幕
- `字幕/JSON/*.json` — 结构化数据

---

## 步骤5：AI内容精炼（由你直接执行，无需调用外部LLM API）

> 此步骤由执行本 Skill 的 AI Agent（即你）直接读取文件并加工内容，不需要安装任何 AI 依赖，也不需要调用 OpenAI 等外部接口。

字幕下载完成后，对每个视频的TXT文件进行AI处理：

### 5.1 生成排版字幕

读取 `字幕/XXX.txt` → 调用AI处理 → 保存到 `AI排版字幕/XXX.txt`

处理要求：
- 保留全部时间戳，不丢失任何内容
- 修正标点符号（中文用全角标点）
- 按语义进行段落分段（不是每句一行）
- 同一说话人的连续内容合并为段落
- 统一格式：`[HH:MM:SS] 段落内容`

### 5.2 生成精炼文章

读取 `字幕/XXX.txt` → 调用AI处理 → 保存到 `AI精炼文章/XXX.md`

处理要求：
- **保留全部信息点**，不能丢失任何内容
- 去除口语词：嗯、啊、这个、那个、就是、然后（重复的口头禅）
- 按主题层级化组织，使用 Markdown 标题
- 长段落按逻辑拆分为子段落
- 技术术语保持原样，不需要解释
- 格式：`# 标题\n\n## 主题1\n\n内容...`

---

## 步骤6：生成报告

```bash
python generate_report.py eps.json ./字幕 -o 提取报告.html
```

---

## 重复步骤3-6

处理完一批后继续下一批，直到全部完成。

---

## 配置说明

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

## 常见问题

| 问题 | 原因 | 处理 |
|------|------|------|
| 403 Forbidden | auth_key过期 | 重新提取该批URL |
| 返回空字幕 | 该视频没有AI字幕 | 标记 NOSUBS 跳过 |
| 搜索无结果 | 关键词不匹配 | 尝试模糊搜索或换关键词 |

## 依赖

```bash
pip install requests
```