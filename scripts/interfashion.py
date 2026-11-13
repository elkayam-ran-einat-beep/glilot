"""Inter Fashion (interfashion.co.il, Shopify): the Israeli online store of Tezenis, Calzedonia and Intimissimi.
Only clothing, leggings and bags are kept; underwear, socks and sleepwear are outside the portal's categories."""
import time
from common import get_json
from classify import classify, color_families
from shopify import KIDS

BASE = "https://interfashion.co.il"
STORE = {"tezenis": "tezenis", "calzedonia": "calzedonia", "intimissimi": "intimissimi"}
SKIP_TYPES = {"הלבשה תחתונה", "פיג'מות והלבשת לילה", "כותנות ובייבידול", "חולצות וגופיות פיג'מה", "בגדי ים", "בגד ים"}
TYPE_FALLBACK = {"תיקים ואקססוריז": None}

def is_men(c):
    t, h = c["title"].lower().replace("women", ""), c["handle"].lower().replace("-women", "")
    return "גבר" in t or "גבר" in h or " men" in " " + t or "-men" in h

def is_women(c):
    return "נשים" in c["title"] or "women" in c["title"].lower() or "women" in c["handle"].lower()

def men_ids(log):
    """Products found only in the site's men's collections. Many men's items (Tezenis basics) never say 'men'
    in their name. Items also listed in a women's collection (unisex) stay with women."""
    cols = []
    for page in range(1, 20):
        try: cs = get_json(f"{BASE}/collections.json?limit=250&page={page}").get("collections") or []
        except Exception as ex: log(f"interfashion collections p{page}: {ex}"); break
        if not cs: break
        cols += cs
    found = {"men": set(), "women": set()}
    for c in cols:
        side = "men" if is_men(c) else "women" if is_women(c) else None
        if not side: continue
        for page in range(1, 20):
            try: ps = get_json(f"{BASE}/collections/{c['handle']}/products.json?limit=250&page={page}").get("products") or []
            except Exception as ex: log(f"interfashion {c['handle']}: {ex}"); break
            found[side].update(p["id"] for p in ps)
            if len(ps) < 250: break
            time.sleep(0.3)
        time.sleep(0.3)
    ids = found["men"] - found["women"]
    log(f"interfashion: {len(found['men'])} products in men's collections, {len(ids)} of them men's only")
    return ids

def collect(log):
    items, seen = [], set()
    men = men_ids(log)
    for page in range(1, 100):
        try: ps = get_json(f"{BASE}/products.json?limit=250&page={page}").get("products") or []
        except Exception as ex: log(f"interfashion p{page}: {ex}"); break
        if not ps: break
        for p in ps:
            if p["id"] in seen: continue
            seen.add(p["id"])
            if p.get("product_type") in SKIP_TYPES: continue
            vs = [v for v in p.get("variants", []) if v.get("available")]
            if not vs: continue
            title = p["title"]
            if KIDS.search(title): continue
            if "יוניסקס" in title: genders = ["women", "men"]
            elif p["id"] in men or any(w in title for w in ("לגבר", "גברים", "לגברים")): genders = ["men"]
            else: genders = ["women"]
            price = min(float(v["price"]) for v in vs)
            old = max(float(v.get("compare_at_price") or 0) for v in vs)
            imgs = [i["src"] for i in p.get("images", [])]
            for g in genders:
                path = classify(title, g)
                if not path: continue
                it = {"s": STORE.get((p.get("vendor") or "").lower(), "tezenis"), "g": g, "p": "/".join(path), "n": title,
                      "pr": price, "c": color_families(title), "cn": "", "img": imgs[0] if imgs else None,
                      "u": f"{BASE}/products/{p['handle']}"}
                if old > price + 0.01: it["old"] = old
                if path == ["bottom","long"]: it["_d"] = p.get("body_html") or ""
                items.append(it)
        time.sleep(0.4)
    log(f"interfashion: {len(seen)} listed, {len(items)} kept")
    return items
