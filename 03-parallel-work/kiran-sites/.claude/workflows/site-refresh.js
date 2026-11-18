export const meta = {
  name: "site-refresh",
  description:
    "Weekly site refresh: research, build in an isolated worktree per client, critic (max 2 rounds), one report. Run with a date, e.g. /site-refresh with date YYYY-MM-DD (the Monday of the refresh)",
  phases: [
    {
      title: "Setup",
      detail: "haiku: one git worktree per client",
      model: "haiku",
    },
    {
      title: "Research",
      detail: "haiku: exact changes as JSON",
      model: "haiku",
    },
    {
      title: "Build",
      detail: "sonnet applies changes in its own worktree",
      model: "sonnet",
    },
    {
      title: "Critic",
      detail: "opus read-only, same worktree, runs check-site.py",
      model: "opus",
    },
    {
      title: "Report",
      detail: "haiku writes reports/<date>-refresh.md",
      model: "haiku",
    },
  ],
};

// Kiran Studio saved workflow (Episode 3). Four working phases: research, build, critic, report
// (plus a setup step that makes one git worktree per client, so the saved workflow needs no prep).
// Run it: /site-refresh with date YYYY-MM-DD
//
// Availability: dynamic workflows depend on your plan and Claude Code release. When we recorded,
// the docs said they are available on paid plans and with Anthropic API access, and on Pro you
// turn them on from the "Dynamic workflows" row in /config. Check /config and the workflows docs
// page (code.claude.com/docs/en/workflows) before you rely on it.
// Size: the size guideline is advice, not a cap. Default "medium" aims for fewer than 10 agents
// ("small", fewer than 5, on Pro). This workflow starts about 16-17 agents for three clients, so
// set "workflowSizeGuideline": "large" (fewer than 50) in .claude/settings.json.

// The date comes in through args: Date.now(), Math.random() and new Date() throw in workflow scripts.
const rawDate = typeof args === "string" ? args : args && args.date;
// args can arrive as the whole phrase ("with date YYYY-MM-DD"), so pull out the YYYY-MM-DD part.
const date = rawDate && (String(rawDate).match(/\d{4}-\d{2}-\d{2}/) || [])[0];
if (!date)
  throw new Error(
    "site-refresh needs a date, e.g. Run /site-refresh with date YYYY-MM-DD",
  );

const SETUP = {
  type: "object",
  required: ["main", "clients"],
  properties: {
    main: { type: "string" },
    clients: {
      type: "array",
      items: {
        type: "object",
        required: ["name", "path"],
        properties: { name: { type: "string" }, path: { type: "string" } },
      },
    },
  },
};
const CHANGES = {
  type: "object",
  required: ["changes"],
  properties: {
    changes: {
      type: "array",
      items: {
        type: "object",
        required: ["file", "to"],
        properties: {
          file: { type: "string" },
          field: { type: "string" },
          from: { type: "string" },
          to: { type: "string" },
          note: { type: "string" },
        },
      },
    },
  },
};
const BUILD = {
  type: "object",
  required: ["filesChanged", "summary"],
  properties: {
    filesChanged: { type: "array", items: { type: "string" } },
    summary: { type: "string" },
  },
};
const VERDICT = {
  type: "object",
  required: ["verdict", "problems"],
  properties: {
    verdict: { type: "string", enum: ["APPROVED", "REJECTED"] },
    problems: { type: "array", items: { type: "string" } },
  },
};

phase("Setup");
const setup = await agent(
  `In the current project checkout (run git rev-parse --show-toplevel; call it MAIN), create one git worktree per client. Clients = the file names in MAIN/data/*.json without .json. For each client: git worktree add -b refresh/${date}-<client> <MAIN>-refresh/${date}/<client> HEAD. Use forward slashes in returned paths. Do not edit any file. Return { main: MAIN, clients: [{name, path}] }.`,
  { label: "setup", phase: "Setup", model: "haiku", schema: SETUP },
);
const MAIN = setup.main;

const results = await pipeline(
  setup.clients,
  (c) =>
    agent(
      `Read ${MAIN}/requests/${c.name}.md and ${MAIN}/data/${c.name}.json (read-only). Return the exact changes needed for the ${date} site refresh as JSON: each change = file (repo-relative), field, from, to, note. Do not edit anything.`,
      {
        label: `research:${c.name}`,
        phase: "Research",
        model: "haiku",
        schema: CHANGES,
      },
    ),
  async (research, c) => {
    let problems = [],
      rounds = 0,
      verdict = "REJECTED",
      build = null;
    while (rounds < 2 && verdict !== "APPROVED") {
      rounds++;
      build = await agent(
        `Your isolated git worktree is ${c.path} (branch refresh/${date}-${c.name}). Work ONLY inside it; never touch ${MAIN}. Apply these changes for ${c.name}:\n${JSON.stringify(research.changes, null, 1)}\n${problems.length ? `\nA reviewer rejected the previous round with these problems; fix them:\n- ${problems.join("\n- ")}\n` : ""}\nDo NOT run scripts/check-site.py and do NOT read checks.md. Leave edits in the worktree. Return files changed and a one-line summary.`,
        {
          label: `build:${c.name}#${rounds}`,
          phase: "Build",
          model: "sonnet",
          schema: BUILD,
        },
      );
      const v = await agent(
        `You are a strict, read-only critic. Work in ${c.path} (the builder's worktree). Do NOT edit any file. Run \`python scripts/check-site.py ${c.name}\` from that directory, read checks.md there, and inspect the changes (git diff) against requests/${c.name}.md. FAIL by default: APPROVED only if the script passes AND every item in checks.md is satisfied AND the request is fully met. Return { verdict, problems[] } with concrete problems.`,
        {
          label: `critic:${c.name}#${rounds}`,
          phase: "Critic",
          model: "opus",
          schema: VERDICT,
        },
      );
      verdict = v ? v.verdict : "REJECTED";
      problems = v ? v.problems : ["critic failed to return"];
    }
    return {
      client: c.name,
      verdict,
      rounds,
      path: c.path,
      summary: build ? build.summary : "build failed",
      files: build ? build.filesChanged : [],
      problems: verdict === "APPROVED" ? [] : problems,
    };
  },
);

const rows = results.map(
  (r, i) =>
    r || {
      client: setup.clients[i].name,
      verdict: "REJECTED",
      rounds: 0,
      path: setup.clients[i].path,
      summary: "pipeline error",
      files: [],
      problems: ["stage threw"],
    },
);
phase("Report");
await agent(
  `Write ${MAIN}/reports/${date}-refresh.md (create the reports dir; this is the ONLY file you write in the main checkout). Markdown: title, then a table with one row per client: Client | Verdict | Rounds | What changed | Worktree path. Follow with any unresolved problems per rejected client. Data:\n${JSON.stringify(rows, null, 1)}`,
  { label: "report", phase: "Report", model: "haiku" },
);
return rows;
