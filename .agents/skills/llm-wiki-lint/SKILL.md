---
name: llm-wiki-lint
description: Run deterministic wiki, source-manifest, and public-audit checks before commits.
---

# LLM Wiki Lint

## Maintenance gate

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
.qmd/bin/lint-wiki
```

After ingestion that changes coverage:

```bash
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
```

## What lint enforces

- OKF: non-empty `type` on wiki concept documents; frontmatter present
- Producer: `title`, `description`, non-empty thematic `tags`
- `source_count` consistency with `## Sources` links
- Uncited `## Core claims` bullets
- Broken or ambiguous wikilinks
- Frontmatter-free `index.md` with `# Contents`
- Manifest: covered sources must have real wiki backlinks
- Public audit: no secrets / private keys / foreign machine home paths

## Log

```bash
python3 .tools/scripts/wiki_tool.py log --title "lint | Scope" --details "Result summary"
```

Or append manually: `## [YYYY-MM-DD] lint | Scope`
