# About `settings.json` in this folder

JSON files cannot hold comments, so the note for `settings.json` lives here.

```json
{
  "permissions": {
    "defaultMode": "default"
  }
}
```

This pins the project's starting permission mode to **Manual** (`"default"`): Claude asks before it edits a file or runs a command.

Interactive sessions may otherwise start in auto mode, depending on your Claude Code version and settings. Remove this line once you have decided auto mode is right for this project.

The bottom line of the Claude Code screen always shows the current mode. Mode names and the starting mode can change between Claude Code releases, so re-check against the official docs after each update: https://code.claude.com/docs
