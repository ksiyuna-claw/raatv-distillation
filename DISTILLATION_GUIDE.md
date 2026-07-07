# RAATV Distillation Guide

> The complete methodology for distilling a content creator's style into reusable templates.

---

## Core Principle: Metadata-First, Then Select, Then Download

**Never start downloading/ASR with only partial data!** The correct flow:

```
Full metadata pull (lightweight, ~$0.001/item) → Rank & select top 50 → Download audio + ASR (heavy)
```

---

## Phase 0: Full Metadata Pull

### Goal
Get **all** video metadata from the target account — not a single one missing. This step only fetches metadata (aweme_id, likes, comments, timestamp, description), no audio/video downloads.

### Data Sources
Content from a creator typically falls into two categories:
1. **Independent posts** — Regular published videos
2. **Collection/Series** — Grouped content (e.g., a multi-episode series)

### Steps

```
Step 0.1: Fetch independent posts
  Paginate through all independent posts until has_more=false
  Extract: aweme_id, desc, digg_count, comment_count, create_time, duration

Step 0.2: Check for collections/series
  Look for mix_id/series_id in the data from Step 0.1

Step 0.3: Fetch collection posts
  For each mix_id: paginate until has_more=false

Step 0.4: Merge & deduplicate
  Combine independent + collection posts
  Deduplicate by aweme_id (collections and independent posts may overlap)

Step 0.5: Report to user
  Output: total count, time span, like distribution, collection count
```

### Output Format (all_videos.json)

```json
[
  {
    "aweme_id": "7603587445958937898",
    "desc": "Video description...",
    "digg_count": 97875,
    "comment_count": 9604,
    "create_time": 1770372000,
    "duration": 278431,
    "source": "independent|mix:{mix_id}",
    "share_url": "..."
  }
]
```

### Key Rules
- **Phase 0 downloads zero audio/video files** — metadata only
- **Collections and independent posts may overlap** — must deduplicate by aweme_id
- **API rate limits** — control request spacing (e.g., 0.2-0.5s between paginated requests)

---

## Phase 1: Rank, Select & Transcribe

### Step 1.1: Selection (Must reach 50 items)

```
Read all_videos.json → Sort by digg_count descending

Selection rules:
  1. Select: Top 30 by likes + 20 most recent
  2. Merge & deduplicate (top 30 and recent 20 may overlap)
  3. If fewer than 50 after dedup:
     → Backfill from the full pool by like count (descending)
     → Until total ≥ 50
     → Exception: accounts with <50 total videos = collect all
  4. Output selected_50.json
```

### Step 1.2: Batch Download + ASR

```bash
python3 scripts/download_asr_concurrent.py \
  --selected metadata/selected_50.json \
  --audio-dir audio/ \
  --status status/status.json \
  --transcripts transcripts.json \
  --tikhub-key "YOUR_TIKHUB_API_KEY" \
  --sf-key "YOUR_SILICONFLOW_KEY"
```

- **Checkpoint resume**: re-running skips already-completed items
- If transcripts < 50, backfill from pool by like count
- Copyright-filtered videos should be replaced from the pool

### Audio URL Priority

| Field | Priority | Notes |
|-------|----------|-------|
| `audio_fallback_url` | 🥇 | Pure audio stream |
| `audio_url` | 🥈 | CDN direct |
| `video_url` → ffmpeg extract | 🥉 | Last resort |
| `music_url` | ❌ | **Never use!** Pure BGM, no speech |

---

## Phase 2: Transcript Verification

Confirm all ASR results are complete:
- Check status.json — all items should be `done`
- Re-download + re-ASR any failures
- Merge into transcripts.json

---

## Phase 3: RAATV 5-Step Distillation (JSON State Machine)

### State Machine Principle

```
distill_state.json tracks completion status and output of each step.
Unfinished step = cannot proceed to next.
Insufficient dimension count = step not done.
```

### ⚠️ Context Safety: Batch Reading

50 transcripts (~76K chars ~190K tokens) can overflow LLM context windows.

