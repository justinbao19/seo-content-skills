# Configuration

All scripts accept an optional `--config` JSON file. Pre-publish checks need no API keys.

```json
{
  "siteDomain": "aihubmix.com",
  "minFaqCount": 2,
  "minExternalLinks": 5,
  "maxTierD": 1,
  "tierADomains": ["aihubmix.com", "docs.aihubmix.com"],
  "brandDomains": ["aihubmix.com"]
}
```

These are editable defaults, not mandatory article quotas. First-party sources establish the publisher's own features / prices, not independent proof of quality or benchmark superiority.

## Draft runner and link verifier

| Field | Behavior |
| --- | --- |
| `siteDomain` | Bare domain or site URL; host and its subdomains count as internal, similarly named external domains do not. |
| `reportDir` | Draft runner only: absolute path or path relative to the command's working directory; an article-slug subdirectory is added. Omit to save beside the article. CLI `--report-dir` takes precedence and is the exact output directory. |
| `minFaqCount` | Draft warning threshold; default 2. Adapt to article type. |
| `minExternalLinks` | Draft warning threshold; default 5. Review evidence quality rather than padding counts. |
| `maxTierD` | Draft critical threshold; default 1. Heuristic source classification still needs review. |
| `tierADomains` / `tierBDomains` | Additional first-party / secondary source domains for the verifier. Use bare hostnames, no scheme or path. |
| `brandDomains` | Bare domain roots for within-brand redirect recognition. |
| `siteName` | Reserved metadata; currently not consumed by the scripts. |

`--mode writer` changes FAIL to REVISE. `--skip-serp` omits SERP checks, not article link requests. `--no-jina` disables Jina within SERP analysis. `--stdout-json` writes only JSON stdout and does not persist reports. No config setting overrides those flags.

## Live-page checker only

| Field | Behavior |
| --- | --- |
| `skipSeomator` | Default false; true uses basic / custom checks only. CLI `--no-seomator` also disables it. |
| `seomatorCategories` | Optional category list passed to the installed SEOmator CLI. Supported names depend on that version; CLI `--categories` overrides the list. |
| `psiApiKey` | Optional PageSpeed Insights key; omit to skip that service. Store credentials in an untracked local config, never in this repository. |

These fields are used only by `post_publish_check.py`; the draft runner does not run SEOmator or PageSpeed. Live-page reports go to stdout; `reportDir` does not apply.

## Failure and measurement interpretation

Search / network failures reduce coverage. Keep warnings and missing evidence in the final review. Link liveness, domain tiers, word counts and term overlap cannot alone prove factual reliability, content quality or likely ranking. Process success and editorial approval are separate.

## Optional image policy

`imageFormat: "webp"` enforces local WebP headers and Markdown/frontmatter image references. `publicRoot` resolves site-relative paths, relative to invocation cwd when not absolute. CLI alternatives: `--require-webp --public-root /path/to/public`. No image format requirement is inferred from a repository name or article path. Published checks inspect `<article>` image URL formats only; decoding/MIME and actual image delivery need separate validation.
