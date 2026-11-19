# Claude Code prompt: execute GitHub project setup

Act as a staff engineering manager and GitHub Projects V2 administrator for <OWNER/REPO>.

Goal: create or improve the real native GitHub Project with correct relationships and actionable tasks. Do not stop after producing Markdown docs.

Read README, roadmap, current issues/PRs, tests, CI, release rules and repository-specific instructions. Discover existing Project, milestones, epics, labels and dates first; reuse instead of duplicating.

Create a valid project-plan.json describing measurable milestones, parent epic issues, concrete child issues, P0-P3 priorities, blocked-by links, acceptance criteria, evidence/tests and proposed scheduling. Compare it to live GitHub. Execute --check-only and then a read-only dry-run with scripts/github_project_sync.py. Explain planned changes. If I approve the specific changes, run --apply --confirm <OWNER/REPO>; verify issue relationships, board and fields with gh. Return all resulting GitHub URLs.

Do not overwrite human status, reassign people, create duplicate issues, alter protected branches, merge PRs, deploy, or expose credentials. Project workflow automation is not enabled merely because a YAML or script was created; validate it separately.