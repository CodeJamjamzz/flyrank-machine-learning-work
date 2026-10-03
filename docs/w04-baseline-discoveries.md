# ML-07 · Assignment 4 — Baseline Action Score: Key Discoveries

**Notebook:** `work/notebooks/w04_baseline_score.ipynb`  
**Output:** `work/outputs/baseline_action_score.csv`  
**Branch:** `feat/w04-baseline-action-score`  
**Date completed:** 2026-10-03  
**Lane:** Lane 2 — Refresh / Content Opportunity Scoring  

---

## 1. Dataset ground truth (re-confirmed)

| Fact | Value |
|---|---|
| Total rows | 30,000 |
| Columns (raw) | 44 |
| Columns after label creation | 45 |
| Declining pages (`trend_direction == "down"`) | 16,262 / 30,000 = **54.2%** |
| Label source | `trend_direction` → `is_declining_label` — **NEVER a feature** |
| Label leakage trap confirmed | `impressions_last_30d / impressions_prev_30d` is the exact label formula — any rule using those columns gets 100% precision trivially and is pure leakage |

---

## 2. Signal 1 — Staleness (`days_since_last_update`)

**Flag link:** Behind FlyRank's content refresh flags.  
**Verdict: CONFIRMED (weak)**

### Bucket table

| Freshness tier (days since update) | n | % Declining | vs. base |
|---|---|---|---|
| 91–180 | 9,171 | **61.1%** | +6.9 pp |
| 31–90 | 175 | 58.9% | +4.7 pp |
| 0–30 | 20,480 | 51.1% | −3.1 pp |
| 181+ | 174 | 47.1% | −7.1 pp |

**Base rate: 54.2%**

### Key findings
- The 91–180 day bucket has the highest observed decline rate (+6.9 pp over base). Signal is real but modest.
- **Critical data quirk:** 8,773 of 9,171 stale rows (96%) share the exact same `days_since_last_update = 104`. The platform records edit dates in batch snapshots, not continuously. This means staleness is a **binary gate** rather than a continuous gradient within that tier.
- The 181+ day bucket is *below* base rate (47.1%) — counter-intuitive, but likely because very old content has already exited organic rankings entirely, so it shows flat rather than declining impressions, skipping the "down" classification.
- **Decision:** Use 91–180 day window as the stale gate; do not extend to 181+.

---

## 3. Signal 2 — Organic volume (`impressions_90d`, `impression_tier`)

**Flag link:** Behind FlyRank's quick-win logic (impression floor for actionable interventions).  
**Verdict: CONFIRMED**

### Bucket table

| Impression tier | n | % Declining | Median impressions_90d |
|---|---|---|---|
| moderate (300–3k) | 10,469 | **61.5%** | 998 |
| good (3k–30k) | 7,205 | **58.6%** | 7,249 |
| low (< 300) | 11,248 | 45.4% | 31 |
| excellent (30k+) | 1,078 | 46.2% | 48,675 |

**Base rate: 54.2%**

### Key findings
- Pages in the `moderate` and `good` tiers show meaningfully higher decline rates than base (+7.3 pp and +4.4 pp respectively).
- `low` tier (<300 impressions): 45.4% — *below* base. Low-visibility pages decline less in measured terms because they have already exited organic results; their impressions can't drop much further.
- `excellent` tier (30k+) also below base (46.2%) — top-tier pages may have more editorial attention, more authoritative content, or are trending topic pages protected by brand authority.
- **Decision:** Use ≥300 impressions as the visibility floor for rule eligibility.

---

## 4. Label leakage trap — confirmed and avoided

The impression trend columns (`impressions_last_30d`, `impressions_prev_30d`) are the **exact source of the label**:

```
trend_direction = "down"  ←→  impressions_last_30d < 0.8 × impressions_prev_30d
```

Cross-validated: max rounding difference of 0.05 pp. Any model or rule using these columns achieves 100% "precision" trivially — it's just reading the label. These columns are permanently banned as features.

**Safe feature columns confirmed for this assignment:**
- `days_since_last_update` ✅ — prior editorial event, not derived from trend
- `impressions_90d` ✅ — 90-day aggregate, not the decomposed 30d windows

---

## 5. The baseline rule

### Plain-English statement
> "A page is worth reviewing for a content refresh if it has enough organic traffic to make the effort worthwhile (≥ 300 impressions in 90 days, *visible*) AND it hasn't been updated in 91–180 days (*stale*). Among qualifying pages, those with higher search impressions get priority."

### Code formula
```python
flag_stale   = (days_since_last_update.between(91, 180)).astype(int)
flag_visible = (impressions_90d >= 300).astype(int)
score        = flag_stale × flag_visible × impressions_90d
reason_code  = "stale_but_visible"  |  "no_flag"
action       = "REVIEW_AND_REFRESH" |  "HOLD"
```

