# Reusable examples — use any project

This is the **generic usage guide** for GitHub Project Orchestrator. Replace placeholders each time; do not copy a specific project's tasks into another project.

## Replace these fields

| Placeholder | What to enter | Example (illustrative only) |
|---|---|---|
| [NAME OF THE PROJECT] | Human-readable name | My Example App |
| [GITHUB REPOSITORY URL] | Exact target repository URL | https://github.com/OWNER/REPOSITORY |
| [CURRENT GOAL] | Next meaningful outcome | Stabilize the existing release and resolve confirmed blockers |
| [PROJECT LIFECYCLE] | AUTO-DETECT or your selected stage | AUTO-DETECT |
| [APPROVED DEADLINE] | Real approved deadline, or NONE APPROVED | NONE APPROVED |
| [LINK OR PATH TO APPROVED PLAN] | Reviewed JSON plan or GitHub discussion | Not yet approved |

**Important:** In the executable JSON plan, write the actual `OWNER/REPOSITORY`, project title, and verified work. The example JSON uses `OWNER/REPOSITORY` as a syntactically valid placeholder. Square-bracket prompts are **not** inputs to `gh` or the JSON schema. Do not apply the fictional plan as-is.

## Match the existing project stage

| Stage | Planning emphasis |
|---|---|
| New | Scope, feasibility, prototype, optional MVP |
| Pre-release | Actual next release and readiness gates |
| Established / released | Reliability, current backlog, next release, compatibility, community and contributor work |
| Research | Experiments, evaluation evidence, datasets and publication gates |
| Maintenance-only | Regressions, security, support and deprecation where applicable |

**For existing projects:** audit and reconcile the real board, milestones and issues first; the desired output may be just updated relationships or a status report, with **zero new milestones and zero new issues**. Never reproduce historical completed work, create a second board or add an MVP by default.

## Example: first-time setup for any repository

1. Copy [the ChatGPT project setup prompt](../prompts/CHATGPT.md) into a ChatGPT chat with GitHub connected. Fill in **[NAME OF THE PROJECT]** and **[GITHUB REPOSITORY URL]**. Ask for a read-only audit and draft change set.
2. Review the findings and approve only the plan you want.
3. Copy [the Claude Code setup prompt](../prompts/CLAUDE.md) into Claude Code. Give it the approved plan, target repo URL, and access to this toolkit.
4. Claude Code audits the repo again, prepares `project-plan.json`, validates it, performs a connected **dry-run**, and asks before an apply.
5. After approval, Claude Code runs the CLI provisioner, verifies the actual board/issue links/fields, and returns the URLs.
6. For later check-ins, use [the weekly review prompt](../prompts/WEEKLY_REVIEW.md).

## Expected hierarchy (fictional illustration for an already released project)

    [NAME OF THE PROJECT] — existing GitHub Project V2 (reuse)
    ├── Existing milestone: current release / next meaningful outcome
    │   ├── Existing epic: Reliability and compatibility (reuse)
    │   │   ├── Existing regression issue (do not recreate)
    │   │   └── Missing verified test gate (only if genuinely needed)
    │   └── Existing epic: Next increment (reuse if present)
    │       └── A bounded, accepted improvement
    └── Evergreen bugs / translations / community (may have no milestone)

The hierarchy is **illustrative only**; do not invent those milestones or issues if the target repository does not need them. A greenfield project may instead use prototype or MVP stages when supported by the goals.

In GitHub, milestones track targets; epics and children are **real issues**; blockers are **native dependencies**. Never mistake textual indentation for a native GitHub relationship.

## CLI commands after creating a truthful plan

    cp examples/project-plan.example.json project-plan.json
    # Edit the plan with actual repository evidence. Use no invented deadlines.
    python3 scripts/github_project_sync.py --plan project-plan.json --check-only
    python3 scripts/github_project_sync.py --plan project-plan.json
    # Only after inspecting the dry-run and approving exact writes:
    python3 scripts/github_project_sync.py --plan project-plan.json --apply --confirm OWNER/REPOSITORY

Use `gh auth login` and ensure the appropriate GitHub Project permissions are available. Real GitHub API behavior and view/workflow settings must be verified; unit tests alone do not demonstrate a successful live setup.

## ChatGPT versus Claude Code

| Role | Primary responsibility |
|---|---|
| **ChatGPT** | Discovery, backlog design, business/project priorities, issue decomposition, roadmap, owner dashboard and handoff |
| **Claude Code** | Code-aware design review, create JSON plan, execute CLI dry-run and approved writes, test and verify native GitHub objects |
| **You** | Decide project scope, approve exact GitHub changes and commitments |

Use the same generic prompts with each new project; do not create a different skill for every repository.
