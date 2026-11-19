{
  "schema_version": 1,
  "repository": "OWNER/REPOSITORY",
  "project": {
    "owner": "OWNER",
    "title": "REPOSITORY Delivery",
    "description": "Roadmap, epics, technical work, blockers and release readiness. All dates are proposed until approved.",
    "visibility": "PRIVATE"
  },
  "milestones": [
    {
      "key": "m0",
      "title": "M0 - Verified baseline",
      "description": "Reproducible baseline tests, risk review and approved scope. No deadline set without owner agreement.",
      "due_on": null
    },
    {
      "key": "m1",
      "title": "M1 - MVP candidate",
      "description": "Implementation and evidence for a reviewable MVP candidate.",
      "due_on": null
    }
  ],
  "issues": [
    {
      "key": "baseline-epic",
      "kind": "epic",
      "title": "[EPIC] Establish verified engineering baseline",
      "body": "## Outcome\nCreate reliable, reproducible engineering gates.\n\n## Acceptance criteria\n- [ ] Owner reviews baseline evidence\n- [ ] CI failures and unsupported assumptions documented\n- [ ] Release blockers visible in GitHub",
      "priority": "P1",
      "milestone": "m0"
    },
    {
      "key": "test-audit",
      "kind": "task",
      "title": "Audit test and CI coverage against current architecture",
      "body": "## Outcome\nCreate an evidence-backed inventory of test and CI gaps.\n\n## Acceptance criteria\n- [ ] Record observed commands and results\n- [ ] Separate mocks from real integration evidence\n- [ ] Link every critical gap to an issue",
      "priority": "P1",
      "milestone": "m0",
      "parent": "baseline-epic",
      "blocked_by": [],
      "start_date": null,
      "target_date": null
    },
    {
      "key": "release-gate",
      "kind": "task",
      "title": "Document MVP release criteria and verification checklist",
      "body": "## Outcome\nDefine an auditable MVP GO/NO-GO checklist.\n\n## Acceptance criteria\n- [ ] Pass/fail gates are testable\n- [ ] Human approval gate recorded\n- [ ] Rollback process is linked",
      "priority": "P2",
      "milestone": "m1",
      "parent": "baseline-epic",
      "blocked_by": ["test-audit"],
      "start_date": null,
      "target_date": null
    }
  ]
}