# RAATV Distillation Framework

**A 5-step methodology for distilling any content creator's style from raw video data into reusable writing templates.**

> **R**ead → **A**nalyze (Beliefs) → **A**nalyze (Strategies) → **T**emplate → **V**erify

---

## What is RAATV?

RAATV is a structured distillation framework that takes a content creator's video corpus (e.g., from Douyin/TikTok) and extracts their **belief system**, **content strategies**, **writing formulas**, and **oral style DNA** — then converts them into reusable templates you can apply to your own content.

### The 5 Steps

| Step | Name | What It Does |
|------|------|-------------|
| **R** | Read | Ingest all transcripts, map topic & duration distributions |
| **A1** | Analyze — Beliefs | Extract 12-15 core beliefs (recurring assertions across topics) |
| **A2** | Analyze — Strategies | Extract 10 operational strategies (opening hooks, structures, taboos) |
| **A3** | Analyze — Formulas | Extract 12 content formulas (repeatable title/content structures) |
| **A4** | Analyze — Oral DNA | Extract 12-15 stylistic signatures (catchphrases, tone, emotional markers) |
| **T** | Template | Translate formulas into cross-niche reusable principles |
| **V** | Verify | Trial-write on new topics, compare, and refine |

### Pipeline Overview

```
Phase 0: Fetch Metadata  → Pull all video metadata (likes, comments, timestamps)
Phase 1: Select & ASR    → Rank by likes, select top 50, download audio, transcribe
Phase 2: Verify          → Ensure all transcripts are complete
Phase 3: RAATV Distill   → Run the 5-step state machine
Phase 4: Audit           → Validate frequency claims, coverage checks
Phase 5: Deliver         → Generate final distillation report
Phase 6: Cleanup         → Remove intermediate files
```

---

## Requirements

- **Python 3.8+** (standard library only, no pip packages needed)
- **ffmpeg** (optional, for compressing long audio before ASR)
- **[TikHub API Key](https://tikhub.io/)** — for Douyin/TikTok data access
- **[SiliconFlow API Key](https://siliconflow.cn/)** — for ASR (speech-to-text)

## Setup

```bash
git clone https://github.com/ksiyuna-claw/raatv-distillation.git
cd raatv-distillation

# Set your API keys as environment variables
export TIKHUB_API_KEY="your_tikhub_key_here"
export SILICONFLOW_KEY="your_siliconflow_key_here"
```

## Usage

### Step 1: Fetch All Video Metadata

```bash
python3 scripts/fetch_all_metadata.py \
  --sec_user_id "MS4wLjAB..." \
  --output "metadata/all_videos.json" \
  --tikhub_key "YOUR_TIKHUB_API_KEY"
```

This pulls all video metadata (independent posts + collection/series) from the target account.

### Step 2: Select Top 50 & Transcribe

```bash
python3 scripts/download_asr_concurrent.py \
  --selected metadata/selected_50.json \
  --audio-dir audio/ \
  --status status/status.json \
  --transcripts transcripts.json \
  --tikhub-key "YOUR_TIKHUB_API_KEY" \
  --sf-key "YOUR_SILICONFLOW_KEY"
```

Features:
- **10x parallel** download + ASR (ThreadPoolExecutor)
- **Checkpoint resume** — writes status after each video, re-run skips completed ones
- **Smart audio priority** — prefers pure audio URLs over full video
- **Auto-compress** long audio (>25MB) with ffmpeg before ASR

### Step 3: Run RAATV Distillation

Follow the [Distillation Guide](DISTILLATION_GUIDE.md) to execute the 5-step process using the JSON state machine. Each step writes to `distill_state.json` to track progress.

### Step 4: Cleanup

```bash
python3 scripts/cleanup.py --project-dir "/path/to/your/project"
# Use --dry-run to preview without deleting
```

---

## Project Structure

Each distillation task should have its own folder:

```
your-project/
├── distill-analysis-{creator-name}.md   # Final analysis report
├── transcripts-{creator-name}.json      # All transcripts
├── metadata/
│   ├── all_videos.json                  # Full metadata
│   ├── selected_50.json                 # Curated top 50
│   └── raw.json                         # Raw API data
├── audio/                               # Temporary (auto-cleaned)
├── status/                              # Checkpoint (auto-cleaned)
├── distill_state.json                   # RAATV state machine
└── logs/
```

---

## Key Design Decisions

1. **Metadata-first** — Fetch all metadata (~$0.001/item) before downloading any audio. This lets you see the full landscape before committing resources.
2. **Checkpoint resume** — Every completed item is saved immediately. Network failures won't lose progress.
3. **Batch reading for LLM** — 50 transcripts (~76K chars ~190K tokens) can overflow LLM context windows. The RAATV state machine processes transcripts in 5 batches of 10, analyzing and persisting results between batches.
4. **Music URLs are never used** — Background music tracks don't contain speech. Only `audio_fallback_url` or `video_url` are used for ASR.

---

## Example Output

See [`examples/example-output-structure.md`](examples/example-output-structure.md) for a sample distillation report structure.

---

## License

[MIT](LICENSE)

---

## ⭐ Star This Repo

If this framework helped you understand and replicate creator styles, give it a star! It helps others discover the methodology.
