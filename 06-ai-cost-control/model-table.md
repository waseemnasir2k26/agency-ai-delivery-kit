# Model table: which model does which step

One page. One row per step of the job. Pick each model by the step's **role**, not by its name, and write the
choice into the files (one `model:` line and one `effort:` line per agent in `.claude/agents/<step>.md`).

**Effort** is how long the model thinks before it acts. Thinking is billed as output tokens, so simple steps get
low effort and the judge keeps high. Accepted effort values depend on the model and the provider: check the
Claude Code model-config docs for your tier, and re-check after every Claude Code update.

## Kiran Studio example (monthly site refresh, Setup C in the episode)

| Step                         | Model                                         | Effort   | Why                                                                                     |
| ---------------------------- | --------------------------------------------- | -------- | --------------------------------------------------------------------------------------- |
| Read the request + data file | Haiku                                         | low      | reads two small files, decides nothing                                                  |
| Build the change             | Sonnet                                        | medium   | real edits, checked afterwards by the checker and the critic                            |
| **Critic (the judge)**       | **the top tier you run** (Opus on this build) | **high** | **FIXED ROW: never downgrade the judge.** The last check before a client sees the page. |
| Write the report             | Haiku                                         | low      | summarises facts it was given                                                           |

Where it lives in the kit: `kiran-sites/.claude/agents/reader.md`, `builder.md`, `critic.md`, `reporter.md`
(frontmatter `model:` and `effort:`). `run_job.py` rewrites those two lines from `setups/<setup>.json` before
every run, so each setup is measured from the same starting point.

### Why the judge row is fixed

In the recorded runs, the all-Haiku setup (judge on Haiku too) caught the planted wrong price every time it reached
the page (2 of 2), and in the third run there was nothing to catch. That is three runs, not proof. The most you
save by downgrading the judge is the judge step's own cost; the other side of the bet is one wrong price on a
client's live site. So the rule does not depend on a lucky streak: **the judge is the top tier you run.**

Pick the judge by role, not by name. If a more capable model family is available to you, the judge moves up to it
first.

---

## Blank copy (fill in for your own job)

Job: **********\_\_********** · Owner of this table: **********\_\_**********

| Step               | Model                    | Effort   | Why                                      |
| ------------------ | ------------------------ | -------- | ---------------------------------------- |
|                    |                          |          |                                          |
|                    |                          |          |                                          |
|                    |                          |          |                                          |
| **Judge / critic** | **the top tier you run** | **high** | **FIXED ROW: never downgrade the judge** |
|                    |                          |          |                                          |

Before you lower a model on any step, run the job a few times on that setup with a planted mistake
(see `QUALITY-VS-COST-REVIEW.md`) and keep the result beside the cost range.
