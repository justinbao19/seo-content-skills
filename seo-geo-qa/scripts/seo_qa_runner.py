#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from verify_links import normalize_domain

def _find_skill_root() -> Path:
    """Walk up from this script to find the directory containing SKILL.md."""
    d = Path(__file__).resolve().parent
    for _ in range(5):
        if (d / "SKILL.md").exists():
            return d
        d = d.parent
    return Path(__file__).resolve().parent.parent  # fallback


SKILL_ROOT = _find_skill_root()
ROOT = Path.cwd().resolve()
VERIFY = SKILL_ROOT / "scripts/verify_links.py"
SERP = SKILL_ROOT / "scripts/serp_gap_analyzer.py"
DEFAULT_REPORT_DIRNAME = "qa-reports"
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))")
FRONTMATTER_RE = re.compile(r"\A\s*---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "report"


def run_json(cmd: list[str], allow_failure: bool = False) -> dict | None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        if allow_failure:
            return {"_error": proc.stderr.strip() or proc.stdout.strip() or f"command failed: {' '.join(cmd)}"}
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"command failed: {' '.join(cmd)}")
    return json.loads(proc.stdout)


def run_text(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"command failed: {' '.join(cmd)}")
    return proc.stdout


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extract_cover_image(text: str) -> str | None:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return None
    try:
        frontmatter = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    cover = frontmatter.get("coverImage") if isinstance(frontmatter, dict) else None
    return cover.strip() if isinstance(cover, str) and cover.strip() else None


def is_webp_image(ref: str) -> bool:
    if ref.lower().startswith("data:image/webp"):
        return True
    return urlparse(ref).path.lower().endswith(".webp")


def _local_image_issue(ref: str, article_path: Path | None, public_root: Path | None) -> str | None:
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc or parsed.path.startswith("data:"):
        return None
    if article_path is None:
        return None
    if parsed.path.startswith("/"):
        if public_root is None:
            return f"{ref} (public root required to verify asset)"
        candidate = public_root / parsed.path.lstrip("/")
    else:
        candidate = article_path.parent / parsed.path
    if not candidate.is_file():
        return ref
    if is_webp_image(ref):
        try:
            with candidate.open("rb") as asset:
                header = asset.read(12)
            if header[:4] != b"RIFF" or header[8:12] != b"WEBP":
                return f"{ref} (invalid WebP bytes)"
        except OSError:
            return f"{ref} (unreadable WebP asset)"
    return None


def extract_image_stats(text: str, article_path: Path | None = None, public_root: Path | None = None) -> dict:
    matches = MARKDOWN_IMAGE_RE.findall(text)
    markdown_refs = [first or second for first, second in matches]
    cover_image = extract_cover_image(text)
    refs = []
    for ref in [*markdown_refs, cover_image]:
        if ref and ref not in refs:
            refs.append(ref)
    non_webp = [ref for ref in refs if not is_webp_image(ref)]
    missing_local = []
    for ref in refs:
        issue = _local_image_issue(ref, article_path, public_root)
        if issue:
            missing_local.append(issue)
    return {
        "image_count": len(refs),
        "webp_image_count": len(refs) - len(non_webp),
        "image_references": refs,
        "cover_image": cover_image,
        "non_webp_images": non_webp,
        "missing_local_images": missing_local,
    }



def extract_basic_article_stats(text: str, site_domain: str | None = None, article_path: Path | None = None, public_root: Path | None = None) -> dict:
    site_domain = normalize_domain("//" + site_domain.strip().removeprefix("https://").removeprefix("http://")) if site_domain else None
    lines = text.splitlines()
    h1 = ""
    h2s = 0
    h3s = 0
    faq_count = 0
    external_links = 0
    internal_links = 0

    for line in lines:
        s = line.strip()
        if s.startswith("# ") and not h1:
            h1 = s[2:].strip()
        elif s.startswith("## "):
            h2s += 1
            if s.lstrip("# ").strip().endswith(("?", "？")):
                faq_count += 1
        elif s.startswith("### "):
            h3s += 1
            if s.lstrip("# ").strip().endswith(("?", "？")):
                faq_count += 1
        elif s.startswith("#") and s.endswith(("?", "？")):
            # H4+ headings with questions also count
            faq_count += 1
        elif re.match(r"^\*{1,2}Q[\s:]", s):
            # Bold Q&A format: **Q: ...** or **Q ...** or *Q:*
            faq_count += 1

    urls = re.findall(r"https?://[^\s)\]>\"']+", text)
    for url in urls:
        domain = normalize_domain(url)
        if site_domain and (domain == site_domain or domain.endswith("." + site_domain)):
            internal_links += 1
        else:
            external_links += 1

    internal_links += len(re.findall(r"(?<!!)\[[^\]]+\]\((/[^)\s]+)\)", text))
    words = len(text.split())
    stats = {
        "h1": h1,
        "word_count": words,
        "h2_count": h2s,
        "h3_count": h3s,
        "faq_count": faq_count,
        "external_links": external_links,
        "internal_links": internal_links,
    }
    stats.update(extract_image_stats(text, article_path=article_path, public_root=public_root))
    return stats


