"""Show how Shopify shops mark colour and gender on sample products. Usage: probe.py https://shop.example/ ..."""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from common import get_json
from classify import color_families

for base in sys.argv[1:]:
    base = base.rstrip("/")
    print("=====", base, flush=True)
    ps = []
    for page in (1, 2, 3, 4):
        try: ps += get_json(f"{base}/products.json?limit=250&page={page}").get("products") or []
        except Exception as ex: print("ERR", ex); break
    print("tags", collections.Counter(t for p in ps for t in p.get("tags") or []).most_common(60))
    no = [p for p in ps if not color_families(p["title"])]
    for p in no[:: max(1, len(no) // 8)][:8]:
        body = re.sub(r"<[^>]+>|\s+", " ", p.get("body_html") or "")[:160]
        print("ITEM", p["title"], "|", p.get("vendor"), "|", p["handle"][:50], "|", (p.get("tags") or [])[:14], "|", body, "|", p["variants"][0].get("sku"), flush=True)
