# Receipts — freddyxai weekly report automation

| Receipt | Value |
| --- | --- |
| Step-by-step assembly without the script (agent-performed, timed) | 48 s |
| Scripted run (local) | 1.2–2.2 s (two measured runs) |
| First scheduled run (GitHub Actions) | success · 16 s · https://github.com/freddylearnsai/freddyxai-weekly/actions/runs/28691582470 |
| Cadence | every Monday 07:00 UTC (cron "0 7 * * 1") |
| Monthly infrastructure cost | $0 |

Note: the step-by-step baseline was performed by an AI agent executing each step individually — no loops, no scripted counting — so it bounds the mechanical floor, not human minutes. A person doing the same by hand would take longer; we publish only what was measured.
