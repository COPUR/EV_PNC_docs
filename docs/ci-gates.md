# CI gates for EV_PNC and EV_PnC_Consent repositories

Every pull request passes two gates before it merges. Both are one shared workflow each in
[EV_PNC_infra-modules](https://github.com/COPUR/EV_PNC_infra-modules) (`auditor/README.md` there has the details).

1. **Auditor** (`audit / gitleaks`, `audit / repository audit`): secret scan with the project rules (Turkish national ID,
   card PAN, OCPI token, Kafka JAAS password) and repository and workflow hygiene.
2. **Approver** (`approve / ci-approver`, commit status `ci-approver`): reads the pull request through the API, never runs
   its code, and merges it when everything is green and nothing needs a human.

## What the approver decides

| Verdict | Meaning |
|---|---|
| approve | all checks green, no sensitive path, up to 100 files and 3000 lines, trusted author, no open review thread: it merges (squash) |
| wait | other checks still running; it polls up to 15 minutes |
| hold | a person has to look: draft, stacked or fork PR, label `hold`, `do-not-merge` or `needs-human`, a sensitive path, a big or unreadable diff, a deleted or disabled test, an unresolved thread |
| block | a failed check, merge conflict, changes requested, conflict marker or private key in the diff |

Sensitive paths always need a person: `.github/workflows/`, `.github/actions/`, `CODEOWNERS`, `.gitleaks.toml`,
`.auditor-allow`, `*.tf`, `*.tfvars`, Dockerfiles. A change to CI or to the secret scanner cannot approve itself.

## Working with it

- Open the PR as a draft; mark it ready for review when you want it merged. A ready PR that passes merges by itself.
- Add the label `hold` to stop an automatic merge.
- The approval is a status check, not a GitHub review, because the author of a PR cannot approve it.
- Only the repository owner can make the checks required in branch protection. Until then a person can still merge by hand.
