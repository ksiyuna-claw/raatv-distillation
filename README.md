# RAATV 5-Step Distillation Framework / RAATV 五步蒸馏框架

**A structured methodology for distilling any content creator's style from raw video data into reusable writing templates.**

**一套结构化方法论：从创作者的原始视频数据中，蒸馏出可复用的写作模板。**

> **R**ead → **A**nalyze (Beliefs) → **A**nalyze (Strategies) → **T**emplate → **V**erify

---

## What is RAATV? / 什么是 RAATV？

RAATV is a structured distillation framework that takes a content creator's video corpus (e.g., from Douyin/TikTok) and extracts their **belief system**, **content strategies**, **writing formulas**, and **oral style DNA** — then converts them into reusable templates you can apply to your own content.

RAATV 是一套蒸馏框架，核心做的事很简单：拿一个创作者的全部视频（比如抖音/TikTok），把他的**信念体系**、**内容策略**、**写作公式**和**口语风格基因**全部提取出来，再转化成你自己能直接套用的模板。

### The 5 Steps / 五个步骤

| Step | Name | What It Does / 干什么 |
|------|------|----------------------|
| **R** | Read / 通读 | Ingest all transcripts, map topic & duration distributions / 读完全部逐字稿，画出选题分布和时长分布 |
| **A1** | Analyze — Beliefs / 信念分析 | Extract 12-15 core beliefs (recurring assertions across topics) / 提取 12-15 条核心价值观（跨选题反复出现的断言） |
| **A2** | Analyze — Strategies / 策略分析 | Extract 10 operational strategies (opening hooks, structures, taboos) / 提取 10 条操作策略（开头钩子、结构手法、禁忌） |
| **A3** | Analyze — Formulas / 公式分析 | Extract 12 content formulas (repeatable title/content structures) / 提取 12 条内容公式（可复用的标题和正文结构） |
| **A4** | Analyze — Oral DNA / 风格分析 | Extract 12-15 stylistic signatures (catchphrases, tone, emotional markers) / 提取 12-15 条口语风格特征（口头禅、语气、情绪标记） |
| **T** | Template / 模板化 | Translate formulas into cross-niche reusable principles / 把公式翻译成跨领域可复用的通用原则 |
| **V** | Verify / 验证 | Trial-write on new topics, compare, and refine / 用新选题试写、对比、迭代优化 |

### Pipeline Overview / 流程总览

```
Phase 0: Fetch Metadata  → Pull all video metadata (likes, comments, timestamps)
Phase 1: Select & ASR    → Rank by likes, select top 50, download audio, transcribe
Phase 2: Verify          → Ensure all transcripts are complete
Phase 3: RAATV Distill   → Run the 5-step state machine
Phase 4: Audit           → Validate frequency claims, coverage checks
Phase 5: Deliver         → Generate final distillation report
Phase 6: Cleanup         → Remove intermediate files
```

```
阶段 0: 拉取元数据   → 获取全部视频的点赞、评论、时间戳等元信息
阶段 1: 筛选 & 转写  → 按点赞排序，选 Top 50，下载音频，语音转文字
阶段 2: 校验         → 确认所有逐字稿完整可用
阶段 3: RAATV 蒸馏   → 跑五步状态机
阶段 4: 审核         → 验证频率声称、覆盖率检查
阶段 5: 交付         → 生成最终蒸馏报告
阶段 6: 清理         → 删除中间文件
```

---

## Requirements / 环境要求

