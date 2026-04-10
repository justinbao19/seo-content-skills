---
name: seo-geo-qa
displayName: SEO Content QA
description: "Check blog posts and articles before publishing, and audit live pages after publishing. Finds broken links, weak sources, missing SEO elements, and citation problems. Post-publish check runs 251 SEO rules via SEOmator CLI and adds custom checks for llms.txt, hreflang, and Core Web Vitals. Use when: reviewing a draft, auditing content quality, checking if links still work, verifying sources are credible, running pre-publish QA, or doing post-publish page checks. Also triggers on: 'check this article', 'verify my links', 'review before publishing', 'content audit', 'source quality check', 'are my links working', 'SEO review', 'pre-publish checklist', 'audit live page', 'check published page'. Generates markdown+JSON reports with PASS/FAIL verdict."
tags:
  - seo
  - content-qa
  - links
  - citations
  - publishing
---

# SEO Content QA

Use this skill to audit content reliability before or after publishing.

## Requirements

- **Python 3.10+** (scripts use modern type syntax)
- `curl` available in PATH (for HTTP HEAD checks)
- No pip dependencies for pre-publish scripts — standard library only
- **Network access to `r.jina.ai`** — used as a fallback for SERP search and competitor page fetching via browser rendering (handles JavaScript-heavy pages). Pass `--no-jina` to disable if needed.
- **Node.js 18+ + SEOmator CLI** — required for post-publish page checks (251 rules)
  ```bash
  npm install -g @seomator/seo-audit
  seomator self doctor   # verify installation
  ```
  If SEOmator is not installed, `post_publish_check.py` automatically falls back to basic checks (title / H1 / meta / canonical) and prints an install prompt.
- **PageSpeed Insights API key** — optional, enables Core Web Vitals field data (LCP / CLS / INP / FCP / TTFB). Pass via `--psi-key` or set in config.

## Quick start

Run the unified runner for normal draft review:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps"
```

If you know the site's main domain, pass it so internal vs external links are counted correctly:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps" --site-domain example.com
```

If you want project defaults, pass a lightweight JSON config:

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py path/to/article.md --keyword "best email apps" --config path/to/seo-geo-qa.json
```

## Standard workflow

1. Run `seo_qa_runner.py` on the draft.
2. Read the markdown report for the human audit trail.
3. Use the JSON report for automation or later aggregation.
4. Fix critical issues first.
5. Re-run until the article reaches PASS (or REVISE in writer mode).
6. After publishing, run `post_publish_check.py` on the live URL.

## Lower-level tools

Use these only when debugging a specific failure mode.

### Link/source verification
```bash
python3 skills/seo-geo-qa/scripts/verify_links.py path/to/article.md
python3 skills/seo-geo-qa/scripts/verify_links.py path/to/article.md --json
```

### SERP gap analysis

```bash
# Auto-search (uses DuckDuckGo + Jina Reader fallback for browser-rendered content access)
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "best email apps" path/to/article.md

# Supply competitor URLs directly (skips search, still uses Jina to fetch pages)
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "best email apps" path/to/article.md --urls https://competitor1.com https://competitor2.com

# Disable Jina (direct HTTP only, faster but may fail on JavaScript-rendered pages)
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "best email apps" path/to/article.md --no-jina
```

**How the SERP search works:**
1. Tries DuckDuckGo's HTML endpoint via direct HTTP (fast path)
2. If blocked or returns no results, falls back to Jina Reader (`r.jina.ai`) which renders the page with a real browser and decodes DDG's redirect links
3. Competitor pages are always fetched via Jina first (browser-rendered for reliable access), then falls back to direct HTTP

### Post-publish page check

Full audit (SEOmator 251 rules + custom checks for llms.txt / hreflang / CWV):

```bash
# Standard — SEOmator + custom checks
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post

# With Core Web Vitals (requires PageSpeed Insights API key)
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --psi-key YOUR_KEY

# Scope SEOmator to specific categories (faster)
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --categories core,technical,schema

# Lightweight fallback — skip SEOmator, run custom checks only
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --no-seomator

# JSON output for automation
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --json
```

**What the post-publish check covers:**

| Layer | Source | Checks |
|---|---|---|
| SEOmator | 251 rules / 20 categories | Core SEO, Performance, Links, Images, Security, Technical SEO, Schema, JS Rendering, Accessibility, Mobile, i18n, E-E-A-T, AI/GEO Readiness, … |
| Custom | llms.txt | Existence + HTTP 200 at `/llms.txt` |
| Custom | hreflang | Self-reference validation, return-link symmetry |
| Custom (optional) | PageSpeed Insights API | LCP, CLS, INP, FCP, TTFB field data |

## Report persistence

The runner writes timestamped markdown + JSON reports by default.

Default behavior:
- saves to `qa-reports/<article-slug>/` next to the article
- does not overwrite old reports
- uses markdown for human review and JSON for machine state

Override with `--report-dir` or config.

## Configuration

Read `references/configuration.md` when you need project-level defaults.

## Source quality

Read `references/source-tiers.md` when you need to decide whether a citation is acceptable.

## Verdict rules

Read `references/verdict-rules.md` when you need to tune PASS / FAIL / REVISE behavior.

## Example output

Read `references/example-report.md` for a real QA report with annotations on how to interpret each section.

## LLM review items

The `seo_qa_runner.py` JSON output includes a `llm_review_required` flag and a `llm_review_items` list. These identify checks that scripts cannot resolve deterministically — keyword intent alignment, borderline source quality, word count near thresholds, and SERP overlap edge cases.

When `llm_review_required` is `true`, read `llm_review_items` and apply editorial judgment before issuing a final verdict. Do not pass or fail on these items automatically.

## Design intent

This skill is not a writing assistant. It is a reliability layer.

Scripts handle deterministic checks (link liveness, source tiers, structural metrics).
LLM handles semantic judgment only — and only for items explicitly listed in `llm_review_items`.
Do not let LLM re-evaluate what scripts have already decided.
