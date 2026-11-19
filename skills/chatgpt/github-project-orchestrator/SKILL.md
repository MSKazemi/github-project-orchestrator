---
name: github-project-orchestrator
description: Create and maintain real native GitHub project management for a software repository. Use when someone gives a GitHub repository URL and wants GitHub Projects V2 created or updated, connected milestones, epic and child issues, dependencies, priorities, dates, issue labels, release gates, contributor work and safe automation. Read the actual repository and existing GitHub issues/projects first, generate a deduplicated machine-readable plan, then apply authorized changes with the GitHub connector or the bundled GitHub CLI provisioner. Also use for ongoing synchronization, grooming and project management setup across multiple repositories.
---

# GitHub Project Orchestrator

**Output is live GitHub objects, not a Markdown-only roadmap.** Given an authorized `OWNER/REPO`, audit the current repo, build or reconcile the native GitHub Project, milestones, issues/epics/sub-issues, blocking dependencies, fields and optional board/roadmap views. Provide URLs and evidence of each verified action. Do not call an unexecuted plan "created".

## Choose the project's lifecycle before planning

Infer the **current lifecycle from evidence**, not from the repository age or the existence of code alone: releases/packages, production users, open and closed work, release notes, maintenance obligations, roadmaps and current goals. Record evidence and uncertainty. Distinguish:
- **New / exploratory:** problem discovery, feasibility, prototype and optionally an MVP if the owner wants one.
- **Pre-release / active build:** the next validated release or agreed product increment; do not restart discovery.
- **Established / already released:** current delivery state, defects and safety/security, compatibility, technical debt, adoption, CI/release health, contributor work and the **next real release or objective**. **Never invent another MVP.**
- **Research:** reproducible experiments, datasets, benchmarks, papers and evidence gates rather than a product MVP.
- **Maintenance-only / sunset:** bug fixes, security, support and deprecation or migration obligations.

For an established repository, **reconcile existing milestones, epics, issue hierarchy and the current board first**. Preserve done work and historical releases; don't reconstruct them or generate "M0 baseline / M1 MVP" by default. New milestones are optional and must correspond to justified outcomes under the repository's milestone policy; evergreen tasks can have no milestone. If no changes are necessary, output a maintenance/report-only result. Where lifecycle is uncertain, report unknown and ask for a decision before committing a new product stage.

## One-repo execution loop

1. **Discover:** read README, CONTRIBUTING, SECURITY, ROADMAP, AGENTS.md/CLAUDE.md, existing machine-readable plans, open/closed issues, PRs, GitHub Projects V2, milestones, labels, workflows, releases, active branch and CI. Read only files in permitted scope. If a repo has 1,000+ issues or many projects, paginate and stop on incomplete inventory rather than create duplicates.
2. **Reconcile:** identify canonical existing project board and source of truth. Never create a second board where an appropriate one exists. Do not rename/overwrite existing titles, labels, milestones, issue bodies, fields, status, dates or parent links without specific authorization. For private/business projects, respect sharing boundaries; no personal contracts/negotiations in shared repos.
3. **Plan:** select the lifecycle-appropriate goal: an MVP only for a new project when justified; otherwise the current release, next increment, research outcome or maintenance priorities. Preserve existing milestones and historical completion; add only missing, measurable epics/sub-issues, acceptance criteria, dependencies, prioritized backlog, risks and CI/release gates. Every proposed object has a unique stable key. Do not fabricate facts, budgets, owners, staff capacity or fixed deadlines. Proposed dates are not approved due dates.
4. **Validate:** use `scripts/github_project_sync.py --plan PATH --check-only` locally to validate schema, refs, and cycles without any network. For connected preflight (GitHub CLI present), run with `--plan PATH` and no `--apply`; this reads GitHub and prints a prospective change list. Review creates/links/updates, verify scopes and compare existing objects.
5. **Apply:** only after user's explicit permission, prefer connected GitHub actions for issues/labels/file operations when available. Projects V2 create/field/item/link actions may require GitHub CLI or GraphQL/REST with authorized credentials. The bundled script is the default CLI provisioner; run with `--apply --confirm OWNER/REPO`. Never copy tokens into plans, prompts, issues or repository files. If the current environment cannot run authenticated GitHub CLI, provide the precise commands/work packet for Claude Code instead of reporting success.
6. **Verify:** re-fetch GitHub Project URL, milestone links, issue numbers, parent/sub-issue edges, blocked-by edges, Project fields and active workflows. Provide a creation/reuse/skip/error ledger with links; report anything that could not be verified. Separate project objects from code/PR changes; GitHub views and automations are not active unless API/UI verification succeeded.
7. **Maintain:** on next invocation, read live GitHub again; reconcile status, stale blockers, PRs, overdue *approved* dates, release dependencies and contributor availability. Prefer fixes to existing issues; create new ones only for truly new scope.

