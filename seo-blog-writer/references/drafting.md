# Drafting the article

Use the [brief](research-brief.md) as a working hypothesis. Write a complete draft, then edit its logic and voice as a whole. The article should help a specific reader understand, choose, or act.

## Build the piece

- **Title and lead:** Name the subject in language the reader uses. Open with the answer, practical tension, specific observation, or decision that best suits the genre. Make a credible promise. Do not insert a keyword into the first sentence by force or use an intent template.
- **Body:** Give each section a job. Explain criteria before recommendations; show the basis for comparisons; make steps executable; place caveats beside claims. Use tables, examples, lists, and definitions when they make a point easier to grasp. Do not add them because an imagined AI platform prefers them.
- **Evidence:** Attribute consequential product facts, prices, statistics, research results, and quotations to the source that actually supports them. Verify dates, conditions, currency, sample, and context. Distinguish official claims, observed behavior, and the writer's judgment. Omit an unsupported number rather than dressing it up as a vague “industry survey.” Never invent testing or a quote.
- **Links:** Link to the specific official page, primary research, or credible report that supports a claim. Link internally when the destination answers a natural next question. Descriptive anchors help readers. Do not add a link simply to meet a count, or cite a generic homepage for a precise claim.
- **Ending:** Resolve the decision or next action raised at the start. A CTA belongs only if it follows naturally and the destination is real. Do not append a generic summary, “Last updated,” or FAQ unless it serves the reader or the destination requires it.

Write enough to answer the question with the needed evidence, and stop. There is no target length derived from competitor averages. Use the article's actual date and author only when known and required.

## Language pass while drafting

For English, use the voice decision in [voice editing](voice-editing.md): specific nouns and verbs, examples that carry information, natural variation in pace, and a register suited to the publication. Avoid repeating one section pattern across the entire article.

For Chinese, draft from the reader's task and source facts. If an English source draft exists, outline its claims and conditions first, then compose Chinese paragraphs independently. Recheck every price, qualifier, comparison, and link against the source. Rewrite title, subheads, captions, and CTA for the target locale. The aim is accurate, idiomatic Chinese rather than aligned sentence pairs.

After the full draft, do a whole-piece edit for progression, repetition, tone, and transitions. Re-read joins after rewriting. Then use [quality checks](quality-checks.md).

## Blog image format gate — when the destination requires WebP

When the destination requires WebP, every image appearing in a blog article, including the cover/frontmatter image, generated artwork, official screenshot, chart, and diagram, must be converted to **genuine WebP** before finalizing Markdown. Do not leave PNG, JPEG, GIF, AVIF, or SVG references in that blog file.

For each image:
1. Obtain it legally. Keep the source URL and license/permission note for third-party visuals; write descriptive alt text or a caption.
2. Convert the local asset to WebP (for example with `cwebp`, ImageMagick, or `sips`) at a quality where labels remain legible. Keep enough pixels for the intended display; use a 16:9 cover when the page template requires one.
3. Store and reference the `.webp` output in the body and `coverImage`. Remove stale non-WebP references.
4. Verify MIME/magic bytes and dimensions, not just the extension. Check that each referenced URL resolves after the site build.

At final image QA for a WebP destination, enumerate every Markdown image reference and `coverImage`; report total and WebP count. Fail the gate if any reference is non-WebP or any local WebP asset is missing. Re-run after changes to assets, references, or cover metadata. For other destinations, validate their actual image format contract.
