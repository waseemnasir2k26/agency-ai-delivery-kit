# Activity record (OpenTelemetry) — setup and the detail logging decision

Layer four: the logbook. Claude Code reports through OpenTelemetry, a standard way for software to say what it did. When a tool runs, or a hook or a person turns one down, it writes one line: which tool, accepted or rejected, and what decided.

**This is an activity record, not a complete audit trail.** Not every refusal shows up in it.

## 1. Turn it on (managed file `env` block)

```json
"env": {
  "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
  "OTEL_LOGS_EXPORTER": "otlp",
  "OTEL_METRICS_EXPORTER": "otlp",
  "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json",
  "OTEL_EXPORTER_OTLP_ENDPOINT": "http://<collector>:4318",
  "OTEL_LOGS_EXPORT_INTERVAL": "1000",
  "OTEL_RESOURCE_ATTRIBUTES": "team.id=<org>,seat=freelancer-1"
}
```

`seat=` names the laptop, so you can tell seats apart without collecting emails. `grpc` on `:4317` works too; keep the protocol and port matched to your collector.

## 2. Run a collector

- **One machine, no install (what the lab used):** `python3 lab/otel_sink.py` listens on `127.0.0.1:4318` and appends each log record as one flat JSON line to `OTEL_SINK_OUT` (default `/tmp/otel_events.jsonl`). Logs only, no metrics.
- **A team collector:** OpenTelemetry Collector (contrib build) with `otel/collector-config.yaml`: `otelcol-contrib --config otel/collector-config.yaml`. It prints to the console and writes `claude-code-activity.jsonl` with rotation. Not run on the build; check it with `otelcol-contrib validate --config otel/collector-config.yaml` before use.

Watch it live: `tail -f /tmp/otel_events.jsonl` (lab) or the collector's console.

## 3. What is recorded by default (seen in our runs)

| Event                                   | What it says                                                                                                                                       |
| :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| `claude_code.tool_decision`             | tool name, `decision` (`accept` / `reject`), `source` (`config` = a rule or a person's prompt answer, `hook` = a hook blocked it), permission mode |
| `claude_code.tool_result`               | that a tool ran and whether it succeeded (not its output)                                                                                          |
| `claude_code.permission_mode_changed`   | mode switches, e.g. the policy gate turning down auto mode (`trigger: auto_gate_denied`)                                                           |
| `claude_code.managed_settings_resolved` | the managed settings were read                                                                                                                     |
| resource                                | `team.id`, `seat`, `service.name`, `service.version`                                                                                               |

## 4. What is left out

- **Some refusals.** A Read-tool deny on `.env` wrote **no** event in our runs. A sandbox network block was logged as a Bash `accept` plus a successful `tool_result`. No `claude_code.safety_event` appeared in any run. Hook rejections and prompt refusals do appear.
- **Command text, tool input and MCP tool names** — only with `OTEL_LOG_TOOL_DETAILS=1`.
- **Tool output** (what a file or command returned) — only with `OTEL_LOG_TOOL_CONTENT=1`, which needs tracing (`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` + `OTEL_TRACES_EXPORTER`), a beta feature.
- **Prompt text** — only with `OTEL_LOG_USER_PROMPTS=1`.

All three switches are **off** in this pack. Turning one on means storing what your team types and what client files contain. That is a privacy decision: use the form below first.

## 5. Detail logging decision (one page, fill in before any switch goes on)

| Question                                                                                    | Answer |
| :------------------------------------------------------------------------------------------ | :----- |
| Which switch? (`OTEL_LOG_TOOL_DETAILS` / `OTEL_LOG_TOOL_CONTENT` / `OTEL_LOG_USER_PROMPTS`) |        |
| Who asked for it? (name, role, client if a client asked)                                    |        |
| Why? What question will the extra detail answer that the default record cannot?             |        |
| Which seats and which client projects?                                                      |        |
| Where is it stored? (host, folder, encrypted at rest yes/no)                                |        |
| Who may read it? (names)                                                                    |        |
| How long is it kept? When and how is it deleted?                                            |        |
| Does any client contract or data-protection rule forbid it? (checked by whom)               |        |
| Are the freelancers told, in writing?                                                       |        |
| Decision (yes / no), by the policy owner, and review date                                   |        |
