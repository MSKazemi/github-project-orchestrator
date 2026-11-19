# Reusable follow-up prompt — weekly GitHub Project maintenance

**Project name:** [NAME OF THE PROJECT]  
**GitHub repository:** [GITHUB REPOSITORY URL]  
**Review period:** [START DATE] to [END DATE] (Europe/Rome)

Use the GitHub Project Orchestrator Skill to perform a **read-only** weekly review of the live GitHub Project, its milestones, epic/sub-issue graph, blocking dependencies, open PRs, CI, releases and outstanding decisions.

Reconcile changes since the previous review. Identify work completed with evidence, newly blocked or stale issues, PRs awaiting review, approved dates at risk, duplicated or orphaned work, and release-readiness gaps. Separate observed facts from assumptions. Preserve existing statuses and human edits.

Return:
- Progress toward the next milestone and evidence links.
- The **top three actionable priorities** for the next week.
- Blockers, dependencies and decisions that need human input.
- Precise GitHub issues suitable for Claude Code or other contributors.
- A deduplicated, read-only proposed issue/field update plan.
- Automation health: scheduled checks that actually ran, failed, or are merely proposed.

Do not mutate GitHub until I approve a scoped change set. Do not close issues solely because a draft exists. Do not invent dates, assignees, release readiness or workflow execution.
