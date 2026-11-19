# Claude Code instructions — GitHub Project Orchestrator

Read `README.md`, `.claude/skills/github-project-orchestrator/SKILL.md`, `scripts/github_project_sync.py` and `tests/test_sync.py` before changing this toolkit.

This repository distributes tooling. Do not create a GitHub Project for the toolkit itself unless the owner explicitly requests it. For a target repository, audit its current GitHub issues/Projects/milestones before preparing a tailored plan; never apply the generic example verbatim.

Maintain the read-only default, stable managed keys, deduplication, no secrets, no unapproved dates, no automatic merge or deployment. Run `python3 -m unittest discover -s tests -v`, validate the JSON example, and review the exact diff. Use only `main` as the long-lived branch. Do not create extra branches or PRs by default; when the owner explicitly requests PR review, use a temporary branch, review CI, merge only when authorized, then delete the temporary branch. The ChatGPT Skill's copy of `scripts/github_project_sync.py` must match the root implementation.