---
name: content-qa
description: Review supplied articles, product copy, ads, social posts or emails for
  factual support, reader value, language and destination fit; report specific issues
  and required fixes.
metadata:
  version: 3.0.0
---

# Content review

Review the supplied artifact against its audience, purpose and actual destination requirements. A review-only request produces findings; revise when the user requests fixes. Do not invent flaws or rewrite merely to satisfy a preferred style.

## Scope and evidence

Read the draft, brief and available product/brand facts. Check material claims, quotes in their original context, comparisons, author experience, language, logic and usable next steps. Verify volatile facts from current primary sources. An accessible URL does not prove its claim; a blocked request is unverified, not automatically a dead link.

Use [review checklists](references/review-checklists.md) for the requested format only. Suggested word counts, link totals, FAQ, keyword density, CTA and rhetorical patterns are heuristics. Apply them as requirements only when the destination or brief actually sets that contract. Natural Chinese and English may use different structures. A phrase is not evidence of AI authorship.

For substantial SEO drafts, use an installed `seo-geo-qa` if available. This is a conditional technical dependency; absence does not prevent an editorial review. Report technical coverage as unavailable when it was not run. The optional wrapper is:

```bash
bash <this-skill>/scripts/run_qa.sh draft.md --skip-serp
```

Set `SEO_QA_SKILL_DIR` to a separately installed QA directory if it is not alongside this skill. The wrapper does not install or publish anything.

## Findings and verdict

Report the content type, scope, verdict, critical issues with locations and evidence, warnings, and checks not performed. PASS means no supported critical issue was found within the reviewed scope; FAIL means a material error or unmet explicit requirement remains. Unverified important claims must be verified, qualified or removed. Never call an automated PASS publication approval, a ranking guarantee or proof of human authorship.

Critical examples: false feature/price, misquoted source, unsupported central assertion, changed product behavior, missing required disclosure or broken required output. Style alternatives and optional metadata are warnings or notes. Scores may summarize an agreed rubric but cannot override material correctness or substitute for evidence.

For revisions, recheck changed passages and outstanding findings. After three unsuccessful review rounds, report unresolved items and the specific decision needed. Keep substantial reports next to the article or in the user’s output directory, never in the installed skill.
