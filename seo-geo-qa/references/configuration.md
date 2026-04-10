# Configuration

Use an optional JSON config file to set project defaults.

## Example

```json
{
  "siteName": "Example Site",
  "siteDomain": "example.com",
  "reportDir": "qa-reports",
  "minFaqCount": 2,
  "minExternalLinks": 5,
  "maxTierD": 1,
  "tierADomains": ["mycompany.com", "docs.mycompany.com"],
  "tierBDomains": ["partner-site.com"],
  "brandDomains": ["mycompany.com"],
  "psiApiKey": "YOUR_PAGESPEED_INSIGHTS_API_KEY",
  "seomatorCategories": ["core", "technical", "schema", "ai-geo"],
  "skipSeomator": false
}
```

## Fields

- `siteName` — optional metadata for your own reporting
- `siteDomain` — used to distinguish internal vs external links
- `reportDir` — report output root, relative to workspace root
- `minFaqCount` — warning threshold for FAQ count (default: 2)
- `minExternalLinks` — warning threshold for thin citation profiles (default: 5)
- `maxTierD` — maximum allowed TIER-D sources before FAIL (default: 1)
- `tierADomains` — additional domains to treat as TIER-A (first-party / official)
- `tierBDomains` — additional domains to treat as TIER-B (reputable secondary)
- `brandDomains` — domain roots for same-brand redirect detection (e.g., subdomains that should not count as "moved")
- `psiApiKey` — PageSpeed Insights API key; enables CWV field data (LCP/CLS/INP/FCP/TTFB) in post-publish checks. Leave null to skip CWV. Get a free key at https://developers.google.com/speed/docs/insights/v5/get-started
- `seomatorCategories` — limit SEOmator audit to specific categories for faster runs (e.g. `["core","technical","schema"]`). Omit for full 20-category audit. Valid values: `core`, `performance`, `links`, `images`, `security`, `technical`, `crawlability`, `schema`, `js`, `accessibility`, `content`, `social`, `eeat`, `url`, `redirects`, `mobile`, `i18n`, `html`, `ai-geo`, `legal`
- `skipSeomator` — set `true` to disable SEOmator and run custom checks only (useful in environments without Node.js; default: false)

## Notes

- The runner works without config.
- Keep config small. If your config becomes huge, your process is probably overfitted.
- Prefer stable project defaults over article-by-article micromanagement.
