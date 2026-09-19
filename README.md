# Content Review Prioritization

This project explores how to rank published pages for human review when a content team has
more pages than it can investigate. It follows **Lane 2: Refresh / Content Opportunity
Scoring** in the FlyRank ML Internship.

The central question is:

> Given limited editorial capacity, which pages should a team review first, based on
> observable search performance and evidence of decline or opportunity?

## The problem and why it matters

A website can accumulate thousands of published pages. Some continue attracting readers,
some lose search traffic, and others receive search exposure without attracting many clicks.
Editors need to decide where to spend their time: investigate a decline, update information,
improve a title, expand a useful page, or monitor a change before acting.

This project's working scenario assumes a team can review approximately **20 to 50 pages
per month**. That capacity is a planning assumption from the research question, not a
measured staffing limit for every client. The practical challenge is to turn a large inventory
into a short, explainable review queue.

Looking only at page age, total traffic, or the largest percentage drop can produce poor
priorities. An old page may still perform well. A large percentage drop may represent only
a few lost clicks. A high-traffic page may deserve protection even when its percentage
decline appears modest. The project will investigate whether combining several signals
produces a more useful ranking than a simple rule.

The consequences of a wrong recommendation run in both directions:

- **Unnecessary review:** the team spends limited time investigating a page with little
  evidence of a meaningful problem or opportunity.
- **Missed priority:** a page with substantial demand and sustained deterioration receives
  attention too late, or never reaches the review queue.

These are the operational costs the project aims to address. Financial returns and traffic
gains from acting on recommendations remain unmeasured.

## Who uses the result and what they receive

Content strategists and SEO managers would use the ranking to plan a review cycle. Editors
would inspect the evidence and decide whether a change is appropriate.

The intended output is one ranked entry per content item at a defined decision date, with:

- A pseudonymized content identifier and client identifier.
- A priority score whose meaning is documented. A score is not automatically a calibrated
  probability or an estimate of financial value.
- Measured evidence supporting the priority, such as exposure, traffic movement, or CTR.
- Reason codes, such as `declining_with_demand` or `low_ctr_visible_page`, where the
  measurements support them.
- A suggested next step for human investigation and any relevant data limitations.

For an illustrative comparison, a page with substantial search exposure and a sustained
traffic drop may deserve earlier investigation than a page whose clicks fell from two to
one. Both declined, but their scale and uncertainty differ. This example explains the
decision; it is not a reported finding from the warehouse.

## How success will be evaluated

The project will compare a transparent rule baseline with a learned ranking using the same
eligible pages, outcome definition, and validation split. A relevant measure is
**Precision@K**: among the top K recommended pages, what fraction meet the defined outcome?
K should match the assumed review capacity, such as 20 or 50 pages.

A high Precision@K for a decline label means the queue concentrates pages that meet that
decline definition. It does not measure whether refreshing them would succeed. Evaluation
should also examine missed cases, low-volume errors, performance across clients, and whether
the reason codes help a reviewer understand each recommendation.

Future-outcome experiments need validation that respects time. Holding out entire clients
provides an additional check on performance for clients not represented in training.
Features derived from the answer or measured after the decision cannot enter the model.

The bundled starter pipeline provides a reference example of comparing a baseline and a
model. Its results describe its starter-data proxy and split. They do not establish the
performance of this project's proposed warehouse ranking, which still needs its own tests.

## Scope and limits

- The project supports review decisions. Human reviewers determine whether to refresh,
  investigate further, or leave a page alone.
- Decline can reflect seasonality, changes in search results, tracking gaps, or traffic
  moving to another page. It does not always imply outdated content.
- Client histories vary in length. Eligibility filters can make the analyzed subset less
  representative of clients with limited tracking history.
- Snapshot metadata may not describe a page as it existed at an earlier prediction date.
  Historical use requires a timing check.
- Observational performance data cannot by itself establish that a refresh causes recovery,
  reveal Google's ranking algorithm, or quantify the return on an editorial change.
