"""Manual GEO scoreboard -> docs/index.html (GitHub Pages).

Renders the manual ChatGPT/Perplexity/Claude/AIO citation checks recorded in
manual/checks.json against the canonical 12 tracked queries (queries.yml) plus
the extended buyer set. Deterministic: every value comes from the data files;
no wall-clock. Stdlib only.
"""
import html, json, re

# --- load -------------------------------------------------------------------
def parse_queries(path: str = "queries.yml") -> list[dict]:
    out, q = [], None
    for line in open(path):
        m = re.match(r'\s*-\s*q:\s*"(.+)"\s*$', line.rstrip("\n"))
        if m:
            q = {"q": m.group(1)}; out.append(q); continue
        m = re.match(r"\s*target:\s*(\S+)\s*$", line)
        if m and q is not None:
            q["target"] = m.group(1)
    return out

CANONICAL = parse_queries()
CHECKS = json.load(open("manual/checks.json"))
CITES = json.load(open("results/citations.json"))
ASSISTANTS: list[str] = CHECKS["assistants"]
EXTENDED: list[str] = CHECKS["extended_queries"]
SESSIONS: list[dict] = sorted(CHECKS["sessions"], key=lambda s: s["date"])

# Latest manual state per (query, assistant): later sessions win.
latest: dict[tuple[str, str], dict] = {}
for s in SESSIONS:
    for r in s.get("results", []):
        latest[(r["q"], r["assistant"])] = {**r, "date": s["date"]}

def q_cited(q: str) -> bool:
    return any(latest.get((q, a), {}).get("cited") for a in ASSISTANTS)

canon_qs = [c["q"] for c in CANONICAL]
canon_cited = sum(q_cited(q) for q in canon_qs)
ext_cited = sum(q_cited(q) for q in EXTENDED)
cells_total = (len(canon_qs) + len(EXTENDED)) * len(ASSISTANTS)
cells_checked = len(latest)
data_through = max([s["date"] for s in SESSIONS] + [CITES.get("last_measured", CITES.get("baseline", ""))])

# --- render -----------------------------------------------------------------
E = html.escape

def cell(q: str, a: str) -> str:
    r = latest.get((q, a))
    if r is None:
        return '<td class="c unchecked"><span class="chip"><span class="dot">·</span>unchecked</span></td>'
    note = E(r.get("notes", "") or "")
    tip = f' title="{E(r["date"])}{" — " + note if note else ""}"'
    if r.get("cited"):
        return f'<td class="c cited"{tip}><span class="chip"><span class="dot">✓</span>cited</span></td>'
    return f'<td class="c nocite"{tip}><span class="chip"><span class="dot">—</span>not cited</span></td>'

