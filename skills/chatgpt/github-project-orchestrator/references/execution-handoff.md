# ChatGPT -> Claude Code handoff

Delegate when the connector cannot create GitHub Projects V2, a local GitHub CLI has the right permissions, or technical repo analysis is needed. Send:

```text
Goal: Configure native GitHub project management for <OWNER/REPO>.
Current state: <audited GitHub URLs and observed date>
Approved scope: <exact project name, milestones, epics, child issues, fields, relationships and views>
Input plan: <absolute or repo-relative path to validated plan.json>

Read all existing management and repo instructions first.
Run the orchestrator --check-only and dry-run. Reconcile and preserve existing GitHub objects.
After approval, run --apply --confirm OWNER/REPO. Do not create duplicate board/issue/epic.
Verify each created/reused Project, milestone, parent link, blocked-by edge, priority and date with GitHub CLI.
Output evidence-backed ledger: Created | Reused | Skipped | Failed, with direct URLs.
Do not merge PRs, deploy releases, publish claims, spend money or expose secrets.
Never claim a workflow is active until verified in GitHub.
```

Separate repository engineering implementation: Claude Code picks an approved task issue, writes code/tests in a branch, opens a draft PR and links the issue. ChatGPT reviews status/dependencies and updates plans, not code. Either model can perform low-risk actions when authorized and tools permit, but maintain distinct audit logs.