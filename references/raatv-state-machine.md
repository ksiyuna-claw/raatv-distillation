# RAATV State Machine — Detailed Phase 2-6 Flow

## Phase 2: Transcript Verification

Confirm Phase 1 ASR results are complete:
- Read status.json, confirm all 50 items are `done`
- Re-download + re-ASR any failures
- Merge into transcripts.json

---

## Phase 3: RAATV 5-Step Distillation — JSON State Machine

### distill_state.json Template

```json
{
  "target": "creator-name",
  "total_transcripts": 0,
  "total_chars": 0,
  "current_phase": "R",
  "phases": {
    "R": {
      "done": false,
      "theme_distribution": {},
      "duration_distribution": {},
      "notes": ""
    },
    "A1": {
      "done": false,
      "beliefs": [],
      "count": 0,
      "target_count": 12
    },
    "A2": {
      "done": false,
      "strategies": [],
      "count": 0,
      "target_count": 10
    },
    "A3": {
      "done": false,
      "formulas": [],
      "count": 0,
      "target_count": 12
    },
    "A4": {
      "done": false,
      "oral_genes": [],
      "count": 0,
      "target_count": 12
    },
    "archive": {
      "done": false
    },
    "template": {
      "done": false,
      "translation_principles": []
    },
    "verify": {
      "done": false,
      "trial_writes": [],
      "gap_notes": ""
    }
  }
}
```

### Flow: Each Step = Read JSON → Analyze → Write JSON → Output

```
┌──────────────────────────────────────────────────┐
│ STEP R: Read                                      │
│   read distill_state.json                         │
│   read transcripts.json (in batches of 10)        │
│   → compute theme/duration distribution           │
│   → edit distill_state.json (fill R fields)       │
├──────────────────────────────────────────────────┤
│ STEP A1: Belief Layer                             │
│   read distill_state.json → confirm R.done=true   │
│   read transcripts.json (batch by batch)          │
│   → extract 12-15 beliefs                         │
│   → edit distill_state.json (fill A1 fields)      │
│   → count < target_count → not done, keep reading │
├──────────────────────────────────────────────────┤
│ STEP A2: Strategy Layer                           │
│   read distill_state.json → confirm A1.done=true  │
│   → extract 10 strategies                         │
│   → edit distill_state.json (fill A2 fields)      │
├──────────────────────────────────────────────────┤
│ STEP A3: Content Formula Layer                    │
│   read distill_state.json → confirm A2.done=true  │
│   → extract 12 content formulas                   │
│   → edit distill_state.json (fill A3 fields)      │
├──────────────────────────────────────────────────┤
│ STEP A4: Oral DNA Layer                           │
│   read distill_state.json → confirm A3.done=true  │
│   → extract 12-15 stylistic traits                │
│   → edit distill_state.json (fill A4 fields)      │
├──────────────────────────────────────────────────┤
│ STEP Archive: Structured Profile                  │
│   read distill_state.json → confirm A1-A4 done    │
│   → write structured character profile            │
│   → edit distill_state.json                       │
├──────────────────────────────────────────────────┤
│ STEP Template: Templating                         │
│   → translation principles + prototypes +         │
│     templates + AI reuse examples                 │
│   → edit distill_state.json                       │
├──────────────────────────────────────────────────┤
│ STEP Verify: Validation                           │
│   → trial-write 2-3 segments on new topics        │
│   → note gaps and improvement areas               │
│   → edit distill_state.json (done=true)           │
└──────────────────────────────────────────────────┘
```

### Iron Rules

- ⚠️ **Batch reading, no full-context dumps**. 50 transcripts (~76K chars ~190K tokens) can overflow context windows. **Read 10-15 at a time**, analyze immediately, persist to distill_state.json, then read the next batch.
- **Previous step not done = cannot proceed**. A1 incomplete blocks A2.
- **Insufficient dimension count = step not done**. Fewer than 12 beliefs, fewer than 10 strategies → cannot mark done.
- **Every step must edit distill_state.json**. Outputting text without writing JSON = violation.
- **After every batch of 10-15 transcripts, immediately analyze and persist**. Don't read everything then analyze.

### Layer-by-Layer Extraction Guide

#### R — Read (Batched)
⚠️ **Never read all transcripts at once. Split into 5 batches of 10.**

Each batch:
1. Read 10 transcripts (use offset/limit for precise reading)
2. Compute theme/duration stats for current batch
3. Append to distill_state.json R field (cumulative update)
4. Read next batch

After all 5 batches: total count, topic distribution, duration distribution → mark R.done = true

#### A1 — Belief Layer (12-15 beliefs, batched)
⚠️ **Batch reading, 10-15 per batch.**

Each batch:
1. Read current batch from transcripts.json
2. Extract high-frequency assertions, record to distill_state.json beliefs list
3. Annotate each belief with source citation
4. Read next batch

After all batches: merge, deduplicate, refine to 12-15 → mark A1.done=true
- What does the creator believe? Recurring underlying judgments across all topics
- Method: cross-topic search for high-frequency assertions, synthesize into beliefs
- Each belief must include at least 1 source citation

#### A2 — Strategy Layer (10 strategies, batched)
⚠️ **Batch reading, 10-15 per batch.**

Each batch:
1. Read current batch
2. Annotate opening strategies, analogy techniques, closing patterns
3. Append to distill_state.json strategies list
4. Read next batch

After all batches: merge, deduplicate, refine to 10 → mark A2.done=true
- How does the creator operate? Opening hooks, language style, structure patterns, no-go zones

#### A3 — Content Formula Layer (12 formulas, batched)
⚠️ **Batch reading, 10-15 per batch.**

Each batch:
1. Read current batch
2. Categorize by topic → identify common structures
3. Append to distill_state.json formulas list
4. Read next batch

After all batches: merge, deduplicate, refine to 12 → mark A3.done=true
- What specific structures do their titles/content follow?
- Method: categorize by topic → identify common structure → distill into formula template
- ⚠️ Must include reverse-search keywords for content audit

#### A4 — Oral DNA Layer (12-15 traits, batched)
⚠️ **Batch reading, 10-15 per batch.**

Each batch:
1. Read current batch
2. Extract catchphrases, tone, self-positioning, emotional markers
3. Append to distill_state.json oral_genes list
4. Read next batch

After all batches: merge, deduplicate, refine to 12-15 → mark A4.done=true
- Uncopiable personal signature: catchphrases, tone, self-positioning, emotional markers

#### Archive — Structured Profile
Structured character profile: identity description + belief system + operational laws + content formulas + red lines

#### Template — Templating
Translate core formulas into **cross-niche reusable translation principles**, each with:
- Prototype example (from original creator)
- Translation template
- AI reuse example

#### Verify — Validation
Trial-write 2-3 segments on uninvolved new topics, compare and evaluate. Note gaps and improvement areas.

---

## Phase 4: Content Audit (Mandatory)

Before finalizing the distillation report:
- Physically verify all frequency numbers in the report
- Deviation > ±1 → correct before delivery
- Select TOP1 viral video, map each segment to a formula, verify formula coverage

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

After report delivery, clean up intermediate files:

```bash
python3 scripts/cleanup.py --project-dir "/path/to/your/project"
```

Deletes: `audio/`, `status/`, `scripts/`, `logs/`, `segments/`
Keeps: distillation analysis + transcripts.json + metadata/ + distill_state.json
