"""For each Shopify shop: how many products get their gender only from the default (the name, brand and tags say nothing),
and how many of those the shop itself lists in men's collections. Usage: gender_probe.py [shop ...]"""
import collections, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from common import get_json
from shopify import SHOPS, WOMEN, MEN, KIDS, _products

def side(c):
    t = (c.get("title") or "") + " " + (c.get("handle") or "")
    m, w = bool(MEN.search(t)), bool(WOMEN.search(t))
    return "men" if m and not w else "women" if w and not m else None

def collection_sets(base):
    cols = []
    for page in range(1, 20):
        try: cs = get_json(f"{base}/collections.json?limit=250&page={page}").get("collections") or []
        except Exception as ex: print("   collections:", ex); break
        if not cs: break
        cols += cs
    found = {"men": set(), "women": set()}
    named = collections.Counter()
    for c in cols:
        s = side(c)
        if not s: continue
        named[s] += 1
        for page in range(1, 40):
            try: ps = get_json(f"{base}/collections/{c['handle']}/products.json?limit=250&page={page}").get("products") or []
            except Exception as ex: print("   ", c["handle"], ex); break
            found[s].update(p["id"] for p in ps)
            if len(ps) < 250: break
            time.sleep(0.25)
        time.sleep(0.25)
    return found, named, len(cols)

done = set()
for sid in sys.argv[1:] or list(SHOPS):
    base = SHOPS[sid]["base"]
    if base in done: continue
    done.add(base)
    ps = [p for p in _products(base, print) if any(v.get("available") for v in p.get("variants", []))]
    ps = [p for p in ps if not KIDS.search(p["title"])]
    silent = [p for p in ps if not any(WOMEN.search(h) or MEN.search(h)
              for h in (p["title"], p.get("vendor") or "", " | ".join(p.get("tags") or [])))]
    found, named, ncols = collection_sets(base)
    men_only = [p for p in silent if p["id"] in found["men"] and p["id"] not in found["women"]]
    women_only = [p for p in silent if p["id"] in found["women"] and p["id"] not in found["men"]]
    both = [p for p in silent if p["id"] in found["men"] and p["id"] in found["women"]]
    print(f"== {sid}: {len(ps)} products, {len(silent)} with no gender in name/brand/tags; "
          f"{ncols} collections ({named['men']} men's, {named['women']} women's); "
          f"of the silent ones: {len(men_only)} men's only, {len(women_only)} women's only, {len(both)} both, "
          f"{len(silent) - len(men_only) - len(women_only) - len(both)} in neither", flush=True)
    for p in men_only[:8]: print("    men:", p["title"], "|", p.get("product_type"), "|", p["handle"])
