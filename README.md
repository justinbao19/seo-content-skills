# SEO Content Skills

Public compatibility distribution of four independently installable content skills. Personal maintenance now lives in [agent-skills](https://github.com/justinbao19/agent-skills) (private); this repository preserves its original public paths and installation commands.

| Skill | Use |
| --- | --- |
| seo-blog-writer | Research, natural bilingual article writing and revision |
| seo-geo-qa | Draft diagnostics and live-page technical checks |
| content-qa | Evidence, reader value, language and destination review |
| content-production | Coordinate a requested full content workflow |

Install an entire selected skill directory, including references and scripts, into the host's skill location. Existing local edits must be checked and backed up before replacement. Each skill works to its requested scope; a small edit does not trigger the full workflow.

```bash
git clone https://github.com/justinbao19/seo-content-skills.git
cd seo-content-skills
python3 seo-geo-qa/scripts/seo_qa_runner.py /path/to/article.md --skip-serp --stdout-json
python3 seo-geo-qa/scripts/post_publish_check.py https://example.com/blog/post --no-seomator --json
python3 -m unittest discover -s tests -v
```

SEO QA requires Python 3.10+ and curl. Network checks, optional Jina, SEOmator and PageSpeed have documented dependencies and coverage limits. WebP is a project-specific policy enabled with `--require-webp` or config `imageFormat: "webp"`; use `--public-root` for site-relative assets. Inspect verdict, issues and editorial review flags: exit 0 does not establish a passing article. Link liveness and internal scores do not prove claim support or ranking outcomes.

Writing and QA do not authorize publication. Read each SKILL.md for actual commands and scope. Source versions and adaptation are in [SOURCES.md](SOURCES.md); active maintenance and compatibility updates follow [AGENTS.md](AGENTS.md), [sync-map.json](sync-map.json) and [docs/sync.md](docs/sync.md). No background sync trigger is installed. Earlier independent repositories remain archived.

The earlier README described the original SEO material as MIT, but its imported snapshot did not contain a complete LICENSE file. This migration adds no blanket license or expanded rights to mixed-source resources.
