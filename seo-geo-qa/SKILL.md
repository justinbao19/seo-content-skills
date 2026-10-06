---
name: seo-geo-qa
description: 'Audit SEO article drafts and published pages: link availability, source
  tiers, structure, SERP coverage, snippets and technical page checks. Produces reports
  and flags editorial review. Use for checking an existing draft or live URL; use
  seo-blog-writer to create an article.'
metadata:
  short-description: SEO content QA and post-publication checks
---

# SEO Content QA

Audit a saved draft or live page, keeping automatic measurements separate from editorial judgment. This Skill does not publish or rewrite an article unless requested.

## Inputs and requirements

- Draft mode: article Markdown path; keyword for optional SERP analysis; site domain for internal-link classification; optional JSON config.
- Live mode: the published URL; optional SEOmator installation and PageSpeed Insights key.
- Python 3.10+ and `curl`; pre-publish scripts use only the Python standard library. Search / fetch checks require network access. For AIHubMix pass `--site-domain aihubmix.com` or the actual target site.
- SERP analysis uses DuckDuckGo and may use Jina Reader (`r.jina.ai`) for public search / competitor URLs. Use `--no-jina` for direct HTTP only, or `--skip-serp` to omit SERP checks. Do not send internal or credential-bearing URLs to external reader services.
- SEOmator is optional for expanded live-page audits. Missing installation falls back to basic checks; report that coverage limit. Optional PageSpeed data is skipped without a key. No SEOmator rule count is guaranteed across versions.

Commands below run from the `product-skills` checkout. If this Skill is installed on its own, use its actual `scripts/` directory instead of assuming the repository layout. Resolve input paths relative to the current working directory.

## Draft review

```bash
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py /path/to/article.md \
  --keyword "target keyword" --site-domain aihubmix.com

# Use existing project defaults
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py /path/to/article.md \
  --keyword "target keyword" --config /path/to/seo-qa-config.json

# Skip public SERP access; still verifies article URLs over the network
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py /path/to/article.md \
  --site-domain aihubmix.com --skip-serp

# Return JSON on stdout only, without saving report files
python3 skills/seo-geo-qa/scripts/seo_qa_runner.py /path/to/article.md \
  --site-domain aihubmix.com --skip-serp --stdout-json
```

Default output: timestamped Markdown and JSON under `qa-reports/<article-stem>/` beside the article. `--report-dir` selects the exact output directory; config `reportDir` is relative to the invocation working directory and adds an article-slug subdirectory. See [configuration.md](references/configuration.md).

1. Run the draft runner and read the latest report for this article revision.
2. Address `critical_issues` first, then review warnings, unavailable checks and `llm_review_items`.
3. Verify core claims against the actual cited sources, even when URLs are live and tiers are favorable. Automatic source tiers / SERP overlap are heuristics; document any evidence-backed editorial disagreement without altering the raw report.
4. Hand concrete fixes to the writer, or fix them if authorized. `--mode writer` names fixable failures REVISE; it is not a passing verdict.
5. Recheck the revised artifact. Cap write / QA iteration at three rounds, then report unresolved items rather than looping or hiding failures.

## Verdicts and limitations

Draft runner verdicts are PASS / FAIL; writer mode can return REVISE. Live checks can return PASS / WARN / FAIL. **Process exit code 0 only means the report ran**, not that the article passed. Automation must inspect the JSON verdict, critical issues, warnings and review flags.

Automatic PASS is not publication approval or proof of factual correctness. Editorial review covers search intent, source-to-claim fit, current price / feature claims, misleading tested / best claims and any skipped checks, in addition to flagged items. A blocked fetch is not proof that a link is dead or a source is unreliable.

Known upstream limits: word counts and SERP term overlap favor whitespace-separated languages; relative Markdown links are not included in URL checks; source allowlists are heuristic; live-page false-positive suggestions need inspection of the original SEOmator findings, not automatic acceptance. No full accessibility, browser-rendering, indexing or ranking guarantee follows from this audit.

Read [source-tiers.md](references/source-tiers.md) for citation classification, [verdict-rules.md](references/verdict-rules.md) for decision interpretation, and [example-report.md](references/example-report.md) for an illustrative result.

## Snippet and long-tail review

Read [snippet-long-tail-upgrades.md](references/snippet-long-tail-upgrades.md) for title / description, multilingual intent, opening-answer and GSC evidence reviews. Review final rendered metadata after site templates add suffixes; distinguish low data volume from evidence for a rewrite. Recommendations are hypotheses, not performance promises.

## Standalone checks

```bash
python3 skills/seo-geo-qa/scripts/verify_links.py /path/to/article.md --site-domain aihubmix.com --json
python3 skills/seo-geo-qa/scripts/serp_gap_analyzer.py "target keyword" /path/to/article.md --no-jina --json
```

SERP `--urls` accepts explicit public competitor URLs and skips search. It does not disable Jina unless `--no-jina` is also supplied. Individual link/source checks may still query public search for indexing evidence.

## Post-publication checks

Use only for a supplied live URL within the current task. The checker reads the page; it does not deploy it.

```bash
# Basic and custom checks, no SEOmator dependency
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://aihubmix.com/ --no-seomator --json

# Include SEOmator when installed; see --help and installed CLI version
python3 skills/seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --json
```

The post-publish script writes its report to stdout; redirect it into the article output directory if persistence is needed. Optional config keys for SEOmator / PageSpeed apply to this script, not to the draft runner. The full SEOmator / PageSpeed integrations are environment-dependent; do not claim they ran when only fallback checks executed.
