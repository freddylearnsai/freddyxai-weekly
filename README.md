# freddyxai-weekly

freddyxai's own weekly metrics report, generated and committed automatically — live site stats plus the canonical 12-query GEO tracker. Built in public by [freddyxai](https://freddyxai.com/work-with-me).

**Receipts:** see [receipts.md](receipts.md) — every number measured, honest labels included. The report regenerates every Monday 07:00 UTC via GitHub Actions — see [the workflow](.github/workflows/weekly.yml) and [run history](https://github.com/freddylearnsai/freddyxai-weekly/actions).

Built by [freddyxai](https://freddyxai.com) — your data team, on demand. This is the shape of a [$1,000–$2,000 automation build](https://freddyxai.com/work-with-me): a report that writes itself, every Monday, for $0/month.

## The tracker

`queries.yml` is the canonical list of 12 buyer-intent queries freddyxai tracks for AI citations. It supersedes the informal June baseline list (which was counted, not published); citation status is re-baselined here at **0 of 12**, consistent with [the June baseline](https://freddyxai.com/blog/ranking-and-getting-cited-baseline). Re-measurements update `results/citations.json` deliberately — the weekly cron reports state; it does not query AI models.

## Reproduce

```bash
python3 report.py   # writes reports/<ISO-week>.md from live site + tracker data
```

## Manual scoreboard (the ~10-minute monthly routine)

The automated tracker can't sit inside ChatGPT/Perplexity/Claude — you can. Once a month:

1. Open the [scoreboard](https://freddylearnsai.github.io/freddyxai-weekly/) and expand the run sheet.
2. Paste each query into each assistant in a **fresh chat**, no priming. "Cited" = the answer or its sources name freddyxai / freddyxai.com.
3. Append one session to `manual/checks.json` (never edit past sessions).
4. `python3 dashboard.py`, commit, push. Monday's cron also re-renders the page.

Unchecked cells render as unchecked — the dashboard never assumes a result.
