"""Look at Shopify shops from the server: how big they are and how they mark gender, type and colour.
Usage: probe.py https://shop.example/ ...  Prints a short report to the run log."""
import collections, json, re, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_json
from classify import classify, color_families

WOMEN = re.compile(r"נשים|לאישה|women|woman|ladies", re.I)
MEN = re.compile(r"גברים|לגבר|\bmen\b|\bman\b|\bmens\b", re.I)

for base in sys.argv[1:]:
    base = base.rstrip("/")
    print("=====", base, flush=True)
    try:
        ps, page = [], 1
        while page <= 40:
            batch = get_json(f"{base}/products.json?limit=250&page={page}").get("products") or []
            if not batch: break
            ps += batch; page += 1; time.sleep(0.4)
    except Exception as ex:
        print("ERR", ex, "after", len(ps))
    avail = [p for p in ps if any(v.get("available") for v in p.get("variants", []))]
    print("products", len(ps), "available", len(avail))
    print("types", collections.Counter(p.get("product_type") for p in avail).most_common(14))
    print("vendors", collections.Counter(p.get("vendor") for p in avail).most_common(6))
    print("options", collections.Counter(o.get("name") for p in avail for o in p.get("options", [])).most_common(6))
    tags = collections.Counter(t for p in avail for t in (p.get("tags") or []))
    print("gender tags", [(t, n) for t, n in tags.most_common(400) if WOMEN.search(t) or MEN.search(t)][:10])
    print("gender in title w/m", sum(bool(WOMEN.search(p["title"])) for p in avail), sum(bool(MEN.search(p["title"])) for p in avail))
    kept = [p for p in avail if classify(p["title"], "women")]
    print("classified from title", len(kept), "of", len(avail))
    print("unclassified", [p["title"][:30] for p in avail if not classify(p["title"], "women")][:8])
    print("sample", [p["title"][:36] for p in avail[:6]])
    print("images per product", collections.Counter(len(p.get("images", [])) for p in avail).most_common(4))
    if avail:
        print("image urls", [i["src"].split("?")[0] for i in avail[len(avail)//2].get("images", [])][:5])
        print("price sample", sorted(float(p["variants"][0]["price"]) for p in avail)[len(avail)//2])
    print(flush=True)