### Design decision
- Multiplying by `impressions_90d` makes raw exposure the tie-breaker within the stale cohort. This is intentional — among pages that both qualify, the highest-exposure ones have the most to lose from continued decay.
- There are no fitted weights. Every threshold is hand-chosen from observed data and logical reasoning.

---

## 6. Baseline evaluation results

| Metric | Value |
|---|---|
| Pages flagged (`REVIEW_AND_REFRESH`) | 7,212 / 30,000 (24.0%) |
| Declining among flagged | **61.7%** |
| Base rate | 54.2% |
| Lift over base | **+7.5 pp** |
| Precision@10 | **0.600** |
| Precision@50 | 0.440 |
| Precision@100 | 0.380 |
| Precision@200 | 0.390 |

> [!NOTE]
> Precision@50 (0.440) is *below* the base rate (0.542). This happens because the score ranking within the flagged queue is dominated by raw impressions volume, and the top-50 by impressions heavily overlaps the `excellent` tier — which has a *lower* decline rate (46.2%) than base. The rule surfaces the highest-exposure stale pages first, but those high-exposure pages are also the most likely to still be holding rank.

> [!IMPORTANT]
> This is the **target the Week-5 model must beat.** Any learned model should exceed Precision@K at K=10, 50, and 100 on the same data slice and labels.

---

## 7. Top-10 review: findings and weak picks

### Weak picks in the top 10 (flagged but NOT declining)
- **Rank 2** (443k impressions): Page is highly visible and stale, but currently stable. Risk of disrupting what's working.
- **Rank 6** (295k impressions): Large exposure, holding rank — pre-emptive flag only.
- **Rank 7** (287k impressions): Similar to rank 6; staleness may reflect unlogged minor edits.
- **Rank 9** (211k impressions): Currently stable; high exposure but no confirmed decline.

**4 of 10** top picks are weak (not actually declining). **11 of 20** top-20 picks are weak.

### Why weak picks concentrate at the top
All top-20 rows share `days_since_last_update = 104` (identical staleness). Score differences are driven entirely by `impressions_90d`. The highest-impression stale pages are in the `excellent` tier — which has the *lowest* decline rate of all tiers (46.2%). The rule's prioritization mechanism works against it: it promotes the very pages least likely to be declining.

---

## 8. What the baseline rule is missing (for Week-5 model)

| Missing signal | Why it would help | Evidence |
|---|---|---|
| **CTR vs. position** (CTR-fix logic) | Below-median CTR for a page's position tier flags optimization opportunity. page_1 low-CTR: 60.3% declining vs. 53.6% high-CTR. | +6.7 pp signal exists but not encoded to keep baseline simple. |
| **Granular staleness** | Continuous `days_since_last_update` rather than binary bucket would allow finer ranking within the stale cohort. | Blocked by platform batch-snapshot issue (96% of stale rows = 104 days). |
| **Engagement quality** | `engagement_rate`, `scroll_rate` — pages where users bounce quickly may be declining due to quality mismatch, not just age. | Not tested in this assignment. |
| **Content type segmentation** | `feedly article` rows have no keyword data; impression signal means something different for them. | Missingness is systematic — blind use injects a content-type proxy. |

---

## 9. Data quirks discovered (important for Week-5 model)

| Quirk | Impact |
|---|---|
| `days_since_last_update` clusters at 104 (96% of stale rows) | Staleness is a batch snapshot artifact. Cannot rely on it as a continuous signal without further investigation. |
| `excellent` impression tier has *lower* decline rate than `moderate` | High-traffic pages may have more editorial protection or audience loyalty. A model must not assume "more impressions = more at risk." |
| `avg_position = 0` means no data (1,205 rows) | Must filter to `avg_position > 0` before any position-based analysis. |
| `impressions_last_30d / impressions_prev_30d` = label | Never use these columns as features. This was re-confirmed empirically (100% label correlation). |
| `181+` freshness tier declines *less* than `0-30` | Very old un-updated content may have already exited rankings. Staleness beyond ~180 days is a different phenomenon. |

---

## 10. Files produced by this assignment

| File | Location | In git? | Notes |
|---|---|---|---|
| `w04_baseline_score.ipynb` (executed) | `work/notebooks/` | ✅ Yes | Primary deliverable |
| `baseline_action_score.csv` | `work/outputs/` | ❌ No (gitignored) | Regenerated by notebook on every run |
| `w04-baseline-discoveries.md` (this file) | `docs/` | ✅ Yes | Persistent record of findings |
