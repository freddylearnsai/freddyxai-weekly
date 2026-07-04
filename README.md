# freddyxai-weekly

freddyxai's own weekly metrics report, generated and committed automatically — live site stats plus the canonical 12-query GEO tracker. Built in public by [freddyxai](https://freddyxai.com/work-with-me).

Status: build in progress. Receipts land in `receipts.md` when the first run completes.

## The tracker

`queries.yml` is the canonical list of 12 buyer-intent queries freddyxai tracks for AI citations. It supersedes the informal June baseline list (which was counted, not published); citation status is re-baselined here at **0 of 12**, consistent with [the June baseline](https://freddyxai.com/blog/ranking-and-getting-cited-baseline). Re-measurements update `results/citations.json` deliberately — the weekly cron reports state; it does not query AI models.

## Reproduce

```bash
python3 report.py   # writes reports/<ISO-week>.md from live site + tracker data
```
