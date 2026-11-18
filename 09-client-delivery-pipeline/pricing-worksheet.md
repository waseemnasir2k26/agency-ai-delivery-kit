# Pricing worksheet: full cost of delivery

**Owner decision:** what is the lowest price at which this job still pays for itself?

A price from a video is a guess, so this sheet has no figures. It is the method from Episode 6 (full cost of
delivery), applied to one client job. Eight rows, and they are not equally solid. Plain-text twin:
`pricing-worksheet.csv`.

| #   | Tag                       | Line                                                      | Value       | Where it comes from                                                                                                                               |
| --- | ------------------------- | --------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **MEASURED**              | AI run cost for this job (list-price estimate)            | \_\_\_\_    | `python pipeline.py summary --job <job>` → `runs/<job>/cost-report.txt`, TOTAL line                                                               |
| 2   | **MEASURE ON A REAL JOB** | Human gate time × your hourly cost                        | your figure | Stopwatch at the four gates on your first real job. The recorded run used a stand-in owner, so its gate minutes are machine pace, not human pace. |
| 3   | OWNER-ENTERED · EXAMPLE   | Human build and fix time                                  | \_\_\_\_    | your records                                                                                                                                      |
| 4   | OWNER-ENTERED · EXAMPLE   | Failed-run allowance                                      | \_\_\_\_    | your assumption: a run can go wrong                                                                                                               |
| 5   | OWNER-ENTERED · EXAMPLE   | Project management, including the wait for client answers | \_\_\_\_    | your records                                                                                                                                      |
| 6   | OWNER-ENTERED · EXAMPLE   | Hosting and integrations                                  | \_\_\_\_    | your records                                                                                                                                      |
| 7   | OWNER-ENTERED · EXAMPLE   | Support                                                   | \_\_\_\_    | your records                                                                                                                                      |
| 8   | OWNER-ENTERED · EXAMPLE   | Overhead                                                  | \_\_\_\_    | your records                                                                                                                                      |
| =   | **FLOOR**                 | FLOOR = full cost of delivery (rows 1-8 added up)         | \_\_\_\_    |                                                                                                                                                   |
| +   | **MARGIN**                | MARGIN (your decision)                                    | \_\_\_\_    | owner decision                                                                                                                                    |

## Read it this way

- The AI run cost is **one row of eight**. "AI run cost + markup" prices below what the job costs you.
- On a subscription login, row 1 is a local estimate at API list price, not a bill. With an API key in its own
  workspace, the Console invoice is the bill.
- One run is one run. Measure a few jobs before you fix a price.
- Project or retainer? See `PROJECT-VS-RETAINER.md`.
