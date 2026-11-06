"""Factory 54 (Shopify). Also the Israeli online home of Tommy Hilfiger, Ralph Lauren, Calvin Klein and Lacoste,
which get their own store label so they can be filtered like the other Glilot stores."""
import time
from common import get_json
from classify import classify, color_families

BASE = "https://www.factory54.co.il"
BRAND_STORE = {"TOMMY HILFIGER": "tommy", "TOMMY JEANS": "tommy", "POLO RALPH LAUREN": "ralph", "RALPH LAUREN": "ralph",
               "LAUREN RALPH LAUREN": "ralph", "CALVIN KLEIN": "ck", "CALVIN KLEIN JEANS": "ck", "LACOSTE": "lacoste"}
NAMES = {"factory54": "פקטורי 54", "tommy": "טומי הילפיגר", "ralph": "ראלף לורן", "ck": "קלווין קליין", "lacoste": "לקוסט"}
TYPE_FALLBACK = {"נעליים": ["shoes"], "תיקים": ["acc","bag"]}
SKIP_TYPES = {"ביוטי", "הלבשה תחתונה", "גיפט קארד", "בית"}

def images(p):
    srcs = [i["src"] for i in p.get("images", [])]
    look = next((u for u in srcs if "_L_" in u), None)
    flat = next((u for u in srcs if "_P_" in u), None)
    main = look or (srcs[0] if srcs else None)
    return main, (flat if flat and flat != main else None)

def collect(log):
    items, seen = [], set()
    for g, handle in (("women", "women"), ("men", "men")):
        n = 0
        for page in range(1, 200):
            try: d = get_json(f"{BASE}/collections/{handle}/products.json?limit=250&page={page}")
            except Exception as ex: log(f"factory54 {handle} p{page}: {ex}"); break
            ps = d.get("products") or []
            if not ps: break
            for p in ps:
                if p["id"] in seen: continue
                seen.add(p["id"]); n += 1
                if p.get("product_type") in SKIP_TYPES or p.get("vendor") == "GIFT CARD": continue
                vs = [v for v in p.get("variants", []) if v.get("available")]
                if not vs: continue
                path = classify(p["title"], g) or TYPE_FALLBACK.get(p.get("product_type"))
                if not path: continue
                opts = [o.get("name","") for o in p.get("options", [])]
                ci = next((i for i, o in enumerate(opts) if o.lower() in ("color","colour","צבע")), None)
                cn = vs[0].get(f"option{ci+1}") if ci is not None else ""
                price = min(float(v["price"]) for v in vs)
                old = max(float(v.get("compare_at_price") or 0) for v in vs)
                main, flat = images(p)
                vendor = (p.get("vendor") or "").strip()
                it = {"s": BRAND_STORE.get(vendor.upper(), "factory54"), "g": g, "p": "/".join(path), "n": p["title"],
                      "v": vendor, "pr": price, "c": color_families(cn), "cn": cn or "", "img": main,
                      "u": f"{BASE}/products/{p['handle']}"}
                if flat: it["img2"] = flat
                if path == ["bottom","long"]: it["_d"] = p.get("body_html") or ""
                if old > price + 0.01: it["old"] = old
                items.append(it)
            time.sleep(0.4)
        log(f"factory54 {g}: {n} listed")
    return items
