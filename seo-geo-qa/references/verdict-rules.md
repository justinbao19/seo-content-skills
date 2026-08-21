# Verdict rules

Use these as defaults, not dogma.

## FAIL

Fail when any of the following is true:
- one or more dead external links
- too many TIER-D sources
- SERP topic overlap is materially low
- the article is missing critical evidence for its core claims
- a core numerical or platform-behavior claim relies only on an unverified leak, screenshot, or unattributed copy
- the copy asserts causality while the evidence only establishes timing or correlation
- a volatile price, capability, availability, or eligibility claim has no date, scope, or source

## REVISE

Use REVISE in writer mode when:
- the article is not publish-ready
- the issues are fixable in another draft pass
- no human escalation is needed yet
- a usable source exists but the draft is missing sample scope, denominator, method, limitations, author, or update metadata
- the page has multiple thin URLs where one complete primary-intent page would be clearer
- the draft confuses retrieved, cited, and clicked sources or treats a domain-scoped query as proof of a hidden implementation

## PASS

Pass when:
- no critical issues remain
- weak-source warnings are tolerable or addressed
- the article has enough evidence to support its major claims
- the report does not reveal obvious structural reliability problems
- major claims are labeled and scoped as facts, observations, inferences, or hypotheses
- retrieval-readiness checks are satisfied for the page type, without implying a ranking or citation guarantee

## Warning-only issues

These should not fail an article by themselves:
- FAQ count slightly low
- a small number of moved links
- SERP analyzer temporarily unavailable
- a few TIER-C sources in otherwise strong evidence mix
- a vendor observation without independent corroboration, when it is clearly labeled and not used to prove causality
- missing optional `llms.txt` or schema when the page remains crawlable and semantically valid

## Degrade gracefully

If public search or target sites block automation:
- keep the report running
- emit warnings instead of crashing the whole workflow
- require editorial judgment on ambiguous cases
