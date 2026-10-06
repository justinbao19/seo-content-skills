"""Merged SEO image/CJK/post-publish regression contracts; offline fixtures only."""
import contextlib,io,json
from pathlib import Path
import subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "seo-geo-qa/scripts"
sys.path.insert(0,str(SCRIPTS))
import seo_qa_runner as qa
import post_publish_check as published
class SeoMergeTests(unittest.TestCase):
    def cli(self,*args):
        return subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,timeout=30)
    def test_chinese_faq_and_relative_internal_links(self):
        stats = qa.extract_basic_article_stats('# 标题\n## 如何开始？\n### Can I export?\n[Docs](/docs)\n![Image](/image.png)')
        self.assertEqual(stats['faq_count'], 2)
        self.assertEqual(stats['internal_links'], 1)

    def test_image_gate_is_explicit_and_validates_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); article = root / 'a.md'
            article.write_text('# Guide\n![Example](fake.webp)')
            (root / 'fake.webp').write_bytes(b'not webp')
            base = [ROOT / 'seo-geo-qa/scripts/seo_qa_runner.py', article, '--skip-serp', '--stdout-json']
            ordinary = self.cli(*base)
            self.assertEqual(ordinary.returncode, 0, ordinary.stderr)
            self.assertTrue(json.loads(ordinary.stdout)['article']['missing_local_images'])
            gated = self.cli(*base, '--require-webp')
            self.assertEqual(gated.returncode, 1, gated.stderr)
            self.assertEqual(json.loads(gated.stdout)['verdict'], 'FAIL')
            (root / 'fake.webp').write_bytes(b'RIFF\x00\x00\x00\x00WEBP')
            # This checks the documented signature contract, not full decoding.
            self.assertEqual(self.cli(*base, '--require-webp').returncode, 0)

    def test_cover_dedup_and_public_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / 'cover.webp').write_bytes(b'RIFF\x00\x00\x00\x00WEBP')
            text = '---\n{"coverImage":"/cover.webp"}\n---\n![Cover](/cover.webp)'
            stats = qa.extract_image_stats(text, root / 'a.md')
            self.assertEqual(stats['image_count'], 1)
            self.assertTrue(stats['missing_local_images'])
            self.assertFalse(qa.extract_image_stats(text, root / 'a.md', root)['missing_local_images'])

    def test_postpublish_parser_retains_metadata_and_article_scope(self):
        page = published.PageParser()
        page.feed('<title>Guide</title><meta name="description" content="Description">'
                  '<link rel="canonical" href="https://example.org/guide">'
                  '<link rel="alternate" hreflang="en" href="https://example.org/guide">'
                  '<script type="application/ld+json">{}</script><h1>Guide</h1>'
                  '<img src="logo.png"><article><img src="body.webp"></article><img src="tail.png">')
        self.assertEqual(page.images, ['body.webp'])
        self.assertEqual(page.json_ld_count, 1)
        self.assertEqual(page.meta_description, 'Description')
        self.assertEqual(page.hreflang_links[0]['hreflang'], 'en')
        self.assertTrue(callable(published.check_pagespeed))
        self.assertTrue(callable(published.run_seomator))

    def test_postpublish_cli_enforces_optional_image_policy(self):
        body = '<title>Guide</title><h1>Guide</h1><article><img src="body.png"></article>'
        argv = ['post_publish_check.py', 'https://example.org/guide', '--json', '--no-seomator']
        for enforced in [False, True]:
            output = io.StringIO()
            with patch.object(sys, 'argv', argv + (['--require-webp'] if enforced else [])), patch.object(published, 'fetch', return_value=(200, 'https://example.org/guide', body)), patch.object(published, 'check_llms_txt', return_value={'exists': True}), patch.object(published, 'check_hreflang', return_value={'issues': []}), contextlib.redirect_stdout(output):
                published.main()
            report = json.loads(output.getvalue())
            self.assertEqual(report['verdict'], 'FAIL' if enforced else 'PASS')
            self.assertEqual(report['basic_checks']['image_count'], 1)


if __name__ == '__main__': unittest.main()
