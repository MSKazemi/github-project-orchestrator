---
name: github-project-orchestrator
description: Audit an existing GitHub repository then create or reconcile its real native GitHub Project V2, milestones, epic/sub-issue hierarchy, blocking dependencies, P0-P3 priority fields, date fields and delivery backlog. Use when asked to set up professional GitHub project management, update a roadmap, break features into linked issues, assign milestones, manage blockers, or synchronize a GitHub Project for any repository. Requires authenticated gh CLI for remote writes. Default to read-only audit and dry-run; apply only authorized changes.
---

# GitHub Project Orchestrator — Claude Code

Operate on real GitHub objects, not just README and ROADMAP text. Accept `OWNER/REPO` or `https://github.com/OWNER/REPO`. Use the GitHub CLI (`gh`) and checked-in `scripts/github_project_sync.py` after reading the target repo. The skill is reusable across different repos; do not create a new management-framework repo for each target.

## Choose the project's lifecycle before planning

Infer the **current lifecycle from evidence**, not from the repository age or the existence of code alone: releases/packages, production users, open and closed work, release notes, maintenance obligations, roadmaps and current goals. Record evidence and uncertainty. Distinguish:
- **New / exploratory:** problem discovery, feasibility, prototype and optionally an MVP if the owner wants one.
- **Pre-release / active build:** the next validated release or agreed product increment; do not restart discovery.
- **Established / already released:** current delivery state, defects and safety/security, compatibility, technical debt, adoption, CI/release health, contributor work and the **next real release or objective**. **Never invent another MVP.**
- **Research:** reproducible experiments, datasets, benchmarks, papers and evidence gates rather than a product MVP.
- **Maintenance-only / sunset:** bug fixes, security, support and deprecation or migration obligations.

For an established repository, **reconcile existing milestones, epics, issue hierarchy and the current board first**. Preserve done work and historical releases; don't reconstruct them or generate "M0 baseline / M1 MVP" by default. New milestones are optional and must correspond to justified outcomes under the repository's milestone policy; evergreen tasks can have no milestone. If no changes are necessary, output a maintenance/report-only result. Where lifecycle is uncertain, report unknown and ask for a decision before committing a new product stage.

## Mandatory workflow

1. Read target repo README, CONTRIBUTING, SECURITY, AGENTS.md, CLAUDE.md, roadmap docs, issues (open and closed), pull requests, milestones, Project boards, labels and current CI. On a private repo, authenticate with authorized account; never echo tokens. Stop if repo content is insufficient for planning.
2. Check existing GitHub Project boards and roadmap documents before proposing duplicates. Treat GitHub Issues/PRs/Projects as the execution source of truth. Preserve manual edits, milestones, statuses and assignments.
3. Select a lifecycle-appropriate sequence: only plan an MVP for a genuinely early-stage project when justified; for a released product, work from existing releases and milestones toward the next deliverable, reliability and maintenance needs; for research, use evidence/experiment gates. Construct `project-plan.json` using the repository's actual language, components and test structure. Use the example only for JSON syntax, not its fake tasks. Put epics before related work conceptually; the provisioner creates real parent/sub-issue relationships by key regardless of JSON ordering. Add blocked-by keys and verify the graph has no cycles.
4. Validate and preview:

```bash
python3 scripts/github_project_sync.py --plan project-plan.json --check-only
python3 scripts/github_project_sync.py --plan project-plan.json
```

5. Summarize exact creates, reuses, dates, priorities, costs/permissions and unverified elements. Secure human approval of the intended scope before writes, unless the user's current message already explicitly authorizes applying that precise scope.
6. Apply:

```bash
python3 scripts/github_project_sync.py --plan project-plan.json --apply --confirm OWNER/REPO
```

7. Re-read GitHub Projects V2, milestones, issues, native sub-issues, blocked-by relationships, Project fields, and view/workflow status to **verify**. Give clickable links and a Created/Reused/Skipped/Failed report; never claim views/workflows worked when API/UI verification did not succeed.
8. For ongoing management, reconcile issues/PRs/CI weekly, prioritize blocked paths and release gates, and hand engineering tasks to scoped branches/PRs. Do not merge, deploy, spend, publish or overwrite governance files without permission.

## Requirements

- Recent GitHub CLI (`gh`) with issue hierarchy and dependency flags, plus authenticated `project` scope; check `gh auth status` and `gh project list --owner OWNER`.
- Default statuses should follow the existing board; do not impose new taxonomy over active human workflow.
- Proposed dates are not binding commitments. Use ISO dates and Europe/Rome display timezone; no invented schedule.
- If view API permissions differ, create what is supported and report the blocker; the script can use `--with-views` on new projects only but cannot enable all built-in workflows. Document UI follow-up.
- Never copy secrets or private negotiations into GitHub issues or plans. For a shared management repository, strictly respect allowed scope.
- Before running a project script from this repository, ensure the script path is correct; don't substitute another project's existing script without inspection.