def build_llm_review_items(article: dict, link_report: dict, serp_report: dict | None) -> list[str]:
    """Identify items that require LLM semantic judgment.

    Scripts handle deterministic checks. This list flags ambiguous cases where
    a human or LLM must apply editorial judgment. Do not auto-pass or auto-fail
    on these items — they require contextual reasoning.
    """
    items: list[str] = []

    # 1. Borderline TIER-D sources (source_quality == "weak", not "reject")
    #    "reject" is clear-cut; "weak" needs editorial judgment on context.
    for link in link_report.get("weak_sources", []):
        if link.get("source_quality") == "weak":
            items.append(f"TIER-D borderline source — editorial judgment needed: {link['url']}")

    # 2. Keyword intent alignment — scripts cannot evaluate semantic relevance.
    h1 = article.get("h1", "")
    if h1:
        items.append(f"Verify H1 semantic intent matches target keyword: \"{h1}\"")

    # 3. Word count near threshold (1800–2200 is the boundary zone around the
    #    2000-word floor for most comparison/guide content).
    wc = article.get("word_count", 0)
    if 1800 < wc < 2200:
        items.append(
            f"Word count {wc} is in the boundary zone (1800–2200) — "
            "verify whether content depth is sufficient for this article type"
        )

    # 4. SERP overlap near the 45% fail threshold.
    if serp_report and not serp_report.get("_error"):
        overlap = serp_report.get("summary", {}).get("article_term_overlap_percent", 100)
        if 40 <= overlap <= 55:
            items.append(
                f"SERP keyword overlap {overlap}% is near the 45% threshold — "
                "verify whether missing terms are genuinely relevant or just noise"
            )

    return items


def determine_verdict(link_report: dict, serp_report: dict | None, article_stats: dict, config: dict) -> tuple[str, dict, dict]:
    critical = {"seo_risks": [], "citation_risks": []}
    warnings = {"seo_risks": [], "citation_risks": []}

    dead = link_report.get("verdict_counts", {}).get("dead", 0)
    moved = link_report.get("verdict_counts", {}).get("moved", 0)
    weak_sources = len(link_report.get("weak_sources", []))
    if dead:
        critical["citation_risks"].append(f"{dead} dead external link(s)")
    if moved:
        warnings["citation_risks"].append(f"{moved} moved link(s) need manual review")
    if weak_sources:
        warnings["citation_risks"].append(f"{weak_sources} weak source(s) should be replaced if stronger evidence exists")

    if config.get("imageFormat") == "webp":
        if article_stats.get("non_webp_images"):
            critical["seo_risks"].append("Required WebP image format: non-WebP references found")
        if article_stats.get("missing_local_images"):
            critical["seo_risks"].append("Required image assets missing, invalid, or unverified")

    min_faq_count = int(config.get("minFaqCount", 2))
    min_external_links = int(config.get("minExternalLinks", 5))
    max_tier_d = int(config.get("maxTierD", 1))
    if article_stats["faq_count"] < min_faq_count:
        warnings["seo_risks"].append(f"FAQ count below {min_faq_count}")
    if article_stats["external_links"] < min_external_links:
        warnings["citation_risks"].append(f"External link count looks thin for an SEO article (< {min_external_links})")
    tier_d = link_report.get("source_tier_counts", {}).get("TIER-D", 0)
    if tier_d > max_tier_d:
        critical["citation_risks"].append(f"Too many TIER-D sources ({tier_d} > {max_tier_d})")

    if serp_report and not serp_report.get("_error"):
        summary = serp_report.get("summary", {})
        overlap = summary.get("article_term_overlap_percent", 100)
        delta = summary.get("article_vs_avg_word_count_delta", 0)
        missing_h2s = summary.get("missing_common_h2s", [])
        if overlap < 45:
            critical["seo_risks"].append(f"SERP topic overlap too low ({overlap}%)")
        if delta < -400:
            warnings["seo_risks"].append(f"Article is materially thinner than SERP average ({delta} words delta)")
        if len(missing_h2s) >= 3:
            warnings["seo_risks"].append(f"Missing {len(missing_h2s)} common SERP sections")
    elif serp_report and serp_report.get("_error"):
        warnings["seo_risks"].append(f"SERP analyzer unavailable: {serp_report['_error']}")

    verdict = "FAIL" if (critical['seo_risks'] or critical['citation_risks']) else "PASS"
    return verdict, critical, warnings


