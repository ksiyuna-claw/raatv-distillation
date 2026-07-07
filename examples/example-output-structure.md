# Example Output Structure

Below is a template showing the expected structure of a completed RAATV distillation analysis.

---

```markdown
# {Creator Name} — RAATV 5-Step Distillation Analysis V1.0

## 1. R — Material Inventory

### Overview
| Metric | Value |
|--------|-------|
| Total transcripts | 50 |
| Total characters | ~76,000 |
| Topics covered | Topic A, Topic B, Topic C, ... |

### Topic Distribution
| Topic | Count | % |
|-------|-------|---|
| Topic A | 15 | 30% |
| Topic B | 12 | 24% |
| Topic C | 10 | 20% |
| Other | 13 | 26% |

### Duration Distribution
| Category | Count | % |
|----------|-------|---|
| Short (<60s) | 8 | 16% |
| Medium (60-180s) | 25 | 50% |
| Long (>180s) | 17 | 34% |

---

## 2. A — Four-Layer Pattern Extraction

### A1: Belief Layer (12-15 beliefs)

| # | Belief | Source Citations |
|---|--------|-----------------|
| 1 | "Quality content always finds its audience" | Video #3, #7, #22 |
| 2 | "Controversy is a tool, not a goal" | Video #1, #15, #34 |
| ... | ... | ... |

### A2: Strategy Layer (10 strategies)

| # | Strategy | Description | Example |
|---|----------|-------------|---------|
| 1 | Question Hook Opening | Start with a provocative question | "Why do 90% of creators fail?" |
| 2 | Analogy Bridge | Connect complex ideas to familiar concepts | ... |
| ... | ... | ... | ... |

### A3: Content Formula Layer (12 formulas)

| # | Formula Name | Structure | Reverse-search Keywords |
|---|-------------|-----------|----------------------|
| 1 | "X个Y" List Formula | Title: "N things about..." | "X个", "X件事" |
| 2 | Contrarian Take | Title: "Everyone says X, but actually..." | "其实", "并不是" |
| ... | ... | ... | ... |

### A4: Oral DNA Layer (12-15 traits)

| # | Trait | Type | Example |
|---|-------|------|---------|
| 1 | Signature catchphrase | Verbal tic | "So here's the thing..." |
| 2 | Rhetorical questioning | Tone | Asks 3+ questions per video |
| ... | ... | ... | ... |

---

## 3. A — Structured Profile

### Identity
{Creator} is a {niche} content creator who {key characteristic}.

### Belief System
- Core thesis: {primary belief}
- Secondary beliefs: {supporting beliefs}

### Operational Laws
- Posting cadence: {frequency}
- Content pillars: {main topics}
- Engagement strategy: {how they interact with audience}

### Red Lines (What They Never Do)
- {taboo 1}
- {taboo 2}

---

## 4. T — Template (Translation Principles)

### Principle 1: {Name}
- **Prototype** (from creator): "{original quote}"
- **Translation template**: {how to adapt to other niches}
- **AI reuse example**: "{generated example in new niche}"

### Principle 2: {Name}
- **Prototype**: ...
- **Translation template**: ...
- **AI reuse example**: ...

---

## 5. V — Verification

### Trial Write 1: {New Topic}
**Written segment**: {AI-generated content using distilled style}

**Comparison**:
| Dimension | Similarity | Gap |
|-----------|-----------|-----|
| Tone | 85% | Slightly more formal |
| Structure | 90% | Good match |
| Catchphrases | 70% | Missing signature phrases |

### Trial Write 2: {New Topic}
...

---

## 6. Summary: Reusable vs. Uncopiable

### ✅ Reusable (Can be replicated)
- Content formulas and structures
- Opening hook patterns
- Topic selection strategy
- Analogy techniques

### ❌ Uncopiable (Personal DNA)
- Specific catchphrases
- Natural vocal cadence
- Personal backstory and authority
- Unique emotional register
```

---

## distill_state.json Example

```json
{
  "target": "example-creator",
  "total_transcripts": 50,
  "total_chars": 76000,
  "current_phase": "V",
  "phases": {
    "R": {
      "done": true,
      "theme_distribution": {"topic_a": 15, "topic_b": 12},
      "duration_distribution": {"short": 8, "medium": 25, "long": 17}
    },
    "A1": {
      "done": true,
      "beliefs": ["..."],
      "count": 14,
      "target_count": 12
    },
    "A2": {
      "done": true,
      "strategies": ["..."],
      "count": 10,
      "target_count": 10
    },
    "A3": {
      "done": true,
      "formulas": ["..."],
      "count": 12,
      "target_count": 12
    },
    "A4": {
      "done": true,
      "oral_genes": ["..."],
      "count": 13,
      "target_count": 12
    },
    "archive": { "done": true },
    "template": {
      "done": true,
      "translation_principles": ["..."]
    },
    "verify": {
      "done": true,
      "trial_writes": ["..."],
      "gap_notes": "Tone needs more warmth in trial writes"
    }
  }
}
```
