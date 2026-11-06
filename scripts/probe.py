"""Print every photo of a few products per Shopify shop, to see which photo shows the item alone.
Usage: probe.py https://shop.example/ ...  Lines start with IMGS, then the shop, then the photo addresses."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get_json

for base in sys.argv[1:]:
    base = base.rstrip("/")
    try: ps = get_json(f"{base}/products.json?limit=250&page=1").get("products") or []
    except Exception as ex: print("ERR", base, ex); continue
    ps = [p for p in ps if len(p.get("images", [])) >= 2]
    for p in ps[len(ps) // 3 :: max(1, len(ps) // 3)][:3]:
        print("IMGS", json.dumps({"shop": base, "imgs": [i["src"].split("?")[0] for i in p["images"]]}), flush=True)