- Public outputs must use safe identifiers and summaries, without private client details,
  raw URLs, raw search queries, or credentials.

The selected problem and starter exploration are documented in the research-question
notebook. The warehouse label, feature checks, and model evaluation remain work to complete.
The internship setup and reference workflow follow below.

---

## FlyRank ML Internship: starter resources

**Applied Search Intelligence: Google Search Ranking & Discoverability**

This is the starting point for the FlyRank ML Internship. You **clone it into your own public
repo** (one click — *Use this template*), build everything there, and submit that repo URL on
each assignment in your portal — it's your workspace, your submission, and your portfolio all
at once. The rhythm is simple: do the work, commit it, submit on the card. Done.

Everything here runs on a small **anonymized** slice of real FlyRank search data. No credentials,
no private client data, no setup headaches.

> **New here?** Two reads: **[SETUP.md](SETUP.md)** (GitHub, Colab, and data access — ten
> minutes, with every silent pitfall flagged), then **[GUIDE.md](GUIDE.md)** (every file
> explained, what to edit vs. leave alone, and where your own work goes — five minutes).

---

## Quickstart — first win in 2 minutes

The fastest path is Google Colab (one click, zero install). Open Notebook 1 and run all cells:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/notebooks/01_first_look_and_discovery.ipynb?flush_cache=true)
 **Week 1 — Run it, then discover a real truth yourself**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/notebooks/02_your_first_readable_model.ipynb?flush_cache=true)
 **Week 2 — The model is just a rule you can read**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/notebooks/03_working_with_the_full_release.ipynb?flush_cache=true)
 **Weeks 3+ — The full release (~79M rows) via DuckDB, no download needed** — hosted at
 [`FlyRank/internship-warehouse`](https://huggingface.co/datasets/FlyRank/internship-warehouse) (gated: request access + accept the data-use terms, approval is instant)

---

## Your assignment notebooks — open, fill, save, done

Every assignment is one pre-named skeleton notebook in `work/notebooks/`. Click its badge,
fill the sections in order, then **File → Save a copy in GitHub → OK** — the dialog is
already pre-filled with your repo and the right path.

> **The badges know whose repo they're in.** About 30 seconds after you create your copy, an
> automatic commit ("Point Colab badges at this copy") rewires every badge in it to open
> **your** notebooks — with your saved work — instead of the shared read-only ones. Reading
> this on the shared starter page? The badges below open blank previews; make your copy
> first ([SETUP.md](SETUP.md), Moment 1).

| Week | Card | Notebook | Open |
|---|---|---|---|
| 1 | ML-02 | `w01_research_question` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w01_research_question.ipynb?flush_cache=true) |
| 2 | ML-03 | `w02_ml_task_framing` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w02_ml_task_framing.ipynb?flush_cache=true) |
| 3 | ML-04 | `w03_data_contract` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w03_data_contract.ipynb?flush_cache=true) |
| 3 | ML-05 | `w03_feature_leakage_check` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w03_feature_leakage_check.ipynb?flush_cache=true) |
| 4 | ML-06 | `w04_signal_audit` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w04_signal_audit.ipynb?flush_cache=true) |
| 4 | ML-07 | `w04_baseline_score` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w04_baseline_score.ipynb?flush_cache=true) |
| 5 | ML-08 | `w05_model` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w05_model.ipynb?flush_cache=true) |
| 6 | ML-09 | `w06_validation_audit` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w06_validation_audit.ipynb?flush_cache=true) |
| 7 | ML-10 | `w07_action_playbook` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/w07_action_playbook.ipynb?flush_cache=true) |
| 8 | ML-11 | `capstone` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CodeJamjamzz/flyrank-machine-learning-work/blob/main/work/notebooks/capstone.ipynb?flush_cache=true) |

Badges not opening *your* copy? Colab's built-in opener always works: **File → Open notebook
→ GitHub tab** → paste `github.com/you/your-repo` → pick the notebook.

