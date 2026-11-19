# GitHub Project Orchestrator

**Purpose:** one reusable Skills + CLI toolkit that sets up and maintains *real* GitHub Projects V2, milestones, epics, sub-issues, native dependencies, priorities, dates and contributor-ready issues in any target repository.

This is **not** itself a centralized GitHub Projects board. The target repo owns its own issue/PR/workflow state. This repository only versions the reusable method and provisioner. The skill source is stored in `skills/chatgpt/` and `.claude/skills/` for their respective clients.

## Branch policy

This toolkit repository uses **`main` as its single long-lived branch**. Do not create feature branches by default. If the owner explicitly requests PR-based review, keep it temporary, review tests, merge after authorization, and delete the merged branch. This policy applies to **this toolkit repository**; do not override each target repository's own contribution and branch rules.

## Copy-and-paste prompts for ANY project

No need to write a new prompt or Skill for each repository. Replace `[NAME OF THE PROJECT]` and `[GITHUB REPOSITORY URL]` in the linked templates:

| Start here | Use with | What happens |
|---|---|---|
| [ChatGPT — project setup and management](prompts/CHATGPT.md) | ChatGPT + GitHub connector | Audit, plan, propose milestones/epics/dependencies and request approval for GitHub changes |
| [Claude Code — provision GitHub](prompts/CLAUDE.md) | Claude Code + authenticated `gh` | Review code, build a valid JSON plan, dry-run, apply approved native GitHub objects and verify links |
| [Weekly project review](prompts/WEEKLY_REVIEW.md) | ChatGPT (or Claude Code) | Read-only status, blockers, PRs, priorities, risks and next actions |
| [Step-by-step generic example](examples/README.md) | Either | Shows placeholders, example hierarchy, commands and roles |

**Example input:** Project `[NAME OF THE PROJECT]`; repository `[GITHUB REPOSITORY URL]`. Always start by inspecting the live repository, then plan, approve the exact writes, apply through authorized tools and verify the resulting GitHub objects.

## Setup

1. Install GitHub CLI (latest release), authenticate: `gh auth login`. Check permissions with `gh auth status`; for Projects, if needed run `gh auth refresh -s project`.
2. Clone this toolkit and run it with local Python 3.10+ (stdlib only).
3. For Claude Code, copy or symlink `.claude/skills/github-project-orchestrator/` to `~/.claude/skills/github-project-orchestrator/`, or keep it local as a repo skill. For ChatGPT, install the separately packaged `skill.zip` in your Skills library if available.
4. Give one target repo URL. Audit existing objects with ChatGPT/Claude before editing the example JSON.
5. Copy and **replace** `examples/project-plan.example.json` with repo-specific verified tasks and naming; leave dates null until approved.
6. Validate, review the connected read-only diff, then apply:

```bash
cp examples/project-plan.example.json project-plan.json
# Edit project-plan.json: OWNER/REPOSITORY, objective and accurate planned tasks.
python3 scripts/github_project_sync.py --plan project-plan.json --check-only
python3 scripts/github_project_sync.py --plan project-plan.json
python3 scripts/github_project_sync.py --plan project-plan.json --apply --confirm OWNER/REPOSITORY
```

`--apply` creates actual GitHub objects; the default mode only previews. `--with-views` optionally attempts creating board/roadmap/table views **only for new projects**, depending on REST API/token permissions. GitHub Project built-in workflow configuration and Actions runners require separate enablement and validation.

## What does the provisioner actually change?

| Object | Supported action |
|---|---|
| Projects V2 | Create or reuse project; link new project to target repo |
| Fields | Create Priority, Start date, Target date if absent |
| Milestones | Create missing repo-level milestones and approved due dates |
| Labels | Create missing priority and epic/task labels |
| Epics/issues | Create with stable managed key; reuse existing exact-title matches |
| Hierarchy | Link newly created tasks to parent epic as native sub-issues |
| Dependencies | Native blocked-by relationships for new/managed issues |
| Project items | Add missing issues, set new item fields, leave existing values alone |
| Views | Optional best effort on new projects; manual fallback if unsupported |
| Automations | Propose and verify separately; no false claim that they are active |

**Existing title matches:** intentionally reuse but do *not* silently rewrite or re-parent the issue; reconcile manually if you need to change its structure. A failed mid-apply is not transactional; rerun with the same stable keys after inspecting GitHub. Report issues when no supported write capability exists.

## Examples of usage

- `Set up complete GitHub project management for https://github.com/MSKazemi/yazses, including native epics/sub-issues and a Projects V2 board.`
- `Synchronize the KubeIntellect project board with existing issues, identify orphan issues and blocked milestones. Do not duplicate epics.`
- `Create milestone-driven AOBench research work with dependencies and validation gates, then open a GitHub Project.`

## Security

Never commit tokens, credentials, customer information or personal legal/negotiation material. Keep private-repo details inside their authorized boundaries. Avoid repo-specific automation that grants broader permissions than required. Review `gh` authorization before execution and inspect the resulting GitHub URLs.

Current scripts were tested with an offline stateful fake GitHub CLI; this is **not** a live API integration test. Confirm permission and remote behavior on a low-risk test repository before applying to production repositories.

## Repository layout and packaging

- `.claude/skills/github-project-orchestrator/SKILL.md`: repository-level Claude Code skill; run Claude Code with this repository available or copy it to `~/.claude/skills/` for global reuse.
- `skills/chatgpt/github-project-orchestrator/`: complete ChatGPT Skill source (instructions, metadata, scripts, references, example plan). Package this folder as a Skill ZIP with `python3 scripts/package_chatgpt_skill.py`; upload via the ChatGPT Skills interface where available.
- `scripts/github_project_sync.py`: standalone GitHub CLI provisioner; `--check-only` does not contact GitHub.
- `examples/project-plan.example.json`: **fictional template**. Never apply without editing both target repo and work items based on actual audit.
- `tests/test_sync.py`: regression tests with mocked `gh`, **not** proof that remote APIs work.
- `.github/workflows/ci.yml`: Python syntax/unit tests and offline plan-schema checks; runs only when GitHub Actions runners are available.

## Contributing

Please open an issue describing the observed GitHub behavior and CLI version before proposing an API change. Keep scripts idempotent and read-only by default. All PRs should include a test for the change, confirm no unapproved remote mutation in dry-run, and explain real-world verification separately from mocked tests.

This repository does **not** automatically provision project management for every repository on your account. Use the toolkit with one audited target repository at a time and approve a concrete plan before `--apply`.