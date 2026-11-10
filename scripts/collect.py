"""Collect items from each store into glilot/data/<store>.json.
Usage: python collect.py [store ...]   (default: every store)"""
import json, os, sys, collections, datetime, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cuts import refine
from shopify import SHOPS, Shop
OUT = os.environ.get("GLILOT_OUT") or os.path.join(HERE, "..", "data")
STORES = {"zara": "זארה", "golf": "גולף", "castro": "קסטרו", "crazyline": "קרייזי ליין", "massimodutti": "מסימו דוטי",
          "factory54": "פקטורי 54", "interfashion": "אינטרפאשן", "shoofra": "שופרא",
          "delta": "דלתא", "emanuelwear": "עמנואל", "emanuel": "עמנואל", "topten": "טופ טן",
          "pullandbear": "פול אנד בר", "stradivarius": "סטרדיבריוס", "oysho": "אוישו",
          **{k: v["name"] for k, v in SHOPS.items()}}
# labels for store ids that a module emits besides its own (Factory 54 carries brands that have their own Glilot store)
NAMES = {"tommy": "טומי הילפיגר", "ralph": "ראלף לורן", "ck": "קלווין קליין", "lacoste": "לקוסט",
         "tezenis": "טזניס", "calzedonia": "קלצדוניה", "intimissimi": "אינטימיסימי"}

# Which group each shop opens under in the portal
TIERS = {"zara": "chains", "golf": "chains", "castro": "chains", "crazyline": "chains", "interfashion": "chains",
         "massimodutti": "high", "factory54": "high", "shoofra": "shoes",
         "delta": "afford", "emanuelwear": "high", "emanuel": "shoes", "topten": "shoes",
         "pullandbear": "afford", "stradivarius": "afford", "oysho": "chains",
         **{k: v["tier"] for k, v in SHOPS.items()}}

def log(m): print(m, flush=True)

def main(names):
    os.makedirs(OUT, exist_ok=True)
    idx_path = os.path.join(OUT, "index.json")
    index = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else {"stores": {}}
    for s in names:
        try:
            module = Shop(s) if s in SHOPS else importlib.import_module(s)
            items = module.collect(log)
            refine(items, module, s, OUT, log)
        except Exception as ex:
            log(f"!! {s} failed: {ex}"); continue
        path = os.path.join(OUT, f"{s}.json")
        prev = index["stores"].get(s, {}).get("count", 0)
        if len(items) < max(20, prev * 0.5) and s not in os.environ.get("GLILOT_FORCE", "").split():
            log(f"!! {s}: only {len(items)} items (previously {prev}), keeping old file"); continue
        with open(path, "w", encoding="utf-8") as f: json.dump(items, f, ensure_ascii=False, separators=(",",":"))
        index["stores"][s] = {"name": STORES[s], "count": len(items),
                              "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}
        flat = sum(1 for i in items if i.get("img2"))
        log(f"   white-background images: {flat} of {len(items)}; by store label: {dict(collections.Counter(i['s'] for i in items))}")
        cnt = collections.Counter((i["g"], i["p"]) for i in items)
        log(f"== {s}: {len(items)} items")
        for k, v in sorted(cnt.items()): log(f"   {k[0]:6} {k[1]:24} {v}")
        nocol = [i for i in items if not i["c"]]
        log(f"   no colour: {len(nocol)} e.g. {[i['cn'] for i in nocol[:8]]}")
    index["names"] = {**{k: v for k, v in STORES.items()}, **NAMES}
    index["tiers"] = TIERS
    json.dump(index, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1:] or list(STORES))
