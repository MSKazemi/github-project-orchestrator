# Agent instructions

Purpose: maintain a reusable tool that provisions **real** GitHub Project V2 boards, milestones, issue hierarchies, blocking relationships, fields and plans for separately scoped target repositories.

Workflow: inspect the repository and relevant target first; propose a change; run unit tests and `--check-only`; perform no remote writes without explicit owner approval and `--confirm OWNER/REPO`; report verified URLs and failures accurately. Do not copy private target data into this public repository or change existing human-managed GitHub objects without consent.

Read `.claude/skills/github-project-orchestrator/SKILL.md` for the command workflow, `README.md` for installation, and `skills/chatgpt/github-project-orchestrator/SKILL.md` for ChatGPT behavior.