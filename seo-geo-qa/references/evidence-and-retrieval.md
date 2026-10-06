# Evidence and retrieval QA

Use this reference when a draft makes platform-behavior claims, reports original
measurements, contains volatile product facts, or is being designed as a retrieval
surface for AI search.

## 1. Label the claim before judging the source

| Label | Meaning | Minimum support |
| --- | --- | --- |
| Fact | A current, directly supported statement | First-party announcement, official documentation, or directly inspectable page behavior |
| Observation | A measured result from a named dataset | Date, scope, denominator, sample/coverage, collection method, and limitations |
| Inference | An explanation of an observation | Clearly marked as interpretation and corroborated where possible |
| Hypothesis | A tactic or expected outcome to test | Test design and success metrics; never phrase as a guarantee |

Do not let a draft turn an observation into a product fact, or an inference into a
confirmed implementation detail. “After the rollout” is a chronology claim; it is not
evidence that the rollout caused the change.

## 2. Claim-evidence matrix

For each high-impact claim, capture:

```text
claim_id
claim_text
claim_label: Fact | Observation | Inference | Hypothesis
source_url
source_role: official | observational-vendor | independent-secondary | user-generated | unverified
source_owner
published_at
last_verified_at
observation_window
sample_count
denominator
metric_definition
scope: model / product surface / locale / plan / region
evidence_excerpt_or_field
limitations
editorial_decision: keep | qualify | replace | remove
```

For arithmetic, preserve the inputs and formula. For example, a change from `0.37%` to
`16.8%` is about `45.4x` the original share, while `1.08` to `1.83` is `+0.75` and about
`+69%`. Do not round away the denominator or imply a larger effect than the data shows.

## 3. Source-role rules

- An official source is authoritative for its own announcement, documentation, pricing,
  or product behavior. It is not automatically evidence for an internal mechanism it
  does not disclose.
- An observational vendor dataset is primary evidence for what that vendor measured,
  but secondary evidence for another platform's internals. Record commercial interest
  and sampling limitations.
- An independent secondary source can corroborate an observation, but does not replace
  the underlying data or prove causality.
- A user-generated page, leaked prompt, copied system prompt, or unattributed screenshot
  is unverified unless ownership, version, provenance, and current relevance are shown.
  It must not be the sole support for a core claim.
- Domain allowlists are hints, not authority. `github.com`, a publisher's domain, or an
  HTTP 200 response does not prove that the specific page is official or trustworthy.

## 4. Retrieval-readiness review

For each important URL, check:

- one primary intent and a page type that matches it;
- answer/definition near the top, with exceptions and scope;
- self-contained factual paragraphs rather than slogans or contextless fragments;
- title, H1, description, author, publication/update dates, and visible page content agree;
- truthful JSON-LD appropriate to the page type;
- server-visible content, HTTP 200, canonical, robots, sitemap, redirects, and hreflang;
- internal links from relevant hub/detail pages, without relying on site search alone;
- source, unit, version, effective date, and last-verified date for volatile facts;
- enough original content to justify a separate URL; otherwise consolidate related subquestions.

Treat robots, `llms.txt`, schema, internal links, and crawlability as eligibility signals,
not guarantees of retrieval or citation.

## 5. Fanout and domain-scoped observations

If a monitoring tool exposes subqueries, store at least:

```text
observed_at
window_start / window_end
model / product_surface / locale / plan / region
prompt_set and sample_count
fanout_count and denominator
domain_scoped_count and denominator
query_definition (for example, literal site: token or domains filter)
retrieved_urls
cited_urls
clicked_urls
collection_method and source_url
limitations
```

Do not assume a literal `site:` token means the internal API uses that syntax. Do not
assume domain-scoped queries run after broad queries; the data may only show that the
paths co-occur or are layered. Do not claim quality improvement without outcome metrics
such as retrieval recall, citation precision, source diversity, factual correctness,
unsupported-claim rate, latency, and cost.

## 6. Verdict guidance

Fail or block publication when a core numerical/platform claim has no adequate evidence,
the only support is an unverified leak, a source is dead, or the copy asserts causality
that the evidence cannot establish.

Use REVISE when the source is usable but the draft is missing scope, date, method,
limitations, author/update metadata, or a clear distinction between observation and
inference.

PASS requires that major claims are supportable, correctly scoped, and presented with
appropriate uncertainty; it does not mean that a page is guaranteed to rank or be cited.