def render_markdown(report: dict) -> str:
    lines = []
    lines.append(f"# SEO QA Report — {report['article']['slug']}")
    lines.append("")
    lines.append(f"- **Generated:** {report['generated_at']}")
    lines.append(f"- **Article:** `{report['article']['path']}`")
    if report.get("keyword"):
        lines.append(f"- **Keyword:** {report['keyword']}")
    lines.append(f"- **Verdict:** **{report['verdict']}**")
    lines.append(f"- **LLM review required:** {'Yes' if report.get('llm_review_required') else 'No'}")
    lines.append("")

    if report.get("llm_review_items"):
        lines.append("## LLM Review Items")
        lines.append("These items require editorial / semantic judgment — scripts cannot decide them automatically:")
        for item in report["llm_review_items"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Snapshot")
    snap = report["article"]
    lines.append(f"- H1: {snap['h1'] or '(missing)'}")
    lines.append(f"- Word count: {snap['word_count']}")
    lines.append(f"- H2/H3: {snap['h2_count']}/{snap['h3_count']}")
    lines.append(f"- FAQ count: {snap['faq_count']}")
    lines.append(f"- Internal links: {snap['internal_links']}")
    lines.append(f"- External links: {snap['external_links']}")
    lines.append(f"- Image references: {snap.get('image_count', 0)}; non-WebP: {len(snap.get('non_webp_images', []))}")
    lines.append("")

    lines.append("## Critical Issues")
    lines.append("### SEO Risks")
    if report["critical_issues"].get("seo_risks"):
        for item in report["critical_issues"]["seo_risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Citation Risks")
    if report["critical_issues"].get("citation_risks"):
        for item in report["critical_issues"]["citation_risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Warnings")
    lines.append("### SEO Risks")
    if report["warnings"].get("seo_risks"):
        for item in report["warnings"]["seo_risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Citation Risks")
    if report["warnings"].get("citation_risks"):
        for item in report["warnings"]["citation_risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Link Verification Summary")
    vc = report["link_report"].get("verdict_counts", {})
    tc = report["link_report"].get("source_tier_counts", {})
    lines.append(f"- Valid: {vc.get('valid',0)}")
    lines.append(f"- Bot-protected: {vc.get('bot-protected',0)}")
    lines.append(f"- Dead: {vc.get('dead',0)}")
    lines.append(f"- Moved: {vc.get('moved',0)}")
    lines.append(f"- Weak: {vc.get('weak',0)}")
    lines.append(f"- Source tiers: TIER-A {tc.get('TIER-A',0)} | TIER-B {tc.get('TIER-B',0)} | TIER-C {tc.get('TIER-C',0)} | TIER-D {tc.get('TIER-D',0)} | skip {tc.get('skip',0)}")
    if report["link_report"].get("dead"):
        lines.append("")
        lines.append("### Dead Links")
        for item in report["link_report"]["dead"]:
            lines.append(f"- {item['url']} — {item['evidence']}")
    if report["link_report"].get("weak_sources"):
        lines.append("")
        lines.append("### Weak Sources")
        for item in report["link_report"]["weak_sources"]:
            notes = "; ".join(item.get("source_notes") or [])
            lines.append(f"- {item['url']} — {item['source_tier']} / {item['source_quality']} — {notes}")
    lines.append("")

    if report.get("serp_report") and not report["serp_report"].get("_error"):
        summary = report["serp_report"].get("summary", {})
        lines.append("## SERP Gap Summary")
        lines.append(f"- Avg competitor word count: {summary.get('avg_competitor_word_count','?')}")
        lines.append(f"- Article vs avg delta: {summary.get('article_vs_avg_word_count_delta','?')}")
        lines.append(f"- Topic overlap: {summary.get('article_term_overlap_percent','?')}%")
        missing_h2s = summary.get("missing_common_h2s", [])
        if missing_h2s:
            lines.append("- Missing common sections:")
            for item in missing_h2s[:10]:
                lines.append(f"  - {item}")
        missing_terms = summary.get("missing_common_terms", [])
        if missing_terms:
            lines.append("- Missing recurring concepts:")
            for item in missing_terms[:12]:
                lines.append(f"  - {item}")
        lines.append("")
    elif report.get("serp_report") and report["serp_report"].get("_error"):
        lines.append("## SERP Gap Summary")
        lines.append(f"- Skipped / unavailable: {report['serp_report']['_error']}")
        lines.append("")

    lines.append("## Next Actions")
    if report["verdict"] == "PASS":
        lines.append("- Ready for AI final review / publication check.")
    else:
        lines.append("- Fix critical issues before PASS.")
    lines.append("- Keep this report with the draft for traceability.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified SEO QA runner")
    ap.add_argument("article", help="Markdown article path")
    ap.add_argument("--keyword", help="Primary keyword for SERP gap analysis")
    ap.add_argument("--mode", choices=["qa", "writer"], default="qa")
    ap.add_argument("--report-dir", help="Override report output directory")
    ap.add_argument("--config", help="Optional JSON config path")
    ap.add_argument("--site-domain", help="Primary site domain for internal link detection")
    ap.add_argument("--skip-serp", action="store_true")
    ap.add_argument("--require-webp", action="store_true", help="Enforce the project WebP image policy")
    ap.add_argument("--public-root", help="Filesystem root for site-relative image URLs")
    ap.add_argument("--no-jina", action="store_true", help="Use direct HTTP only for SERP analysis")
    ap.add_argument("--serp-limit", type=int, default=5)
    ap.add_argument("--stdout-json", action="store_true")
    args = ap.parse_args()

    config = load_config(args.config)
    site_domain = args.site_domain or config.get("siteDomain")
    article_path = Path(args.article).resolve()
    text = article_path.read_text(encoding="utf-8")
    if args.require_webp:
        config["imageFormat"] = "webp"
    public_root_value = args.public_root or config.get("publicRoot")
    public_root = Path(public_root_value).expanduser().resolve() if public_root_value else None
    article_stats = extract_basic_article_stats(text, site_domain=site_domain, article_path=article_path, public_root=public_root)
    slug = article_path.stem

    verify_cmd = [sys.executable, str(VERIFY), str(article_path), "--json"]
    if args.config:
        verify_cmd.extend(["--config", args.config])
    if site_domain:
        verify_cmd.extend(["--site-domain", site_domain])
    link_report = run_json(verify_cmd)
    serp_report = None
    if args.keyword and not args.skip_serp:
        serp_report = run_json([
            sys.executable, str(SERP), args.keyword, str(article_path),
            "--limit", str(args.serp_limit), "--json"
        ] + (["--no-jina"] if args.no_jina else []), allow_failure=True)

    verdict, critical, warnings = determine_verdict(link_report, serp_report, article_stats, config)
    has_critical = bool(critical.get('seo_risks') or critical.get('citation_risks'))
    if args.mode == "writer" and verdict == "FAIL" and has_critical:
        verdict = "REVISE"

    llm_review_items = build_llm_review_items(article_stats, link_report, serp_report)

    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": args.mode,
        "keyword": args.keyword,
        "verdict": verdict,
        "llm_review_required": len(llm_review_items) > 0,
        "llm_review_items": llm_review_items,
        "critical_issues": critical,
        "warnings": warnings,
        "article": {
            "path": str(article_path.relative_to(ROOT)) if article_path.is_relative_to(ROOT) else str(article_path),
            "slug": slug,
            **article_stats,
        },
        "link_report": link_report,
        "serp_report": serp_report,
    }

    image_gate_failed = config.get("imageFormat") == "webp" and bool(article_stats.get("non_webp_images") or article_stats.get("missing_local_images"))

    if args.stdout_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if image_gate_failed else 0

    default_report_root = article_path.parent / DEFAULT_REPORT_DIRNAME
    config_report_dir = config.get("reportDir")
    report_dir = (
        Path(args.report_dir).resolve() if args.report_dir else
        (ROOT / config_report_dir / slugify(slug)).resolve() if config_report_dir else
        (default_report_root / slugify(slug)).resolve()
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    json_path = report_dir / f"qa-{ts}.json"
    md_path = report_dir / f"qa-{ts}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Verdict: {verdict}")
    return 1 if image_gate_failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
