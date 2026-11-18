# WORKTREE-CHEATSHEET: one isolated copy per job

A git worktree is a second (third, fourth) checkout of the same repo, on its own branch, in its own
folder. Two Claude workers in ONE folder can erase each other's lines; in the episode a second worker
"threw away" the first one's changes with a git restore. One worktree per job stops that.

## Before the first worktree (once per repo)

```bash
git --version                                  # Windows: needs Git for Windows
echo ".claude/worktrees/" >> .gitignore        # worktrees live inside the repo folder; never commit them
git remote set-head origin main                # if you have a remote: new worktrees branch from origin's default branch
```

Windows: set `git config core.autocrlf false` in a fresh test repo, or every file can show as modified
after a clone. Use Git Bash or PowerShell; both work.

## Start a worker in its own copy

```bash
claude --worktree mehr        # short form: claude -w mehr
claude --worktree sufi        # second terminal
claude --worktree noor        # third terminal
```

| What you get    | Where                       |
| --------------- | --------------------------- |
| Folder          | `.claude/worktrees/<name>/` |
| Branch          | `worktree-<name>`           |
| List all copies | `git worktree list`         |

Running `claude --worktree <name>` again with an existing name reopens that copy; it does not make a
new one.

## Trust prompt

The first interactive session in a new copy can ask you to trust the folder, like any new folder.
`claude -p` (headless) does not ask, and it loads that folder's hooks and settings. Only run it in
repos you own.

## Gitignored local files: `.worktreeinclude`

A new worktree is a fresh checkout, so gitignored files (here `config/local.json`, the preview
settings) are missing and `python scripts/preview.py noor-dental` fails with
`ERROR: config/local.json not found`. List those files in `.worktreeinclude` at the repo root (same
pattern style as `.gitignore`):

```
config/local.json
```

- It is applied when a worktree is **created**. Reopening an existing worktree does NOT copy the file
  (we tested this: still failing). Remove the worktree and create it again.
- Never list real secrets in it just to make a worker run. Copying a key into three folders triples
  the places it can leak from.

## What isolation does and does not do

- A session in a worktree refuses to edit files in the main checkout through its edit tools
  ("This session is isolated in the worktree ..."). Good.
- A shell command (`cp`, a script) aimed at the main checkout is not blocked by isolation. In our
  test it was stopped only by the normal permission prompt. Keep `"defaultMode": "default"` and read
  the prompts.
- Isolation does not stop two copies from changing the same SHARED file. That is what
  `OWNERSHIP-SHEET.md` is for: in the episode Sufi and Noor both changed `shared/footer.html`, and
  the third merge stopped with `CONFLICT (content): Merge conflict in shared/footer.html`.

## Keep or remove when you exit

When an interactive worktree session ends, Claude Code asks whether to keep or remove the copy.

| Choose     | When                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------- |
| **Keep**   | work not merged yet, or you want to look at it again                                          |
| **Remove** | merged, or abandoned. Removing deletes the folder; unmerged commits on its branch are at risk |

Headless runs (`claude -p --worktree ...`) have no exit prompt and leave the copy in place. Clean up
by hand, only after the branch is merged or truly unwanted:

```bash
git worktree list
git worktree remove .claude/worktrees/noor     # add --force only if you are sure
git branch -D worktree-noor                     # only if merged or unwanted
git worktree prune                              # tidy stale entries
```

## Merge back (see MERGE-CHECKLIST.md)

Try merges on a scratch branch first:

```bash
git switch -c merge-test
git merge --no-edit worktree-mehr
git merge --no-edit worktree-sufi
git merge --no-edit worktree-noor     # a conflict here = two copies changed one shared file
git merge --abort                      # back out, give the file to its owner, redo
```

Then run the checks on the merged result (`python scripts/build.py`, `python scripts/check-site.py
<client>` for each client) before anything reaches `main`.
