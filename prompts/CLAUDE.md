# Reusable Claude Code prompt — provision and maintain a real GitHub Project

**How to use:** Run Claude Code with access to this toolkit and the target repository. Replace the placeholders. Its Skill is at .claude/skills/github-project-orchestrator/SKILL.md; for global reuse install or symlink that Skill under ~/.claude/skills/.

---

Act as a staff engineer, technical lead and GitHub Projects V2 setup operator.

**Project name:** [NAME OF THE PROJECT]  
**GitHub repository:** [GITHUB REPOSITORY URL]  
**Goal or MVP:** [PROJECT GOAL OR "DISCOVER AND PROPOSE"]  
**Approved plan:** [LINK OR PATH TO APPROVED PLAN OR "NOT YET APPROVED"]

The outcome is a **real, verified GitHub Projects V2 project and connected native objects** (not only Markdown files), built from the audited codebase and authorized plan.

## 1. Preflight and discovery

Read this toolkit's README.md, CLAUDE.md, AGENTS.md, .claude/skills/github-project-orchestrator/SKILL.md, scripts/github_project_sync.py, and examples/project-plan.example.json. For the target repository read code structure, docs, tests/CI, active PRs, issues, milestones, Projects V2 boards, labels, roadmaps and security/release rules.

Check GitHub CLI installation and access (gh auth status; project scope if necessary). Never print or commit tokens. Record default branch and observed revision. Read existing GitHub records before writing, including all issues needed for duplicate detection; stop on incomplete paginated inventory. Respect private-repo boundaries.

If the user has not approved an exact plan, **do not write remote objects yet**.

## 2. Prepare a real project plan

Use the actual repository evidence, not the fictional example contents. Create a local project-plan.json using this toolkit's schema:

- Project title: [NAME OF THE PROJECT] Delivery (or reuse its current appropriate board).
- Measurable milestone objectives and exit criteria.
- Stable unique keys for epics and child issues, with bounded outcomes, checklists, tests and release gates.
- Native parent/sub-issue and blocked-by relationships without cycles.
- P0–P3 priorities, labels, effort ranges; dates null until approved.
- Reuse existing work and preserve human-edited issue descriptions, priority and status.
- Explicit notes for board views and workflow automation that cannot be provisioned automatically.

If significant technical unknowns exist, create discovery/decision work first. Do not fabricate work, assignees, budget or due dates.

## 3. Validate, dry-run, then request approval

From the toolkit checkout run:

    python3 scripts/github_project_sync.py --plan project-plan.json --check-only
    python3 scripts/github_project_sync.py --plan project-plan.json

The second command must only inspect GitHub and print the proposed changes. Report the precise create/reuse/link counts, conflicts, gaps and permissions. **Stop here until the human owner approves this exact write plan.**

After approval, execute only authorized changes:

    python3 scripts/github_project_sync.py --plan project-plan.json --apply --confirm OWNER/REPOSITORY

Replace OWNER/REPOSITORY with the actual owner/repository from [GITHUB REPOSITORY URL]. The script's --with-views option is best-effort only for new projects. Do not claim views or automated workflows are enabled unless verified.

## 4. Verify everything on GitHub

Read back and report GitHub URLs for the board, milestones, epic parent issues, child issues, native dependency links, priority/date fields, and any actual views or active workflows. Rerun a read-only preview and check that another apply would not duplicate objects. Report unsupported CLI/API operations, manual UI steps, partial failures, and any differences from the approved plan.

Do not merge PRs, auto-close issues, deploy, change repository permissions, assign people, publish or commit confidential content without approval. If changing toolkit code, use a feature branch and draft PR with tests and evidence.

**Required final report:** Audit evidence · Approved writes · Created/reused/unchanged objects (URLs) · Verified relationships/fields · Tests and CI result · Remaining manual steps · Next issues for developers.
