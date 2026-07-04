"""freddyxai weekly report: live site stats + 12-query GEO tracker → reports/<ISO-week>.md."""
import datetime as dt, json, re, time, urllib.request

SITEMAP = "https://freddyxai.com/sitemap.xml"
UA = {"User-Agent": "freddyxai-weekly/1.0 (+https://github.com/freddylearnsai/freddyxai-weekly)"}

def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""

def parse_queries(path: str = "queries.yml") -> list[dict]:
    out, q = [], None
    for line in open(path):
        line = line.rstrip("\n")
        m = re.match(r'\s*-\s*q:\s*"(.+)"\s*$', line)
        if m:
            q = {"q": m.group(1)}; out.append(q); continue
        m = re.match(r"\s*target:\s*(\S+)\s*$", line)
        if m and q is not None:
            q["target"] = m.group(1)
    return out

def main() -> None:
    t0 = time.time()
    status, xml = fetch(SITEMAP)
    if status != 200:
        raise SystemExit(f"sitemap fetch failed ({status}) — aborting, do not fabricate")
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    projects = [u for u in urls if "/work/" in u]
    posts = [u for u in urls if "/blog/" in u]
    queries = parse_queries()
    cites = json.load(open("results/citations.json"))
    cited = set(cites.get("cited", []))
    rows, live = [], 0
    for item in queries:
        tgt = item["target"]
        if tgt == "planned":
            state = "planned"
        else:
            code, _ = fetch(tgt)
            state = "live" if code == 200 else f"DOWN ({code})"
            live += 1 if code == 200 else 0
        rows.append((item["q"], tgt, state, "cited" if item["q"] in cited else "not cited"))
    week = dt.date.today().isocalendar()
    stamp = f"{week.year}-W{week.week:02d}"
    secs = round(time.time() - t0, 1)
    lines = [f"# freddyxai weekly report — {stamp}", "",
             f"Generated automatically in {secs} s. Source: live sitemap + tracker data.", "",
             "## Site", "",
             f"- Projects live: **{len(projects)}**",
             f"- Posts live: **{len(posts)}**",
             f"- Total routes in sitemap: **{len(urls)}**", "",
             "## GEO tracker (canonical 12)", "",
             f"Citations: **{len(cited)} of {len(queries)}** (last measured {cites['last_measured']}) · Target pages live: **{live}**", "",
             "| Query | Target | Page | Citation |", "| --- | --- | --- | --- |"]
    lines += [f"| {q} | {t} | {s} | {c} |" for q, t, s, c in rows]
    lines.append("")
    open(f"reports/{stamp}.md", "w").write("\n".join(lines))
    print(json.dumps({"week": stamp, "projects": len(projects), "posts": len(posts),
                      "targets_live": live, "citations": len(cited), "seconds": secs}))

if __name__ == "__main__":
    main()
