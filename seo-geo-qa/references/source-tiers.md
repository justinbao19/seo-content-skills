# Source tiers

Use source tiers to judge citation quality.

Tier is a quality signal, not a substitute for source role. A domain can host official,
editorial, user-generated, copied, or leaked material. Classify the specific page and
claim, not only the hostname.

## TIER-A

Primary / first-party sources.

Examples:
- official product pages
- official pricing pages
- first-party documentation
- official support articles
- company research published by the company itself

Best for:
- pricing
- feature availability
- platform support
- product positioning claims

For platform-behavior claims, an official source is TIER-A only for behavior or intent it
actually documents. A first-party announcement that says a model is “more reliable” does
not prove a particular hidden query strategy.

## Observational vendor sources

Treat a vendor's own monitoring or analytics dataset as **primary for its measurements**
but **secondary for another platform's internals**. Record the vendor's collection method,
sample coverage, denominator, date window, and commercial interest. Seek independent
corroboration before turning the observation into a broad product claim.

## TIER-B

Reputable secondary sources.

Examples:
- established review sites
- major publications
- analyst or research firms
- reputable editorial blogs with consistent standards

Best for:
- comparisons
- external evaluations
- market context
- supporting evidence around broader trends

## TIER-C

Usable but not ideal.

Examples:
- relevant niche blogs
- smaller editorial sites
- live pages with mixed authority signals

Use when:
- better evidence is unavailable
- the claim is low-risk
- the source adds context rather than being the sole proof

## TIER-D

Weak or reject.

Examples:
- thin pages
- stale or low-trust sites
- unsupported pages with poor index evidence
- spammy or scraped pages

Treat as:
- replace first
- do not use for high-risk factual claims
- fail if too many accumulate in one article

The following require manual review and should not be the sole evidence for a core claim:

- leaked or scraped system prompts without official provenance;
- unattributed screenshots, copied charts, or posts with no method;
- a GitHub page that is not owned by the product publisher;
- a live page whose only evidence of authority is a matching domain name.

## Practical rule

For hard facts, prefer TIER-A.
For comparison framing, prefer TIER-B.
Use TIER-C sparingly.
Treat TIER-D as cleanup debt at best and disqualifying evidence at worst.

When a source is both high-domain-reputation and unverified at page level, keep the domain
tier but add an **unverified source-role warning**; do not silently upgrade it to official.
