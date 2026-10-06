"""Offline regression checks for independently installed SEO QA scripts."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "seo-geo-qa/scripts"
sys.path.insert(0, str(SCRIPTS))
import seo_qa_runner as runner
import verify_links as verifier


class PageHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(404 if self.path == "/missing" else 200)
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        if self.path != "/missing":
            self.wfile.write(b"<html><title>Reference</title><h1>Reference</h1></html>")

    def log_message(self, *_args):
        pass


@contextlib.contextmanager
def local_site():
    server = ThreadingHTTPServer(("127.0.0.1", 0), PageHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class SeoQaTests(unittest.TestCase):
    def run_runner(self, article, *args, cwd=None):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "seo_qa_runner.py"), str(article),
             "--skip-serp", *args], cwd=cwd, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_draft_without_urls_returns_json_and_review_items(self):
        with tempfile.TemporaryDirectory() as td:
            article = Path(td) / "article.md"
            article.write_text("# Model API guide\n\nA draft with no references.\n")
            result = self.run_runner(article, "--stdout-json")
            report = json.loads(result.stdout)
            self.assertEqual(report["link_report"]["total"], 0)
            self.assertTrue(report["llm_review_required"])
            self.assertTrue(report["warnings"]["citation_risks"])
            self.assertFalse((Path(td) / "qa-reports").exists())

    def test_default_and_explicit_reports_outside_repository(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            article = root / "article.md"
            article.write_text("# Model API guide\n\nDraft.\n")
            self.run_runner(article)
            report_dir = root / "qa-reports/article"
            self.assertEqual(len(list(report_dir.glob("*.json"))), 1)
            self.assertEqual(len(list(report_dir.glob("*.md"))), 1)
            for _ in range(2):
                self.run_runner(article, "--report-dir", str(root / "custom"))
            self.assertEqual(len(list((root / "custom").glob("*.json"))), 2)

    def test_config_report_directory_is_relative_to_invocation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            article = root / "article.md"
            article.write_text("# Model API guide\n\nDraft.\n")
            (root / "config.json").write_text(json.dumps({"reportDir": "reports"}))
            self.run_runner(article, "--config", "config.json", cwd=root)
            self.assertEqual(len(list((root / "reports/article").glob("*.json"))), 1)

    def test_host_boundaries_for_article_stats(self):
        text = "\n".join([
            "https://aihubmix.com/docs", "https://docs.aihubmix.com/guide",
            "https://notaihubmix.com/page", "https://aihubmix.com.example.org/page",
        ])
        stats = runner.extract_basic_article_stats(text, "https://AIHUBMIX.com/")
        self.assertEqual(stats["internal_links"], 2)
        self.assertEqual(stats["external_links"], 2)

    def test_similar_suffix_is_not_a_trusted_source(self):
        with patch.object(verifier, "search_index", return_value=(True, "test evidence")):
            self.assertEqual(verifier.classify_source_quality(
                "docs.openai.com", "reference " * 250, "https://docs.openai.com/x"
            )[1], "TIER-A")
            self.assertEqual(verifier.classify_source_quality(
                "notopenai.com", "reference " * 250, "https://notopenai.com/x"
            )[1], "TIER-C")

    def test_dead_link_fails_and_writer_mode_requests_revision(self):
        with local_site() as url, tempfile.TemporaryDirectory() as td:
            article = Path(td) / "article.md"
            article.write_text(f"# Guide\n\n[Reference]({url}/missing)\n")
            for mode, expected in [("qa", "FAIL"), ("writer", "REVISE")]:
                report = json.loads(self.run_runner(
                    article, "--site-domain", "127.0.0.1", "--mode", mode, "--stdout-json"
                ).stdout)
                self.assertEqual(report["verdict"], expected)
                self.assertTrue(report["critical_issues"]["citation_risks"])

    def test_live_internal_link_skips_source_search(self):
        with local_site() as url, tempfile.TemporaryDirectory() as td:
            article = Path(td) / "article.md"
            article.write_text(f"# Guide\n\n[Reference]({url}/reference)\n")
            report = json.loads(self.run_runner(
                article, "--site-domain", "127.0.0.1", "--stdout-json"
            ).stdout)
            self.assertEqual(report["link_report"]["verdict_counts"]["valid"], 1)
            self.assertEqual(report["article"]["internal_links"], 1)
            self.assertFalse(report["critical_issues"]["citation_risks"])


if __name__ == "__main__":
    unittest.main()