### Prefer local?

```bash
git clone <this-repo-url>
cd flyrank-ml-internship-starter
pip install -r requirements.txt          # or: uv pip install -r requirements.txt
python scripts/run_all.py
```

That runs the whole pipeline on the bundled sample and writes results to `outputs/`.

---

## What you get

| Path | What it is |
|---|---|
| `notebooks/` | Week 1–2 **first-win notebooks** (Colab-ready). Start here. |
| `scripts/01–05` + `run_all.py` | The runnable reference pipeline: prepare → baseline → train → evaluate → PDF. |
| `data/raw/content_refresh_anonymized.csv` | The anonymized starter dataset (~30k pages). |
| `outputs/` | Example outputs so you can see the **target shape** (`model_report.md`, `refresh_queue_sample.csv`, `charts/`). |
| `work/` | **Your space.** Lane experiments and your capstone live here — see `work/README.md`. |
| `docs/` | The core docs + the data dictionary (see below). |

### Read these (in `docs/`)

1. **`ml-core-foundation-framework.md`** — the first-principles map of ML as a whole system. The backbone of the live sessions.
2. **`ml-intern-dataset-and-lane-guide.md`** — how to use the data safely, the capstone workflow, and the analysis "lanes" you can pick from.
3. **`intern-free-tooling-guide.md`** — the zero-budget tool stack (Python, Colab, free AI assistants). You never need to pay for anything.
4. **`data-dictionary.md`** — all 44 columns: meaning, scale, and gotchas. Keep it open while you work.

---

## The pipeline (what `run_all.py` does)

```text
01_prepare_features.py   clean + build the feature vector, define the label
02_baseline_score.py     a transparent hand-rule "fix this first" score
03_train_model.py        logistic regression, decision tree, random forest (client-holdout split)
04_evaluate_and_export.py  ranked queue + charts + Markdown report
05_build_pdf_report.py   a shareable PDF summary
```

On the bundled sample, the learned model clearly beats the hand-written rule at picking the right
pages to review first (**Precision@50 ≈ 0.24 → 0.74**; the model number can land 0.68–0.74
depending on library versions — the ~3x lift is the point). The notebooks compute these numbers
live, so they always reflect the current data and environment.

**Teaching point:** the model is the capstone, but the *workflow* is the lesson —
`problem framing → data cleaning → baseline → first model → evaluation → explainable recommendation`.

---

## Data safety (read `DATA_USE.md`)

- Only the small **anonymized** CSV ships here — no client names, domains, URLs, titles, or keywords.
- **Never** add raw private client data to this repo or your fork. Need more data? Request an approved
  release from your mentor — never export it yourself.
- Don't paste client data into third-party AI tools.
- Frame every result as **observed / measured / directional / decision-support** — never
  "I predicted Google's algorithm."

The `.gitignore` blocks datasets by default, and CI fails any commit that includes a dataset.

---

## Assignments & schedule

Weekly assignments, live events, and the capstone live on **your portal board** (your
enrollment email has your access link). This repo is the shared technical foundation they all
build on — and the `skills/` folder here is the instruction library for your AI assistant
(start at [skills/README.md](skills/README.md)).

**First time with GitHub?** You need exactly four things (full walkthrough: [SETUP.md](SETUP.md)):
1. A free account at github.com.
2. Your own copy of this repo: **Use this template → Create a new repository** → public.
   (One click — brings the notebooks, `work/`, and the CI leak-guard with it.)
3. In Colab: *File → Save a copy in GitHub* — opened from your copy's badges, the dialog is
   already pre-filled with your repo and path, so it's just OK (Colab handles auth).
4. That's your submission repo — share its **github.com/you/your-repo** URL with Assignment 1
   (never a colab.research.google.com or drive.google.com link).

---

*Track leads: Mirza Ašćerić (ML) · Hole (data engineering). Code under MIT (see `LICENSE`); data under `DATA_USE.md`.*
