# SEO Content Skills

A complete SEO content production suite for AI agents. Four skills that cover the full lifecycle — from writing to QA to post-publish verification.

Works with [Claude Code](https://claude.ai/code), [OpenClaw](https://openclaw.ai), and any agent runtime that supports `SKILL.md`.

---

## How They Fit Together

```
Session 1 — Write + Review
─────────────────────────────────────────────────────
content-production   ← entry point, orchestrates everything
  │
  ├─ seo-blog-writer  ← automated research + writing (Phase 0–4)
  │    └─ Decision-Grade Quality Gate (before delivery)
  │
  └─ content-qa       ← LLM review agent (spawned after draft)
       └─ seo-geo-qa scripts ← automated link/source/SERP checks (Step 0)

Session 2 — Publish (human)

Session 3 — Post-Publish Verification
─────────────────────────────────────────────────────
  seo-geo-qa/scripts/post_publish_check.py ← 251-rule technical audit
```

---

## The Four Skills

### 1. `seo-blog-writer` — Automated SEO Writing
Fully automated article production. Give it a topic and domain — it handles keyword research, competitive analysis, writing, link verification, and delivery.

- **Modes:** Express (5-10 min) / Standard (15-20 min) / Expert (25-35 min)
- **Output:** Article + QA report + schema markup + promotion checklist
- **Gate:** Decision-Grade Quality Gate before delivery (exclusion boundaries, ranking fallback, decision engine, convergence summary)

```
topic: "best AI email apps 2026"
domain: "https://yoursite.com"
mode: "standard"
```

### 2. `content-qa` — LLM Content Review Agent
Ruthless, objective QA reviewer. Runs automated checks first (via seo-geo-qa scripts), then applies editorial judgment. Outputs PASS/FAIL with specific, actionable fix requirements.

- **Supports:** SEO blog, ad copy, social post, email sequence, landing page
- **Scoring:** SEO quality score (0-100) for blog articles
- **Max rounds:** 3, then escalates to human

### 3. `seo-geo-qa` — Technical SEO QA Scripts
Python script suite for deterministic checks. No LLM guessing on things scripts can measure precisely.

**Pre-publish (on draft markdown):**
```bash
python3 seo-geo-qa/scripts/seo_qa_runner.py article.md --keyword "best email apps"
```
- Link liveness + source quality (TIER-A through TIER-D)
- SERP gap analysis vs top competitors
- FAQ count, word count, internal/external link counts
- `llm_review_required` flag: identifies what needs editorial judgment

**Post-publish (on live URL):**
```bash
python3 seo-geo-qa/scripts/post_publish_check.py https://yoursite.com/blog/slug
```
- SEOmator CLI: 251 rules across 20 categories (Core SEO, Performance, Security, Schema, hreflang, AI/GEO Readiness…)
- Custom checks: llms.txt existence, hreflang self-reference, PageSpeed Insights CWV
- Verdict: PASS / WARN / FAIL

### 4. `content-production` — Orchestration Layer
Thin orchestrator that chains the other three skills into a complete Produce → Review → Revise → Deliver workflow. The entry point for any content task.

---

## Installation

```bash
# Clone the suite
git clone https://github.com/justinbao19/seo-content-skills.git

# Install SEOmator CLI (required for post-publish checks)
npm install -g @seomator/seo-audit

# Verify setup
seomator self doctor
python3 --version  # 3.10+ required
```

---

## Requirements

| Tool | Required for | Notes |
|---|---|---|
| Python 3.10+ | seo-geo-qa scripts | Standard library only, no pip deps |
| `curl` | Link verification | Must be in PATH |
| Node.js 18+ + SEOmator CLI | Post-publish checks | `npm install -g @seomator/seo-audit` |
| Network access to `r.jina.ai` | SERP analysis fallback | Browser rendering service for JS-heavy pages. Pass `--no-jina` to disable. |
| PageSpeed Insights API key | Core Web Vitals (CWV) | Optional. Free key at [developers.google.com](https://developers.google.com/speed/docs/insights/v5/get-started) |

---

## Usage

### Full pipeline (via content-production)
Load `content-production/SKILL.md` and say:
```
Write an SEO blog article about "best email apps for productivity" for https://yoursite.com
```
The orchestrator handles the rest.

### Individual skills
```bash
# Write only
# Load seo-blog-writer/SKILL.md → "Write a comparison article about [topic] for [domain]"

# QA only (pre-publish)
python3 seo-geo-qa/scripts/seo_qa_runner.py path/to/draft.md --keyword "your keyword"

# Post-publish audit
python3 seo-geo-qa/scripts/post_publish_check.py https://yoursite.com/blog/slug
```

---

## Configuration

Create a `seo-qa-config.json` for project defaults:

```json
{
  "siteDomain": "yoursite.com",
  "reportDir": "qa-reports",
  "minFaqCount": 2,
  "minExternalLinks": 5,
  "maxTierD": 1,
  "psiApiKey": "YOUR_KEY",
  "seomatorCategories": ["core", "technical", "schema", "ai-geo"]
}
```

See `seo-geo-qa/references/configuration.md` for all options.

---

## What Makes This Different

| Feature | This Suite | Typical SEO Tools |
|---|---|---|
| GEO / AI search optimization | ✅ Answer-first structure, standalone passages, AEO signals | ❌ |
| AI writing pattern detection | ✅ 20+ banned words/phrases | ❌ |
| Source quality tiers (TIER-A to D) | ✅ Citation credibility grading | ❌ |
| SERP gap analysis | ✅ vs top 5 competitors | Partial |
| Decision-grade content gate | ✅ Exclusion boundaries, decision engine, convergence | ❌ |
| `llm_review_required` flag | ✅ Scripts flag what needs editorial judgment | ❌ |
| Post-publish: 251 SEO rules | ✅ via SEOmator | Paid tools only |
| Post-publish: llms.txt + hreflang + CWV | ✅ Custom checks | Partial |
| Zero hardcoded dependencies | ✅ Works for any site/industry/CMS | ❌ |

---

## License

MIT
