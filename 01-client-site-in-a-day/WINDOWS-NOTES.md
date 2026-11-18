# Windows notes

Claude Code runs on Windows, macOS and Linux. These notes cover the Windows-specific parts of Episode 1. Official troubleshooting: https://code.claude.com/docs/en/setup (section on troubleshooting the install). Re-check after each Claude Code update.

## PowerShell vs CMD

- The Windows install command is a **PowerShell** command. It does not work in the old Command Prompt (CMD).
- How to tell: a PowerShell prompt starts with `PS`, for example `PS C:\>`. CMD shows only `C:\>`.
- To open PowerShell in a folder: in File Explorer, right-click the folder → **Open in Terminal**. Windows Terminal opens PowerShell by default.
- Copy the install command from the official setup page, PowerShell tab, not from a video: it can change.

```
irm https://claude.ai/install.ps1 | iex
```

Nothing moves on screen while it downloads. That is normal.

## "claude is not recognised"

After installing, open a **new** terminal window and type:

```
claude --version
```

A version number means it worked. If Windows says `claude` is not recognised, the install folder is not on your PATH in that window yet. Close the terminal and open a fresh one. Still stuck: follow the troubleshooting section on the official setup page.

## Install Git for Windows

- Download: https://git-scm.com/downloads/win
- Claude Code runs without it, using PowerShell, and that is fine for Episode 1.
- From Episode 2 on you need it: Git Bash runs the hook scripts, and git runs the worktrees used later in the course.
- With Git for Windows installed, Claude Code can use both tools: Bash and PowerShell.

## Paths and opening the preview

- Windows paths use backslashes (`<your-project>\mehr-bakery\index.html`). Claude Code shows the working folder at the top of the session; check it is the one folder you meant.
- Open the preview with a double click on `index.html` in File Explorer. If Claude offers to open it, it runs a PowerShell command such as `Start-Process`, which raises a command prompt. Answering "don't ask again" there is remembered for the project.

## Before Episode 2

- [ ] `claude --version` prints a version in a new PowerShell window
- [ ] Git for Windows installed (`git --version` prints a version)
