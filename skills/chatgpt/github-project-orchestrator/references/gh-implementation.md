# GitHub CLI, API and verification notes

## Prerequisites

Install a recent GitHub CLI version that supports `gh issue create --parent` and `gh issue edit --add-blocked-by`. Run `gh auth login`, `gh auth status`, and `gh auth refresh -s project` if your token allows it. Ensure issue write access to the repository and project permissions for the chosen owner. Never paste a token into conversation or commit it to a repository.

**Native API / CLI mapping**

- `gh project list --owner OWNER --format json`; `gh project create --owner OWNER --title TITLE --format json`; `gh project link NUMBER --owner OWNER --repo OWNER/REPO`.
- `gh project field-create NUMBER --owner OWNER --name Priority --data-type SINGLE_SELECT --single-select-options P0,P1,P2,P3`.
- `gh project item-add NUMBER --owner OWNER --url https://github.com/OWNER/REPO/issues/N`.
- `gh project item-edit NUMBER --owner OWNER --url ISSUE_URL --field Priority --value P1`; dates use `--field 'Target date' --date YYYY-MM-DD`.
- `gh issue create -R OWNER/REPO --title ... --body ... --label ... --milestone ...`.
- `gh issue edit N -R OWNER/REPO --parent EPIC_NUMBER` creates an actual sub-issue relationship, not merely an issue-body checklist.
- `gh issue edit N -R OWNER/REPO --add-blocked-by OTHER_ISSUE_NUMBER` creates a native dependency.
- Milestones and project views can also use `gh api` authenticated REST endpoints. The script uses `gh api` for milestone creation.

Reference documentation:
- https://cli.github.com/manual/gh_project
- https://cli.github.com/manual/gh_project_item-edit
- https://cli.github.com/manual/gh_issue_edit
- https://docs.github.com/en/rest/issues/sub-issues
- https://docs.github.com/en/rest/issues/issue-dependencies
- https://docs.github.com/en/rest/projects/views
- https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations

## Views and automation constraints

- The script optionally attempts creation of a Table, Board and Roadmap view only when it creates a new Project; it does not create duplicate views in existing projects. GitHub Projects view API authorization differs for user-owned and org-owned projects; failure is logged, not counted as success. Configure native project view filters, grouping and date bars in the UI if needed.
- Project built-in workflows include closed/merged -> Done. Auto-add, project Status transitions and item archiving can be configured separately in Project > Workflows. Review whether toggles are enabled and verify behavior with a safe test issue.
- Actions-based scheduled reconciliation should use minimum permissions, a token with Project scope only if essential, least-cost schedule, and never bypass GitHub account Actions usage/billing restrictions.
- This script does not configure GitHub workflows, branch protections, CODEOWNERS, org issue types, review rules, release publication or CI. It may propose them as a separate scoped PR, not mark them as active.

## Operational safety

- `--check-only`: offline JSON and graph validation; no network, no writes.
- No `--apply`: authenticates/read actual state; prints proposed operations; no writes.
- `--apply --confirm OWNER/REPO`: makes incremental GitHub writes. GitHub API operations are not a transaction; if interrupted, rerun from the same plan and review warnings; do not create a new plan with changed keys.
- Existing matched titles, bodies and project fields are preserved, and existing hierarchy links aren't silently rewritten. Existing issues with managed markers may receive missing parent or blocker relationships; conflicting relationships are preserved for review.
- Use `--with-views` only if creating a new project and token supports the REST API. Verify result manually.
- After applying, query GitHub again and report actual URL, issues, milestones, relationships and Project item fields. Do not treat command exit status as independent verification of correctness.