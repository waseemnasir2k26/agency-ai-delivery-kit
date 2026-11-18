# Pricing floor worksheet · full cost of delivery

Cost is not price. The AI run cost is only the **AI run cost floor**. The job floor is the full cost of delivery.
Green = measured · Blue = you enter from your own records · Yellow = assumption, labelled as one. No prices filled in.

| colour | line | value | source |
|---|---|---|---|
| GREEN / MEASURED | AI run cost per job (top of range, setup C) | $0.1013 (est., 3 runs) | from cost_report.py |
| GREEN / MEASURED | Human review time per job (minutes, stopwatch) | NOT MEASURED (time one review) | stopwatch |
| BLUE / OWNER-ENTERED | Human build time per job (minutes) |  | your records |
| BLUE / OWNER-ENTERED | Your hourly cost (PKR or USD per hour) |  | your records |
| BLUE / OWNER-ENTERED | Project management per job |  | your records |
| BLUE / OWNER-ENTERED | Hosting and integrations per job |  | your records |
| BLUE / OWNER-ENTERED | Support per job |  | your records |
| YELLOW / ASSUMPTION | Failed-run and capped-run allowance |  | your assumption |
| YELLOW / ASSUMPTION | Overhead share per job |  | your assumption |
| YELLOW / ASSUMPTION | Margin |  | your assumption |
| - | AI run cost floor (not the job floor) | = AI run cost per job | - |
| - | **FULL COST OF DELIVERY = FLOOR** | = AI run cost + (review + build minutes / 60 x hourly cost) + PM + hosting + support + allowance + overhead, then margin | - |

Value check (no figures): hours the job took by hand x your rate = what it is worth. Price on the hours it saves, then check price >= full floor.

> **LOCAL ESTIMATE AT API LIST PRICE - NOT A BILL.** These runs used a subscription login: Claude Code computes the dollar figure on this machine from token counts at list price. It is not what you were charged. For cost-per-job numbers you can show a client, re-run with an API key in its own workspace.
