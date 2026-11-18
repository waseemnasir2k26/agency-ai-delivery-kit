# Permission modes: who approves what

Claude Code can change files and run commands on your computer. The permission mode decides how often it asks you first. On day one with a client's work, you want it to ask.

Mode names, the starting mode and the exact wording of the prompts can change between Claude Code releases. Re-check this page against the official docs after each Claude Code update: https://code.claude.com/docs (pages "Permission modes" and "Permissions").

## The four modes in this course

| Mode (bottom line shows)      | Settings value  | What it asks before                                                                  | Use it when                                                                     |
| ----------------------------- | --------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Manual** (`manual mode on`) | `"default"`     | Every file edit and every command. Reading files in the project folder does not ask. | New project, new client, anything you have not watched work yet. This episode.  |
| **Accept edits**              | `"acceptEdits"` | Commands still ask. File edits (and common file commands) are approved for you.      | You have read and approved the plan and know which files are coming.            |
| **Plan** (`plan mode on`)     | `"plan"`        | Claude reads, thinks and writes a plan. It does not edit your files.                 | Anything bigger than a tiny change: see the drawing before the walls come down. |
| **Auto** (`auto mode on`)     | `"auto"`        | A background check approves most actions and stops risky ones.                       | Later in the course, once you have decided it fits the project.                 |

## How to see and change the mode

- **See it:** the line at the bottom of the Claude Code screen always shows the current mode.
- **Change it:** press **Shift+Tab** to move to the next mode. In the recording, from auto one press gave manual; from manual, two presses gave plan (manual → accept edits → plan); a third press went back to auto.
- **Plan for one message:** start the message with `/plan`.
- **Teach auto mode your environment:** `/auto-mode-setup` (later in the course).

## Pin a project to Manual

Put this in `.claude/settings.json` inside the project folder (`starter/.claude/settings.json` is exactly this):

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

Interactive sessions may otherwise start in auto mode, depending on your Claude Code version and settings. Remove this line once you have decided auto mode is right for this project. JSON cannot hold comments, so the note sits in `starter/.claude/SETTINGS-NOTE.md`.

## The three answers to a permission prompt

When Claude stops and asks, the prompt shows exactly what it wants to do (which file, what content; or which command).

1. **Yes**, just this once.
2. **Yes, and stop asking** about this kind of action. For **file edits** this lasts for the session (in the recording it read "Yes, and switch to accept edits … for this session"). For a **command** ("Yes, and don't ask again for: …") the answer is remembered for this project, not just today. Be slower to say it for commands.
3. **No**, optionally with a note telling Claude what to do instead (Tab to amend, Esc to cancel).

## The rule for you and your team

Read, then answer. If you do not understand what it wants to do, say no and ask it to explain. Asking takes a few seconds. Guessing can cost you a client's files.

## Two other prompts you will meet

- **Workspace trust:** the first time you start Claude Code in a new folder, it asks whether you trust the folder. The highlight starts on "No, exit". Say yes only for your own folder.
- **Plan approval:** after a plan, you choose how the build runs. In the recording the options were auto mode, "manually approve edits", or tell Claude what to change. This episode chose manually approve edits.