## Modes

- **setup**: repo audit -> plan -> approval -> live GitHub Projects + milestone + issue graph provisioning -> verify.
- **sync**: compare live GitHub with plan; add missing project objects/links; preserve human edits by default; report conflicts.
- **triage**: label and prioritize existing work, detect duplicates, obsolete tasks, broken dependencies, missing acceptance criteria; ask before consequential bulk edits.
- **release**: check gates, evidence, security, migration, rollback, docs and approval; propose release issues and blockers, not an automatic deployment.
- **weekly**: report what's completed, blocked, at risk, next, and which GitHub issue each agent/human should take.

## GitHub object mapping

| Intent | GitHub object |
|---|---|
| Program board | GitHub Projects V2 attached to repository |
| Roadmap stages | Repository milestones with measurable exit criteria |
| Epic | Parent issue (Issue Type Epic if configured; otherwise `[EPIC]` + `type:epic` label) |
| Tasks/stories/bugs | Normal issue with real sub-issue relationship to epic |
| Dependencies | Native `blocked by` / `blocking` issue relationship, not only body text |
| Priority | `Priority` single-select field + compatible priority labels |
| Dates | `Start date` / `Target date` fields (proposed until approved); milestone due date only if human-approved |
| Execution status | Project native `Status` field, reconcile without overwriting updates |
| Contributor execution | Assigned GitHub issues -> branch/PR -> CI -> review -> completion |
| Automation | GitHub built-in Project workflows and/or reviewed GitHub Actions, verified active |

**Priority:** P0 urgent safety/security/data loss; P1 blocks accepted deliverables; P2 near-term improvement; P3 backlog. Do not assign P0 merely for marketing urgency. Tasks require outcome, bounded scope, acceptance checks, evidence/tests, dependency, risk and role-based ownership. Preserve existing labels and status taxonomies whenever possible.

## Bundled executable provisioner

`assets/project-plan.example.json` is a *template only*; it must be rewritten for the real audited repo. It uses placeholder `OWNER/REPOSITORY`, and must never be blindly applied. `scripts/github_project_sync.py` implements read-before-write, stable issue keys, cycle detection, reuse by key or exact title, required confirmation for `--apply`, native milestone/issue/relationship creation, Project fields and assignment. It updates neither repo source code nor existing issue bodies. On subsequent runs, existing issue title matches preserve the issue and warn about unreviewed hierarchy edits.

```bash
# 1. Review and customize a JSON plan based on the live repository
python3 scripts/github_project_sync.py --plan path/to/plan.json --check-only
# 2. Read actual GitHub state, preview mutations; requires logged-in gh
python3 scripts/github_project_sync.py --plan path/to/plan.json
# 3. Only after owner authorizes this exact plan
python3 scripts/github_project_sync.py --plan path/to/plan.json --apply --confirm OWNER/REPO
```

`--with-views` makes a best-effort attempt to create Backlog/Board/Roadmap views on a *new* Project only; availability differs by project owner and token type. Built-in workflow toggles remain separate and must be checked in the GitHub UI. Read `references/gh-implementation.md` for credentials, limitations and current CLI details. Read `references/plan-schema.md` when composing plans. Read `references/execution-handoff.md` when delegating to Claude Code.

## Failure and honesty rules

- If GitHub Projects V2, org issue types, view creation or automation writes are unsupported by the current connector/token, **stop that step and report the exact blocker**, do not substitute Markdown while claiming that GitHub was changed.
- Do not silently create/close/merge PRs or issues, delete a Project, archive items, approve budgets, assign people without permission, deploy or publish releases.
- CLI script does not enable built-in Project workflows or schedule Actions. Never claim continuous automation until a real workflow is configured and successfully run.
- Use local timezone Europe/Rome for reporting, UTC for API timestamps and ISO dates in plans. Respect private information classifications per repo.