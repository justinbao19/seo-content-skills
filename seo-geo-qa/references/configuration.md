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
- `psiApiKey` — PageSpeed Insights API key; enables CWV field data in post-publish checks. Leave null to skip CWV.
- `seomatorCategories` — limit SEOmator audit to specific categories for faster runs. Omit for the full audit.
- `skipSeomator` — set `true` to disable SEOmator and run custom checks only.

Domain lists are convenience defaults for automated triage. They do not prove that every
page on a domain is official. A project using `github.com`, a media network, or a large
publisher in `tierADomains` should add manual page-level review for leaks, user-generated
content, copied material, and pages without clear ownership.

## Notes

- The runner works without config.
- Keep config small. If your config becomes huge, your process is probably overfitted.
- Prefer stable project defaults over article-by-article micromanagement.
- Keep observation metadata (sample scope, denominator, collection method, and limitations)
  with the report or evidence manifest; do not encode it as a domain allowlist.
