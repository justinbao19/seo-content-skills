---
name: content-production
description: "Mandatory workflow for ALL content production — blog articles, social posts, email copy, ad copy, release notes. Every piece of content MUST go through produce → review → revise. Auto-spawn a review agent after every content draft. This skill triggers whenever you write, draft, or produce any content."
---

# Content Production Workflow

**This is mandatory. No content ships without review.**

## Core Rule

Every content task follows: **Produce → Review → Revise → Deliver**

Never deliver a first draft directly. Always spawn a review agent.

---

## Workflow

### Step 1: Produce
Write the content using the appropriate skill:
- **SEO blog articles** → `seo-blog-writer/SKILL.md` (fully automated: keyword research → competitive analysis → write → QA → delivery package). Mandatory dependency: `heavy-task-protocol/SKILL.md` — load it first for checkpoint/resume safety.
- **Marketing copy** → your copywriting skill
- **Comparison pages** → your competitor-alternatives skill
- **Social posts** → your social-content skill
- **Email sequences** → your email-sequence skill
- **Landing pages** → your page-cro skill + copywriting skill
- **Release notes** → your release-notes skill

### Step 2: Auto-Review
Immediately after producing, spawn a review sub-agent with the appropriate review profile below. Use a cheaper model (sonnet) for review to save cost.

### Step 3: Revise
Apply review feedback. If critical issues found (broken links, factual errors, brand violations), fix and re-review.

### Step 4: Deliver
Only after review passes, deliver to the user.

### Step 5: Post-Publish Verification (separate session after publishing)

**This step runs in a NEW session after the article is live.** Do not chain it into the same writing session — context would be too large and external dependencies (seomator, PSI API) add failure risk.

Trigger: user confirms the article is published and provides the live URL.

```bash
python3 seo-geo-qa/scripts/post_publish_check.py https://your-domain.com/blog/your-slug

# With Core Web Vitals (if PSI API key is configured)
python3 seo-geo-qa/scripts/post_publish_check.py https://your-domain.com/blog/your-slug --psi-key YOUR_KEY
```

Verdict:
- **PASS** — no action needed
- **WARN** — review seomator findings, fix high-priority items
- **FAIL** — fix critical issues (noindex, broken canonical, missing H1) before the page gets indexed

---

### SEO Blog Pipeline (Full Lifecycle)

**Session 1 — Write + QA** (heavy task, checkpoint protocol required):
```
Load heavy-task-protocol → Load seo-blog-writer
→ Phase 0: Context discovery + confirmation gate
→ Phase 1–4: Research, write, QA, iterate
→ Decision-Grade Quality Gate (before Phase 5)
→ Write draft + QA report to disk
→ Spawn content-qa review agent
→ Revise until PASS
→ Deliver
```

**Session 2 — Publish** (human-driven):
```
Take draft from disk → publish to CMS/repo
```

**Session 3 — Post-publish** (separate, lightweight):
```
Run post_publish_check.py on live URL → report verdict
```

---

## Review Profiles

### SEO Blog Article
**Reference docs:**
- `content-qa/SKILL.md` — QA checklist framework
- `seo-geo-qa/SKILL.md` — technical SEO checks and link verification
- `brand/voice.md` — brand voice, red lines, tone guidelines (provide via Brand Context input)
- `product/` — product facts (pricing, features, platforms)

**Checklist:**
- [ ] All external links verified (no 404/403)
- [ ] All internal links point to real pages on your domain
- [ ] Word count meets target (2500-3500 for comparison articles)
- [ ] Title includes primary keyword
- [ ] Meta description under 160 chars, includes keyword
- [ ] H2/H3 structure is logical
- [ ] Comparison table present and accurate
- [ ] Product info is accurate (check product/ context)
- [ ] Competitor info is current (pricing, features)
- [ ] No brand voice violations (check brand/ context)
- [ ] FAQ section present (for schema markup)
- [ ] Internal links to other blog posts included
- [ ] CTA present
- [ ] No fluff paragraphs
- [ ] Decision-Grade Quality Gate passed (exclusion boundaries, ranking fallback, decision engine, convergence summary)

### Social Post (X / LinkedIn)
**Reference docs:**
- Your social content skill
- `brand/voice.md` — brand voice guidelines

**Checklist:**
- [ ] Within character/format limits for platform
- [ ] Stays in product's topic lane
- [ ] No hashtag spam (0-1 max for X)
- [ ] Matches brand voice
- [ ] Clear point or take
- [ ] Engagement hook or CTA present

### Email Sequence
**Reference docs:**
- Your email-sequence skill
- `brand/voice.md`

**Checklist:**
- [ ] Subject line under 50 characters
- [ ] No spam trigger words in subject
- [ ] Unsubscribe link present
- [ ] Each email has ONE primary CTA
- [ ] Sequence logic makes sense
- [ ] All links work

### Ad Copy
**Reference docs:**
- Your paid-ads skill
- `brand/voice.md`

**Checklist:**
- [ ] Character limits met for platform
- [ ] CTA clear
- [ ] Value prop in first line
- [ ] No competitor names in ad (policy risk)
- [ ] Matches landing page messaging

### Landing Page
**Reference docs:**
- Your page-cro skill
- Your schema-markup skill
- `brand/voice.md`

**Checklist:**
- [ ] Above-fold: headline + value prop + CTA visible without scrolling
- [ ] Single primary CTA
- [ ] Social proof present
- [ ] H1 contains target keyword
- [ ] Meta description optimized
- [ ] Schema markup suggested

---

## Review Agent Spawn Template

```
sessions_spawn:
  task: |
    You are a content QA reviewer. Read content-qa/SKILL.md for your full checklist and protocol.

    Review the content at [FILE_PATH].

    Content Type: [seo-blog | ad-copy | social-post | email-sequence | landing-page]
    Target Keyword: [keyword] (SEO blog only)
    Brand Context: [path to brand/voice.md or inline brand guidelines]
    Round: 1

    Follow the full checklist for this content type in content-qa/SKILL.md.
    Use the automated QA runner (content-qa/scripts/run_qa.sh) for Step 0.
    Calculate SEO Quality Score (0-100) for blog articles.

    Output format: as defined in content-qa/SKILL.md (PASS ✅ / FAIL ❌).
  mode: run
  model: sonnet
```

---

## When to Skip Review

Never. But you can use a lighter review for:
- Internal notes/memos (no review needed)
- Casual conversational replies

Everything that goes **public** gets reviewed.
