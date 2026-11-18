# MERGE-CHECKLIST: nothing merges on "the job ran"

In the episode the first PR review on GitHub went green without reading anything: the job ran, so the
check passed. Green meant "ran", not "reviewed". A merge waits for an APPROVED verdict, and a person.

## Per pull request: all four, every time

| #   | Check                                    | How to see it                                                                      | Pass when                                                                                                                                                                       |
| --- | ---------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Required check green**                 | PR page, Checks: `site-review`                                                     | `site-review` is green AND it is a _required_ check on `main` (branch protection). A check that is not required does not block anything                                         |
| 2   | **Verdict approved, not just "job ran"** | the `site-review` job log ("Review verdict: ...") and the inline comment on the PR | The verdict is `APPROVED` and an inline comment says which client passed `check-site.py` (6/6). A green check with no verdict and no comment = the v1 workflow: not reviewed    |
| 3   | **A person read the diff**               | PR, "Files changed"                                                                | Someone on the team read every changed line, including any change to a shared file (`OWNERSHIP-SHEET.md`) and any change to `.github/workflows/` (those PRs skip the AI review) |
| 4   | **Who pressed merge**                    | written in the table below / PR timeline                                           | One named person merged it, after 1-3                                                                                                                                           |

## Copy this table for each merge

| PR  | Client | `site-review` required + green | Verdict APPROVED (comment seen) | Diff read by | Shared files touched (owner OK?) | Merged by |     |
| --- | ------ | ------------------------------ | ------------------------------- | ------------ | -------------------------------- | --------- | --- |
|     |        |                                |                                 |              |                                  |           |     |
|     |        |                                |                                 |              |                                  |           |     |
|     |        |                                |                                 |              |                                  |           |     |

## Stop signs: do not merge

- The check is green but the log shows no `Review verdict` and the PR has no inline comment.
- The verdict is `REJECTED` (v2 fails the check, so branch protection blocks the merge; do not
  override it with admin rights).
- The PR changes `.github/workflows/site-review.yml`: the action skips its own review on such a PR.
  Review it by hand.
- The PR changes a shared file and its owner has not agreed.
- `check-site.py` passes but a price on the page differs from `data/<client>.json`. In the episode a
  planted wrong price (cleaning 3000 on the page, 3500 in the data) was REJECTED and the merge was
  blocked until it was fixed.
- A red check from an infrastructure error (for example an HTTP 504 while the action sets up). Re-run
  the job; do not treat it as a verdict either way.

## One-time setup: make the check required

GitHub, repo Settings, Branches (or Rules), protect `main`, require status check `site-review`.
Or with the GitHub CLI (replace `<owner>/<repo>`; this command was not run for the kit, check it against the GitHub docs):

```bash
gh api -X PUT repos/<owner>/<repo>/branches/main/protection \
  -F "required_status_checks[strict]=false" \
  -F "required_status_checks[contexts][]=site-review" \
  -F "enforce_admins=true" \
  -F "required_pull_request_reviews=null" \
  -F "restrictions=null"
```

`enforce_admins=true` means admins cannot merge past a red check either. The recorded repo used
`false`; for a team, `true` is the stricter choice.

## After merging several worktree branches

- [ ] Merged on a scratch branch first (`WORKTREE-CHEATSHEET.md`), no conflicts left.
- [ ] Shared-file change made once, by its owner, after the client branches.
- [ ] `python scripts/build.py` ran, and `python scripts/check-site.py <client>` passes 6/6 for every client.
- [ ] Worktrees of merged branches removed (`git worktree remove ...`).
