# Snippet and long-tail upgrades

Use this reference when improving an existing article's title, meta description,
opening answer, or long-tail search coverage. The goal is a clearer retrieval surface,
not a denser keyword string.

## 1. Establish the evidence level

Before recommending a rewrite, record the available window, latest complete date,
page impressions, clicks, CTR, average position, and page-query rows.

- Treat delayed dates and privacy-suppressed query rows as missing detail, not zero demand.
- Treat a small number of impressions or a single short window as a weak signal. Preserve a
  promising title/intent unless another problem is directly inspectable.
- Separate facts from hypotheses. A proposed snippet is a test; it does not guarantee a
  ranking, click, retrieval, or citation improvement.
- Record the before state so later monitoring can attribute changes to the right revision.

## 2. Audit the rendered snippet, not only frontmatter

Inspect the final server-rendered HTML and include title templates, brand suffixes, escaping,
fallback descriptions, canonical URL, locale, and H1 in the review.

Title length is a display budget, not a universal character limit. Prefer this order:

1. primary intent or exact entity;
2. decision modifier such as comparison, guide, free, API, or use case;
3. one or a few differentiating entities when they match real queries;
4. brand suffix only when its recognition or trust value justifies the space.

If a global template makes otherwise useful titles likely to truncate, shorten or remove the
template before stripping the page's primary intent. Do not duplicate the same year, brand,
or category phrase in both the page title and template.

## 3. Give the description a job

The description should set an accurate expectation and earn the right click. Search engines
may rewrite it, so do not treat it as a fixed SERP contract.

- Map important entities to user jobs, trade-offs, or evaluation dimensions.
- Prefer concrete tasks such as editing, transcription, bot-free capture, Base64 input, or
  team governance over generic phrases such as “learn more” or “complete guide.”
- Avoid exhaustive product lists. Name only the entities needed to establish scope.
- Keep claims aligned with visible content and evidence. Do not promise “tested,” “best,” or
  benchmark superiority when the article does not support that standard.
- Write each locale naturally; do not mechanically translate English modifiers.

## 4. Distribute long-tail coverage

Use one primary intent per URL. Put only the main intent and strongest differentiator in the
title, then distribute related demand across the description, opening answer, H2s, comparison
table, FAQ, captions, and internal-link anchors.

Build a compact coverage map for the page:

- category discovery: “best” or “recommended” queries;
- decision comparisons: entity A vs entity B, workflow, price, open source, or team fit;
- task queries: what the user wants to accomplish;
- constraint queries: free, bot-free, local, language, API format, limits, or errors;
- brand/official queries: exact product and model names;
- follow-up questions that belong to the same primary intent.

Create a separate URL only when the subtopic has independent intent, enough original content,
and a distinct freshness or internal-link role. Otherwise strengthen the existing article.

## 5. Make the opening answer retrievable

The first answer block should normally resolve the decision in two or three short sentences:

1. direct recommendation or definition;
2. alternatives mapped to distinct use cases;
3. a material scope, evidence, freshness, or vendor-data caveat when needed.

Remove throat-clearing, repeated product inventories, and unexplained superlatives. Keep exact
entity names and technical identifiers when they are what users search for. A concise answer
improves extractability, but it does not guarantee AI citation.

## 6. Change and measurement discipline

- Avoid repeatedly rewriting a page with promising but sparse data.
- Prefer one coherent revision: title packaging, description, and opening answer aligned to the
  same intent. Do not simultaneously change the URL or primary topic without a separate reason.
- Update the visible modification date when the editorial change is material.
- After search-system data latency has passed, compare the same URL against its prior period and
  a recent baseline. Review impressions, clicks, CTR, position, query mix, landing engagement,
  retrieved pages, cited pages, and clicked pages separately.
- Roll back or revise only when repeated evidence supports the decision; do not react to a
  one-day fluctuation.
