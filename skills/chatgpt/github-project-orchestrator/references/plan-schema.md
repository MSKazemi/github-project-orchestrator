# Native GitHub project plan schema v1

Reference file: `../assets/project-plan.example.json`.

- `schema_version`: integer `1`.
- `repository`: exact `OWNER/REPO` (the target repository, not the Skill repository).
- `project`: `owner`, unique `title`, optional `description`, optional `visibility` (PRIVATE/PUBLIC). The project owner may be a user or organization; credentials must have permission.
- `milestones`: array of `{key, title, description, due_on}`. Each stable `key` is unique. `due_on` is optional ISO YYYY-MM-DD **only when approved**; otherwise null. These are repo-level milestones, not release tags.
- `issues`: array of `{key, kind, title, body, priority, milestone, parent, blocked_by, start_date, target_date}`.
  - `kind`: `epic` or `task`; `priority` P0/P1/P2/P3.
  - `milestone`: milestone key defined above, or omitted/null.
  - `parent`: issue key, or omitted/null. For an issue reused by exact title, the parent edge is **not** created (the dry run prints `SKIP set parent …`); add it separately with `gh issue edit PARENT --add-sub-issue N` after approval. Native GitHub sub-issue edge is created for new issues, and missing parent edges on explicitly managed issues may be repaired; conflicting human-set parent edges are preserved for review.
  - `blocked_by`: list of issue keys in the same plan; script creates native `blocked by` edges for new issues and fills missing edges on previously managed issues.
  - `start_date` and `target_date`: ISO YYYY-MM-DD if meaningful; otherwise null. The `Start date` / `Target date` Project fields are created only when at least one issue carries a date. Project item fields are populated only for newly added items, to preserve human edits.
  - `body`: Markdown with outcome, acceptance criteria, tests and evidence. A stable management marker is appended automatically, enabling duplicate-safe reruns.

## Date and dependency rules

- `due_on` is a real milestone due date in GitHub. Do not set an arbitrary date for demonstration on live repos.
- Start and target dates may be proposed, but their distinction from approved dates must be visible in project description/reports.
- No circular parent relations or blocked-by cycles; the script validates both before reading or writing GitHub.
- Record estimated effort separately in issue body or a Project `Estimate` field established by an approved process; the shipped script intentionally does not invent it.

## Lifecycle and project maturity

- **Do not require an MVP.** Infer project stage from releases, active users, existing roadmap, issue/PR history and current objectives.
- For an established repository, reuse the existing board, release/milestone policy, epics, work history and accepted status. Plan the next release, reliability, compatibility, maintenance or research evidence as appropriate.
- The JSON schema allows empty `milestones` and empty `issues` arrays. **Creating zero new issues/milestones is valid** when the project already has sufficient management records.
- Sample milestone keys `m0`/`m1` and example tasks are **fictional syntax examples**, not instructions to create M0/M1 stages in a real repo. Keep existing milestones when an actual target repo already has them.

## Existing-work reconciliation

- Match a previously managed issue via `<!-- github-project-orchestrator:key=... -->` in its body.
- Otherwise match by exact title if unique. This prevents duplicate issues but **does not mean authorization to edit an existing issue**; existing titles, bodies, labels, milestones and parent links remain unchanged.
- Duplicate titles or keys cause validation/execution errors.
- If a similarly named issue exists but no exact match, use judgment and reconcile manually before applying; fuzzy auto-merge would be dangerous.
- Project items that already exist are reused; current field values are preserved.
- Don't copy secret or NDA information from other repos into plans.