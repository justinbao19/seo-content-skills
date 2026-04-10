#!/usr/bin/env python3
"""Post-publish page QA check — three-layer architecture.

Layer 1: SEOmator CLI (251 rules / 20 categories)
Layer 2: Custom checks — llms.txt, hreflang self-reference, PageSpeed Insights CWV
Layer 3: Unified JSON + Markdown report with llm_review_required flag

SEOmator is a soft dependency: if not installed, falls back to basic checks
(title / H1 / meta / canonical) and prints an install prompt.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)
PSI_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


# ── HTML Parser ─────────────────────────────────────────────────────────────

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title: list[str] = []
        self.in_title = False
        self.h1: list[str] = []
        self.in_h1 = False
        self.meta_description: str | None = None
        self.canonical: str | None = None
        self.robots: str | None = None
        self.json_ld_count = 0
        self.links: list[str] = []
        self.hreflang_links: list[dict] = []  # [{href, hreflang}]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.meta_description = attrs.get("content")
            elif name == "robots":
                self.robots = attrs.get("content", "")
        elif tag == "link":
            rel = attrs.get("rel", "")
            if "canonical" in rel.split():
                self.canonical = attrs.get("href")
            if "alternate" in rel.split() and attrs.get("hreflang"):
                self.hreflang_links.append({
                    "href": attrs.get("href", ""),
                    "hreflang": attrs.get("hreflang", ""),
                })
        elif tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.json_ld_count += 1
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1.append(data)


# ── HTTP helpers ─────────────────────────────────────────────────────────────

def fetch(url: str, method: str = "GET", max_bytes: int = 400_000) -> tuple[int, str, str]:
    """Fetch URL, return (status, final_url, body). Never raises."""
    req = Request(url, headers={"User-Agent": USER_AGENT}, method=method)
    try:
        with urlopen(req, timeout=20) as resp:
            body = resp.read(max_bytes).decode("utf-8", errors="ignore") if method == "GET" else ""
            return resp.status, resp.geturl(), body
    except HTTPError as e:
        body = e.read(max_bytes).decode("utf-8", errors="ignore") if method == "GET" and hasattr(e, "read") else ""
        return e.code, url, body
    except (URLError, Exception):
        return 0, url, ""


def normalize_url(url: str, base: str) -> str:
    """Resolve relative URLs against base."""
    if url.startswith("http"):
        return url
    return urljoin(base, url)


# ── Layer 1: SEOmator ────────────────────────────────────────────────────────

def seomator_available() -> bool:
    return shutil.which("seomator") is not None


def run_seomator(url: str, categories: list[str] | None = None) -> dict:
    """Run seomator audit, return parsed summary dict.

    Uses --format llm (token-optimized XML) and --no-cwv (no browser required).
    Returns {"score": int, "grade": str, "fail_count": int, "warn_count": int,
             "top_fails": [str], "categories": {name: score}, "raw": str}
    or {"_error": str} on failure.
    """
    cmd = ["seomator", "audit", url, "--format", "llm", "--no-cwv"]
    if categories:
        cmd += ["-c", ",".join(categories)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        raw = result.stdout
    except subprocess.TimeoutExpired:
        return {"_error": "seomator timed out after 180s"}
    except Exception as e:
        return {"_error": str(e)}

    if result.returncode not in (0, 1):  # seomator exits 1 when issues found — that's normal
        err = result.stderr.strip() or result.stdout.strip() or "seomator exited with unexpected code"
        return {"_error": err}

    return _parse_seomator_llm(raw)


def _parse_seomator_llm(raw: str) -> dict:
    """Parse seomator --format llm XML output into a summary dict.

    The LLM format is a compact XML optimized for token efficiency.
    We extract score, grade, category scores, and top failures.
    """
    summary: dict = {"raw": raw, "score": None, "grade": None,
                     "fail_count": 0, "warn_count": 0,
                     "top_fails": [], "categories": {}}

    # Overall score: <score>82</score> or <overall-score>82</overall-score>
    m = re.search(r"<(?:overall-)?score>(\d+)</(?:overall-)?score>", raw)
    if m:
        summary["score"] = int(m.group(1))

    # Grade: <grade>B</grade>
    m = re.search(r"<grade>([A-F][+-]?)</grade>", raw, re.IGNORECASE)
    if m:
        summary["grade"] = m.group(1).upper()

    # Category scores: <category name="core" score="90">
    for cat_m in re.finditer(r'<category[^>]+name=["\']([^"\']+)["\'][^>]+score=["\'](\d+)["\']', raw):
        summary["categories"][cat_m.group(1)] = int(cat_m.group(2))
    # Also handle: <category name="core"><score>90</score>
    for cat_m in re.finditer(r'<category[^>]+name=["\']([^"\']+)["\'][^>]*>.*?<score>(\d+)</score>', raw, re.DOTALL):
        if cat_m.group(1) not in summary["categories"]:
            summary["categories"][cat_m.group(1)] = int(cat_m.group(2))

    # Fail items: <issue status="fail">...</issue>
    fail_items = re.findall(r'<issue[^>]+status=["\']fail["\'][^>]*>(.*?)</issue>', raw, re.DOTALL | re.IGNORECASE)
    summary["fail_count"] = len(fail_items)
    # Clean and keep top 10
    summary["top_fails"] = [re.sub(r"<[^>]+>", "", f).strip() for f in fail_items[:10]]

    # Warn items
    warn_items = re.findall(r'<issue[^>]+status=["\']warn["\'][^>]*>(.*?)</issue>', raw, re.DOTALL | re.IGNORECASE)
    summary["warn_count"] = len(warn_items)

    # Remove raw from summary to keep output clean (it's large)
    del summary["raw"]
    summary["_raw_available"] = True  # signal that raw was captured but omitted

    return summary


# ── Layer 2: Custom checks ───────────────────────────────────────────────────

def check_llms_txt(base_url: str) -> dict:
    """Check if /llms.txt exists and is accessible (HTTP 200).

    llms.txt tells AI crawlers what the site allows. Its absence is a signal
    that the site hasn't opted into the AI/GEO readiness pattern.
    """
    parsed = urlparse(base_url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"
    status, _, _ = fetch(llms_url, method="HEAD")
    return {
        "url": llms_url,
        "status": status,
        "exists": 200 <= status < 300,
    }


def check_hreflang(parser: PageParser, page_url: str) -> dict:
    """Validate hreflang self-reference.

    A page that declares hreflang alternates must include itself in that set.
    Missing self-reference is a common hreflang implementation error.
    Also checks for x-default presence when multiple alternates exist.
    """
    links = parser.hreflang_links
    if not links:
        return {"declared": False, "lang_count": 0, "self_ref": None, "x_default": None, "issues": []}

    parsed_page = urlparse(page_url)
    page_path = parsed_page.path.rstrip("/")

    has_self_ref = False
    has_x_default = False
    for link in links:
        href = normalize_url(link["href"], page_url)
        parsed_href = urlparse(href)
        if (parsed_href.netloc == parsed_page.netloc
                and parsed_href.path.rstrip("/") == page_path):
            has_self_ref = True
        if link.get("hreflang", "").lower() == "x-default":
            has_x_default = True

    issues = []
    if not has_self_ref:
        issues.append("hreflang set is missing self-reference for this URL")
    if len(links) > 1 and not has_x_default:
        issues.append("hreflang set has multiple alternates but no x-default")

    return {
        "declared": True,
        "lang_count": len(links),
        "self_ref": has_self_ref,
        "x_default": has_x_default,
        "issues": issues,
    }


def check_pagespeed(url: str, api_key: str) -> dict:
    """Fetch Core Web Vitals field data from PageSpeed Insights API.

    Returns LCP / CLS / INP / FCP / TTFB from CrUX field data (real-user metrics).
    Only runs if api_key is provided.
    """
    psi_url = f"{PSI_API}?url={url}&key={api_key}&strategy=mobile&category=performance"
    try:
        status, _, body = fetch(psi_url)
        if status != 200:
            return {"_error": f"PSI API returned HTTP {status}"}
        data = json.loads(body)
    except Exception as e:
        return {"_error": str(e)}

    metrics: dict = {}
    lhr = data.get("lighthouseResult", {})
    fld = data.get("loadingExperience", {}).get("metrics", {})

    # Field data from CrUX (preferred — real users)
    cwv_map = {
        "LARGEST_CONTENTFUL_PAINT_MS": "lcp_ms",
        "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls",
        "INTERACTION_TO_NEXT_PAINT": "inp_ms",
        "FIRST_CONTENTFUL_PAINT_MS": "fcp_ms",
        "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "ttfb_ms",
    }
    for api_key_name, out_key in cwv_map.items():
        entry = fld.get(api_key_name, {})
        p75 = entry.get("percentile")
        category = entry.get("category", "")
        if p75 is not None:
            metrics[out_key] = {"p75": p75, "category": category}

    # Lighthouse score as fallback signal
    perf_score = lhr.get("categories", {}).get("performance", {}).get("score")
    if perf_score is not None:
        metrics["lighthouse_performance"] = round(perf_score * 100)

    return metrics if metrics else {"_error": "no field data available (URL may lack CrUX data)"}


# ── Layer 3: Unified output ──────────────────────────────────────────────────

def build_basic_checks(parser: PageParser, url: str, status: int) -> tuple[dict, list[str]]:
    """Run basic HTML checks (used standalone or as seomator fallback)."""
    robots = parser.robots or ""
    basic = {
        "status": status,
        "title": " ".join(parser.title),
        "h1": " ".join(parser.h1),
        "meta_description": parser.meta_description,
        "canonical": parser.canonical,
        "robots": robots,
        "json_ld_count": parser.json_ld_count,
        "link_count": len(parser.links),
    }
    issues = []
    if status < 200 or status >= 400:
        issues.append(f"HTTP status {status}")
    if not basic["title"]:
        issues.append("missing <title>")
    if not basic["h1"]:
        issues.append("missing H1")
    if not basic["meta_description"]:
        issues.append("missing meta description")
    if not basic["canonical"]:
        issues.append("missing canonical")
    if "noindex" in robots.lower():
        issues.append("page has noindex — will not appear in search results")
    if "nofollow" in robots.lower():
        issues.append("page has nofollow — link equity will not pass")
    if basic["json_ld_count"] == 0:
        issues.append("missing JSON-LD structured data")
    if basic["link_count"] < 3:
        issues.append("unexpectedly low link count on published page")
    return basic, issues


def build_llm_review_items(seomator_result: dict, custom: dict, basic_issues: list[str]) -> list[str]:
    """Identify items that require LLM/editorial judgment after automated checks."""
    items = []

    # Seomator: score near grade boundaries (neither clearly good nor bad)
    score = seomator_result.get("score") if not seomator_result.get("_error") else None
    if score is not None and 65 <= score <= 75:
        items.append(
            f"SEOmator score {score} is in the borderline zone (65–75) — "
            "review top_fails to decide if this is publish-ready"
        )

    # hreflang: declared but with issues that need review
    hreflang = custom.get("hreflang", {})
    if hreflang.get("declared") and hreflang.get("issues"):
        for issue in hreflang["issues"]:
            items.append(f"hreflang issue needs verification: {issue}")

    # CWV: borderline metrics
    psi = custom.get("pagespeed", {})
    if not psi.get("_error"):
        lcp = psi.get("lcp_ms", {}).get("p75")
        if lcp and 2500 <= lcp <= 4000:
            items.append(f"LCP {lcp}ms is in the 'needs improvement' zone (2500–4000ms) — assess impact on ranking")
        cls = psi.get("cls", {}).get("p75")
        if cls and 0.1 <= cls <= 0.25:
            items.append(f"CLS {cls} is in the 'needs improvement' zone (0.1–0.25) — check layout shifts")

    return items


def render_markdown(report: dict) -> str:
    lines = []
    url = report["url"]
    lines.append(f"## Post-Publish QA — {url}")
    lines.append("")
    lines.append(f"- **URL:** {url}")
    lines.append(f"- **Final URL:** {report['final_url']}")
    lines.append(f"- **HTTP status:** {report['status']}")
    lines.append(f"- **Verdict:** **{report['verdict']}**")
    lines.append(f"- **LLM review required:** {'Yes' if report.get('llm_review_required') else 'No'}")
    lines.append("")

    # LLM review items
    if report.get("llm_review_items"):
        lines.append("### LLM Review Items")
        for item in report["llm_review_items"]:
            lines.append(f"- {item}")
        lines.append("")

    # Seomator
    seo = report.get("seomator", {})
    if seo.get("_error"):
        lines.append(f"### SEOmator: unavailable ({seo['_error']})")
        lines.append("Install: `npm install -g @seomator/seo-audit`")
    elif seo:
        score = seo.get("score", "?")
        grade = seo.get("grade", "?")
        lines.append(f"### SEOmator Audit — Score: {score}/100 (Grade {grade})")
        lines.append(f"- Failures: {seo.get('fail_count', 0)} | Warnings: {seo.get('warn_count', 0)}")
        cats = seo.get("categories", {})
        if cats:
            cat_str = " | ".join(f"{k}: {v}" for k, v in cats.items())
            lines.append(f"- Categories: {cat_str}")
        if seo.get("top_fails"):
            lines.append("- Top failures:")
            for f in seo["top_fails"]:
                lines.append(f"  - {f}")
    lines.append("")

    # Basic checks
    basic = report.get("basic_checks", {})
    if basic:
        lines.append("### Basic Checks")
        lines.append(f"- Title: {basic.get('title') or '(missing)'}")
        lines.append(f"- H1: {basic.get('h1') or '(missing)'}")
        lines.append(f"- Meta description: {'present' if basic.get('meta_description') else 'missing'}")
        lines.append(f"- Canonical: {basic.get('canonical') or '(missing)'}")
        lines.append(f"- Robots: {basic.get('robots') or '(none)'}")
        lines.append(f"- JSON-LD blocks: {basic.get('json_ld_count', 0)}")
        lines.append(f"- Link count: {basic.get('link_count', 0)}")
        lines.append("")

    # Custom checks
    custom = report.get("custom_checks", {})
    lines.append("### Custom Checks")

    llms = custom.get("llms_txt", {})
    if llms:
        status_str = "✓ exists" if llms.get("exists") else f"✗ missing (HTTP {llms.get('status', '?')})"
        lines.append(f"- llms.txt: {status_str} — {llms.get('url', '')}")

    hreflang = custom.get("hreflang", {})
    if hreflang.get("declared"):
        self_ref = "✓" if hreflang.get("self_ref") else "✗ missing"
        xdef = "✓" if hreflang.get("x_default") else "✗ missing"
        lines.append(f"- hreflang: {hreflang['lang_count']} alternates | self-ref: {self_ref} | x-default: {xdef}")
        for issue in hreflang.get("issues", []):
            lines.append(f"  - ⚠ {issue}")
    else:
        lines.append("- hreflang: not declared on this page")

    psi = custom.get("pagespeed", {})
    if psi.get("_error"):
        lines.append(f"- PageSpeed / CWV: skipped ({psi['_error']})")
    elif psi:
        lcp = psi.get("lcp_ms", {})
        cls = psi.get("cls", {})
        inp = psi.get("inp_ms", {})
        fcp = psi.get("fcp_ms", {})
        ttfb = psi.get("ttfb_ms", {})
        lines.append(f"- Core Web Vitals (mobile, p75 field data):")
        if lcp:
            lines.append(f"  - LCP: {lcp.get('p75')}ms [{lcp.get('category', '?')}]")
        if cls:
            lines.append(f"  - CLS: {cls.get('p75')} [{cls.get('category', '?')}]")
        if inp:
            lines.append(f"  - INP: {inp.get('p75')}ms [{inp.get('category', '?')}]")
        if fcp:
            lines.append(f"  - FCP: {fcp.get('p75')}ms [{fcp.get('category', '?')}]")
        if ttfb:
            lines.append(f"  - TTFB: {ttfb.get('p75')}ms [{ttfb.get('category', '?')}]")
        if psi.get("lighthouse_performance"):
            lines.append(f"  - Lighthouse performance: {psi['lighthouse_performance']}/100")
    else:
        lines.append("- PageSpeed / CWV: not checked (pass --psi-key to enable)")
    lines.append("")

    # Issues
    all_issues = report.get("issues", [])
    if all_issues:
        lines.append("### Issues")
        for item in all_issues:
            lines.append(f"- {item}")
    else:
        lines.append("### Issues\n- None")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Post-publish page QA check")
    ap.add_argument("url", help="Live page URL to audit")
    ap.add_argument("--json", action="store_true", help="Output JSON to stdout")
    ap.add_argument("--psi-key", help="PageSpeed Insights API key (enables CWV field data)")
    ap.add_argument("--no-seomator", action="store_true", help="Skip SEOmator, run custom checks only")
    ap.add_argument("--categories", help="Comma-separated SEOmator categories (default: all)")
    ap.add_argument("--config", help="Optional JSON config path")
    args = ap.parse_args()

    # Load config
    config: dict = {}
    if args.config:
        import pathlib
        config = json.loads(pathlib.Path(args.config).read_text(encoding="utf-8"))

    psi_key = args.psi_key or config.get("psiApiKey")
    skip_seomator = args.no_seomator or config.get("skipSeomator", False)
    categories = (
        [c.strip() for c in args.categories.split(",") if c.strip()]
        if args.categories
        else config.get("seomatorCategories") or None
    )

    # Fetch page HTML (needed for basic + custom checks)
    status, final_url, body = fetch(args.url)
    parser = PageParser()
    if body:
        parser.feed(body)

    # Basic checks (always run)
    basic, basic_issues = build_basic_checks(parser, args.url, status)

    # Layer 1: SEOmator
    seomator_result: dict = {}
    if not skip_seomator:
        if seomator_available():
            seomator_result = run_seomator(args.url, categories=categories)
        else:
            seomator_result = {
                "_error": "seomator not installed — run: npm install -g @seomator/seo-audit",
                "_fallback": "basic checks only",
            }
            print(
                "⚠  SEOmator not found. Running basic checks only.\n"
                "   Install: npm install -g @seomator/seo-audit",
                file=sys.stderr,
            )

    # Layer 2: Custom checks
    custom_checks: dict = {}
    custom_checks["llms_txt"] = check_llms_txt(args.url)
    custom_checks["hreflang"] = check_hreflang(parser, final_url)
    if psi_key:
        custom_checks["pagespeed"] = check_pagespeed(args.url, psi_key)

    # Collect all issues
    all_issues = list(basic_issues)
    hreflang_issues = custom_checks.get("hreflang", {}).get("issues", [])
    all_issues.extend(hreflang_issues)
    if not custom_checks.get("llms_txt", {}).get("exists"):
        all_issues.append("llms.txt not found — AI crawlers have no explicit access signal")
    if seomator_result and not seomator_result.get("_error"):
        for fail in seomator_result.get("top_fails", []):
            all_issues.append(f"seomator: {fail}")

    # Verdict
    has_critical = any(
        kw in issue.lower()
        for issue in all_issues
        for kw in ("noindex", "http status", "missing <title>", "missing h1")
    )
    seo_score = seomator_result.get("score") if not seomator_result.get("_error") else None
    if has_critical or (seo_score is not None and seo_score < 50):
        verdict = "FAIL"
    elif seo_score is not None and seo_score < 70:
        verdict = "WARN"
    else:
        verdict = "PASS"

    # LLM review items
    llm_review_items = build_llm_review_items(seomator_result, custom_checks, all_issues)

    report = {
        "url": args.url,
        "final_url": final_url,
        "status": status,
        "verdict": verdict,
        "llm_review_required": len(llm_review_items) > 0,
        "llm_review_items": llm_review_items,
        "seomator": seomator_result,
        "basic_checks": basic,
        "custom_checks": custom_checks,
        "issues": all_issues,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))


if __name__ == "__main__":
    main()