**Rules:**
- Never read all transcripts at once
- Process in 5 batches of 10 transcripts each
- After each batch: analyze → write results to distill_state.json → read next batch
- All 5 batches complete → merge results → generate final report

### The Steps

#### R — Read (Batch Processing)
Process transcripts in 5 batches of 10:
1. Read 10 transcripts
2. Analyze topic/duration distribution
3. Append to distill_state.json R field
4. Read next batch

After all 5 batches: mark R.done = true

#### A1 — Belief Layer (12-15 beliefs)
What does the creator fundamentally believe? Recurring assertions across all topics.
- Process in batches
- Extract high-frequency assertions with source citations
- Each belief must have at least 1 source reference

#### A2 — Strategy Layer (10 strategies)
How does the creator operate? Opening hooks, language style, structure patterns, taboos.
- Annotate opening strategies, analogy techniques, closing patterns

#### A3 — Content Formula Layer (12 formulas)
What specific structures do their titles/content follow?
- Categorize by topic → identify common structures → distill into formula templates
- Each formula must include reverse-search keywords for auditing

#### A4 — Oral DNA Layer (12-15 traits)
The uncopiable personal signature: catchphrases, tone, self-positioning, emotional markers.

#### Archive — Structured Profile
Compile a structured character profile: identity + beliefs + operational laws + content formulas + red lines.

#### T — Template
Translate core formulas into **cross-niche reusable principles**, each with:
- Prototype example (from original creator's content)
- Translation template
- AI reuse example

#### V — Verify
Trial-write 2-3 segments on new topics using the distilled style. Compare and evaluate. Note gaps and improvement areas.

---

## Phase 4: Content Audit (Mandatory)

Before finalizing the report:
- Physically verify all frequency numbers in the report
- Deviation > ±1 → correct before delivery
- Select TOP1 viral video, map each segment to a formula, verify coverage

---

## Phase 5: Output Delivery

### Deliverable Checklist
- [ ] `distill-analysis-{creator}.md` exists
- [ ] `transcripts-{creator}.json` exists
- [ ] Content audit passed (≥2 frequency verification points)

### Report Structure
```markdown
# {Creator} — RAATV 5-Step Distillation Analysis V{Version}

## 1. R — Material Inventory (topic distribution + duration distribution + total chars)
## 2. A — Four-Layer Pattern Extraction
  Belief Layer (12+) / Strategy Layer (10) / Formula Layer (12) / Oral DNA Layer (12+)
## 3. A — Structured Profile
## 4. T — Template (translation principles)
## 5. V — Verification (trial writes + evaluation)
## 6. Summary: Reusable vs. Uncopiable
```

---

## Phase 6: Cleanup

```bash
python3 scripts/cleanup.py --project-dir "/path/to/your/project"
```

Deletes: `audio/`, `status/`, `scripts/`, `logs/`, `segments/`
Keeps: distillation analysis + transcripts.json + metadata/ + distill_state.json

---

## Pitfall Reference

| # | Phase | Issue | Solution |
|---|-------|-------|----------|
| 1 | 0 | API returns partial results | Fetch independent + collection separately, paginate both |
| 2 | 0 | Collections overlap with independent | Deduplicate by aweme_id |
| 3 | 1 | music_url has no speech | Always skip music_url, use audio_fallback_url |
| 4 | 1 | ASR returns empty | Split long videos into 240s segments; validate char_count < duration×7 = no speech |
| 5 | 1 | Checkpoint lost | Write status.json after every single item |
| 6 | 3 | Dimension count inflated | distill_state.json enforces count tracking |
| 7 | 3 | Skipping steps | Previous step must be done before next |
| 8 | 3 | Formula coverage gaps | TOP1 viral video segment-by-segment mapping audit |
| 9 | 3 | Fake frequencies | Content audit enforces physical grep verification |
| 10 | 1 | Serial processing too slow | Must use ThreadPoolExecutor(10) |
| 11 | 1 | Audio fetch failures reduce count | Backfill from pool, target 55 to guarantee ≥50 |
| 12 | 3 | Reading 50 transcripts overflows context | Process in 5 batches of 10, persist after each batch |