- **Python 3.8+** (standard library only, no pip packages needed) / 只需 Python 标准库，无需 pip 安装
- **ffmpeg** (optional, for compressing long audio before ASR) / 可选，用于压缩长音频
- **[TikHub API Key](https://tikhub.io/)** — for Douyin/TikTok data access / 用于抖音/TikTok 数据抓取
- **[SiliconFlow API Key](https://siliconflow.cn/)** — for ASR (speech-to-text) / 用于语音转文字

## Setup / 安装

```bash
git clone https://github.com/ksiyuna-claw/raatv-distillation.git
cd raatv-distillation

# Set your API keys / 设置 API Key
export TIKHUB_API_KEY="your_tikhub_key_here"
export SILICONFLOW_KEY="your_siliconflow_key_here"
```

## Usage / 使用方法

### Step 1: Fetch All Video Metadata / 第一步：拉取全部视频元数据

```bash
python3 scripts/fetch_all_metadata.py \
  --sec_user_id "MS4wLjAB..." \
  --output "metadata/all_videos.json" \
  --tikhub_key "YOUR_TIKHUB_API_KEY"
```

Pulls all video metadata (independent posts + collection/series) from the target account.

拉取目标账号的全部视频元信息（含独立发布 + 合集/系列）。

### Step 2: Select Top 50 & Transcribe / 第二步：筛选 Top 50 并转写

```bash
python3 scripts/download_asr_concurrent.py \
  --selected metadata/selected_50.json \
  --audio-dir audio/ \
  --status status/status.json \
  --transcripts transcripts.json \
  --tikhub-key "YOUR_TIKHUB_API_KEY" \
  --sf-key "YOUR_SILICONFLOW_KEY"
```

Features / 特性：
- **10x parallel** download + ASR (ThreadPoolExecutor) / 10 路并发下载 + 转写
- **Checkpoint resume** — writes status after each video, re-run skips completed ones / 断点续传，每条视频完成后立即写入状态，重跑自动跳过已完成的
- **Smart audio priority** — prefers pure audio URLs over full video / 智能优先纯音频 URL
- **Auto-compress** long audio (>25MB) with ffmpeg before ASR / 超过 25MB 的长音频自动用 ffmpeg 压缩后再转写

### Step 3: Run RAATV Distillation / 第三步：执行 RAATV 蒸馏

Follow the [Distillation Guide](DISTILLATION_GUIDE.md) to execute the 5-step process using the JSON state machine. Each step writes to `distill_state.json` to track progress.

按照[蒸馏指南](DISTILLATION_GUIDE.md)执行五步流程，使用 JSON 状态机管理进度。每一步的中间结果写入 `distill_state.json`。

### Step 4: Cleanup / 第四步：清理

```bash
python3 scripts/cleanup.py --project-dir "/path/to/your/project"
# Use --dry-run to preview without deleting / 加 --dry-run 预览不实际删除
```

---

## Project Structure / 项目结构

Each distillation task should have its own folder:

每个蒸馏任务用独立文件夹管理：

```
your-project/
├── distill-analysis-{creator-name}.md   # Final analysis report / 最终分析报告
├── transcripts-{creator-name}.json      # All transcripts / 全部逐字稿
├── metadata/
│   ├── all_videos.json                  # Full metadata / 完整元数据
│   ├── selected_50.json                 # Curated top 50 / 精选 Top 50
│   └── raw.json                         # Raw API data / 原始 API 数据
├── audio/                               # Temporary (auto-cleaned) / 临时文件（自动清理）
├── status/                              # Checkpoint (auto-cleaned) / 断点状态（自动清理）
├── distill_state.json                   # RAATV state machine / RAATV 状态机
└── logs/
```

---

## Key Design Decisions / 关键设计决策

1. **Metadata-first / 元数据先行** — Fetch all metadata (~$0.001/item) before downloading any audio. This lets you see the full landscape before committing resources. / 先花极低成本拉完元数据（约 ¥0.007/条），看清全貌再决定下载哪些。

2. **Checkpoint resume / 断点续传** — Every completed item is saved immediately. Network failures won't lose progress. / 每条完成即落盘，网络故障不会丢进度。

3. **Batch reading for LLM / LLM 分批读取** — 50 transcripts (~76K chars ~190K tokens) can overflow LLM context windows. The RAATV state machine processes transcripts in 5 batches of 10, analyzing and persisting results between batches. / 50 条逐字稿约 76000 字（~190K tokens），可能撑爆 LLM 上下文窗口。状态机分 5 批（每批 10 条）处理，批次间持久化结果。

4. **Music URLs are never used / 不用音乐 URL** — Background music tracks don't contain speech. Only `audio_fallback_url` or `video_url` are used for ASR. / 背景音乐音轨没有语音内容，只用 `audio_fallback_url` 或 `video_url` 做转写。

---

## Example Output / 示例输出

See [`examples/example-output-structure.md`](examples/example-output-structure.md) for a sample distillation report structure.

示例报告结构见 [`examples/example-output-structure.md`](examples/example-output-structure.md)。

---

## License / 许可证

[MIT](LICENSE)

---

## ⭐ Star This Repo / 点个 Star

If this framework helped you understand and replicate creator styles, give it a star! It helps others discover the methodology.

如果这个框架帮到了你，点个 Star 让更多人看到。

---

<p align="center">
  <b>👨‍🍳 匡书记的家常出品</b><br>
  <i>Crafted by Kuang Shuji's Kitchen</i>
</p>
