"""Inter Fashion (interfashion.co.il, Shopify): the Israeli online store of Tezenis, Calzedonia and Intimissimi.
Only clothing, leggings and bags are kept; underwear, socks and sleepwear are outside the portal's categories."""
import time
from common import get_json
from classify import classify, color_families

BASE = "https://interfashion.co.il"
STORE = {"tezenis": "tezenis", "calzedonia": "calzedonia", "intimissimi": "intimissimi"}
SKIP_TYPES = {"הלבשה תחתונה", "פיג'מות והלבשת לילה", "כותנות ובייבידול", "חולצות וגופיות פיג'מה", "בגדי ים", "בגד ים"}
TYPE_FALLBACK = {"תיקים ואקססוריז": None}

def collect(log):
    items, seen = [], set()
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
            g = "men" if any(w in title for w in ("לגבר", "גברים", "לגברים")) else "women"
            path = classify(title, g)
            if not path: continue
            price = min(float(v["price"]) for v in vs)
            old = max(float(v.get("compare_at_price") or 0) for v in vs)
            imgs = [i["src"] for i in p.get("images", [])]
            it = {"s": STORE.get((p.get("vendor") or "").lower(), "tezenis"), "g": g, "p": "/".join(path), "n": title,
                  "pr": price, "c": color_families(title), "cn": "", "img": imgs[0] if imgs else None,
                  "u": f"{BASE}/products/{p['handle']}"}
            if old > price + 0.01: it["old"] = old
            if path == ["bottom","long"]: it["_d"] = p.get("body_html") or ""
            items.append(it)
        time.sleep(0.4)
    log(f"interfashion: {len(seen)} listed, {len(items)} kept")
    return items