def grid(title: str, qs: list[str], targets: dict[str, str] | None = None) -> str:
    head = "".join(f"<th scope=\"col\">{E(a)}</th>" for a in ASSISTANTS)
    rows = []
    for q in qs:
        tgt = (targets or {}).get(q)
        label = f'<a href="{E(tgt)}">{E(q)}</a>' if tgt and tgt != "planned" else E(q)
        rows.append(f'<tr><th scope="row">{label}</th>' + "".join(cell(q, a) for a in ASSISTANTS) + "</tr>")
    return (f'<h2>{E(title)}</h2><div class="scroll"><table><caption class="sr">{E(title)}: manual citation state per query and assistant</caption>'
            f'<thead><tr><th scope="col">Query</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

def tiles() -> str:
    t = [
        (f"{canon_cited} of {len(canon_qs)}", "canonical queries cited by any assistant (latest manual check)"),
        (f"{ext_cited} of {len(EXTENDED)}", "extended buyer queries cited (latest manual check)"),
        (f"{cells_checked} of {cells_total}", "query × assistant cells checked so far"),
        (f'{len(CITES.get("cited", []))} of {len(canon_qs)}', f'automated tracker baseline (measured {E(CITES.get("last_measured", "?"))})'),
    ]
    return '<div class="tiles">' + "".join(f'<div class="tile"><p class="n">{E(v)}</p><p class="l">{E(l)}</p></div>' for v, l in t) + "</div>"

def history() -> str:
    if not SESSIONS:
        return '<h2>Session history</h2><p class="muted">No manual sessions recorded yet — this page is the “before” photo. The first filled session becomes the trend’s first point.</p>'
    rows = []
    for s in SESSIONS:
        qs_cited = len({r["q"] for r in s.get("results", []) if r.get("cited")})
        n = len(s.get("results", []))
        pct = round(100 * qs_cited / max(1, len(canon_qs) + len(EXTENDED)))
        rows.append(f'<li><span class="d">{E(s["date"])}</span><span class="bar" aria-hidden="true"><span style="width:{pct}%"></span></span>'
                    f'<span>{qs_cited} queries cited · {n} cells checked</span></li>')
    return "<h2>Session history</h2><ul class=\"hist\">" + "".join(rows) + "</ul>"

def runsheet() -> str:
    items = "".join(f"<li><code>{E(q)}</code></li>" for q in canon_qs + EXTENDED)
    return (f'<h2>Run sheet</h2><p class="muted">Fresh chat per query, no priming. “Cited” = the answer or its sources name freddyxai or freddyxai.com. '
            f'Record results in <code>manual/checks.json</code>, run <code>python3 dashboard.py</code>, commit.</p>'
            f"<details><summary>The {len(canon_qs) + len(EXTENDED)} queries to paste ({len(canon_qs)} canonical + {len(EXTENDED)} extended)</summary><ol>{items}</ol></details>")

targets = {c["q"]: c.get("target", "") for c in CANONICAL}
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>freddyxai — manual GEO scoreboard</title>
<style>
:root {{ --bg:#ffffff; --ink:#171717; --muted:#6b7280; --line:#e5e7eb; --card:#fafafa;
  --teal:#00d4aa; --good:#15803d; --good-bg:#f0fdf4; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#0a0a0a; --ink:#e5e5e5; --muted:#9ca3af; --line:#262626; --card:#171717;
    --good:#4ade80; --good-bg:#052e16; }} }}
* {{ box-sizing:border-box }} body {{ margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.55 ui-sans-serif,system-ui,sans-serif; padding:2rem 1rem 4rem }}
main {{ max-width:1000px; margin:0 auto }}
h1 {{ font-size:1.5rem; margin:0 }} h2 {{ font-size:1.05rem; margin:2.2rem 0 .6rem }}
.sub,.muted {{ color:var(--muted) }} .sub {{ margin:.3rem 0 0 }}
.mono,code,.n,.d {{ font-family:ui-monospace,Menlo,monospace }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin-top:1.4rem }}
.tile {{ border:1px solid var(--line); border-radius:12px; background:var(--card); padding:14px }}
.tile .n {{ font-size:1.45rem; font-weight:600; margin:0 }} .tile .l {{ margin:.2rem 0 0; font-size:.8rem; color:var(--muted) }}
.legend {{ display:flex; gap:14px; flex-wrap:wrap; margin:1rem 0 0; font-size:.85rem }}
.scroll {{ overflow-x:auto }} table {{ border-collapse:collapse; width:100%; font-size:.85rem }}
caption.sr {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0) }}
th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top }}
tbody th {{ font-weight:500; max-width:380px }} tbody th a {{ color:inherit; text-underline-offset:3px }}
td.c {{ white-space:nowrap }}
.chip {{ display:inline-flex; gap:6px; align-items:center; border-radius:999px; padding:2px 10px; border:1px solid var(--line); color:var(--muted) }}
.cited .chip {{ color:var(--good); background:var(--good-bg); border-color:transparent; font-weight:600 }}
.unchecked .chip {{ border-style:dashed }}
.hist {{ list-style:none; padding:0; margin:0 }} .hist li {{ display:flex; gap:12px; align-items:center; padding:6px 0; border-bottom:1px solid var(--line) }}
.bar {{ flex:0 0 140px; height:8px; border-radius:4px; background:var(--line); overflow:hidden }}
.bar span {{ display:block; height:100%; background:var(--teal) }}
footer {{ margin-top:3rem; font-size:.8rem; color:var(--muted); border-top:1px solid var(--line); padding-top:1rem }}
footer a {{ color:inherit }}
details {{ border:1px solid var(--line); border-radius:10px; padding:10px 14px; background:var(--card) }}
summary {{ cursor:pointer }}
</style></head><body><main>
<h1>freddyxai — manual GEO scoreboard</h1>
<p class="sub">Do AI assistants cite <span class="mono">freddyxai</span> for buyer-intent queries? Hand-checked, recorded append-only, rendered from data. Data through <span class="mono">{E(data_through)}</span>.</p>
{tiles()}
<div class="legend"><span class="chip" style="color:var(--good);background:var(--good-bg);border-color:transparent"><span class="dot">✓</span>cited</span>
<span class="chip"><span class="dot">—</span>checked, not cited</span>
<span class="chip" style="border-style:dashed"><span class="dot">·</span>unchecked</span></div>
{grid("Canonical 12 (the tracked baseline)", canon_qs, targets)}
{grid("Extended buyer queries (monthly check set)", EXTENDED)}
{history()}
{runsheet()}
<footer><p><strong>Method.</strong> Manual protocol: each query pasted into each assistant in a fresh chat, no priming; “cited” means the answer or its cited sources name freddyxai or freddyxai.com. Sessions are append-only in <a href="https://github.com/freddylearnsai/freddyxai-weekly/blob/main/manual/checks.json">manual/checks.json</a>; unchecked cells are shown as unchecked, never assumed. The automated tracker’s state lives in <a href="https://github.com/freddylearnsai/freddyxai-weekly/blob/main/results/citations.json">results/citations.json</a> ({E(CITES.get("note", ""))})</p>
<p>Built in public by <a href="https://freddyxai.com">freddyxai</a> — your data team, on demand. Repo: <a href="https://github.com/freddylearnsai/freddyxai-weekly">freddylearnsai/freddyxai-weekly</a>.</p></footer>
</main></body></html>
"""

with open("docs/index.html", "w") as f:
    f.write(page)
print(json.dumps({"canonical_cited": canon_cited, "extended_cited": ext_cited,
                  "cells_checked": cells_checked, "cells_total": cells_total,
                  "sessions": len(SESSIONS), "data_through": data_through, "out": "docs/index.html"}))
