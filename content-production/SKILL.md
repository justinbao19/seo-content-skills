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
- **SEO blog articles** → `seo-blog-writer/SKILL.md` (research → native-language draft → whole-piece edit → factual and format QA). Save substantial milestones for resumption; no separate protocol Skill is required.
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

**Session 1 — Write + QA**:
```
Load seo-blog-writer
→ Understand reader, intent, evidence, and language
→ Draft and edit the whole article in the target language
→ Check factual support, useful decisions, links, and format
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
- [ ] The article has the depth its reader and evidence require
- [ ] Title and description accurately describe the page in the reader's language
- [ ] H2/H3 structure is logical
- [ ] Comparisons have explicit criteria and evidence-backed tradeoffs where relevant
- [ ] Product info is accurate (check product/ context)
- [ ] Competitor info is current (pricing, features)
- [ ] No brand voice violations (check brand/ context)
- [ ] FAQ, internal links, and CTA are present when they help the reader or the destination requires them
- [ ] No fluff paragraphs
- [ ] The piece helps the reader decide or act without forcing an unsupported winner
- [ ] English voice or Chinese localization reads naturally across the whole article

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
