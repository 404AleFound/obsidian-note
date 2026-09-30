import json, time, urllib.parse, urllib.request, sys, os

OUT = r"D:\19816\obsidian-note\.claude\tmp_openalex_top.json"
QUERIES = [
    "sewer pipe defect detection",
    "pipeline inspection defect detection deep learning",
    "sewer CCTV automated condition assessment",
    "drainage pipe defect detection robot",
]

def fetch(q, retries=4):
    url = ("https://api.openalex.org/works?mailto=research@example.com&search="
           + urllib.parse.quote(q) + "&sort=cited_by_count:desc&per-page=40")
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script mailto:research@example.com"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            code = getattr(e, "code", None)
            wait = 15 if code == 429 else 4
            print(f"  retry {q} (err {e}) sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
    return None

rows, seen = [], {}
time.sleep(3)
for q in QUERIES:
    print(f"fetch: {q}", file=sys.stderr)
    data = fetch(q)
    if not data or not data.get("results"):
        print(f"  -> nothing for {q}", file=sys.stderr)
        continue
    for w in data["results"]:
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        key = doi or w.get("id", "")
        if not key or key in seen:
            continue
        seen[key] = 1
        authors = ", ".join(a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])[:3])
        rows.append({
            "title": w.get("title", ""),
            "year": w.get("publication_year"),
            "doi": doi,
            "cites": w.get("cited_by_count", 0),
            "authors": authors,
        })
    time.sleep(2.5)

rows.sort(key=lambda r: r["cites"], reverse=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows[:90], f, ensure_ascii=False, indent=1)
print(f"saved {len(rows)} rows -> {OUT}")
