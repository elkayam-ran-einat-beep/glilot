"""Massimo Dutti Israel (Inditex itxrest API)."""
import time
from common import get_json
from classify import classify, color_families

API = "https://www.massimodutti.com/itxrest"
STORE, CATALOG, LANG = 35009519, 30359534, -52
L = ["bottom","long"]
# category key (or key prefix) -> fallback path. Fit sub-categories carry a cut.
KEYS = {
  "WOMEN_V_FAM_JEANS_STRAIGHT_FIT": L+["straight"], "WOMEN_V_FAM_JEANS_WIDE_LEG": L+["wide"], "WOMEN_V_FAM_JEANS_FLARE_FIT": L+["flare"],
  "WOMEN_C_FAM_TROUSERS_CARGO_WEB": L+["cargo"], "WOMEN_V_FAM_TROUSERS_FORMAL": L+["tailored"], "WOMEN_V_FAM_SUITS_TROUSERS_WEB": L+["tailored"],
  "WOMEN_V_FAM_TROUSERS_PALAZZO_WEB": L+["flare"],
  "MEN_V_FAM_TROUSERS_RELAXED_FIT": L+["relaxed"], "MEN_V_FAM_TROUSERS_SLIM_FIT": L+["slim"], "MEN_V_FAM_TROUSERS_CHINOS": L+["chino"],
  "MEN_V_FAM_TROUSERS_JOGGER_FIT": L+["jogger"], "MEN_V_FAM_JEANS_TAPERED_FIT": L+["slim"], "MEN_V_FAM_JEANS_SLIM_FIT": L+["slim"],
  "MEN_V_FAM_JEANS_STRAIGHT_RELAXED": L+["straight"], "MEN_V_FAM_JEANS_WIDE_BARREL": L+["relaxed"],
  "VISTA23-MEN_V_FAM_TROUSERS_SHORTS_VIEW_ALL": ["bottom","short"],
  "WOMEN_V_FAM_JACKETS_TRENCHS": ["jacket"], "WOMEN_V_FAM_COATS": ["coat"], "VISTA23-WOMEN_V_FAM_DOWN_JACKETS_PUFFERS": ["jacket","puffer"],
  "WOMEN_V_FAM_JUMPERS_CARDIGANS": ["top","knit"], "WOMEN_V_FAM_SHIRTS": ["top","shirt"], "WOMEN_V_FAM_DRESSES_JUMPSUITS": ["dress"],
  "WOMEN_V_FAM_SKIRTS": ["bottom","skirt"], "WOMEN_V_FAM_TROUSERS": L, "WOMEN_V_FAM_JEANS": L, "WOMEN_V_FAM_T-SHIRTS": ["top","tee"],
  "WOMEN_V_FAM_TOPS": ["top"], "WOMEN_V_FAM_BLAZERS_VIEW_ALL": ["jacket","blazer"], "VISTA23-WOMEN_V_FAM_BLAZERS_VIEW_ALL": ["jacket","blazer"],
  "WOMEN_V_FAM_SHOES": ["shoes"], "WOMEN_V_FAM_BAGS_WALLETS": ["acc","bag"], "WOMEN_V_FAM_ACCS_BELTS": ["acc","belt"],
  "WOMEN_V_FAM_LEATHER": None, "WOMEN_V_FAM_100_CASHMERE": None,
  "MEN_V_FAM_JUMPERS_CARDIGANS": ["top","knit"], "MEN_V_FAM_JACKETS": ["jacket"], "MEN_V_FAM_LEATHER_JACKETS": ["jacket","jleather"],
  "MEN_V_FAM_COATS_VIEW_ALL": ["coat"], "VISTA23-MEN_V_FAM_DOWN_PUFFERS_JACKETS_VIEW_ALL": ["jacket","puffer"],
  "MEN_V_FAM_TROUSERS": L, "MEN_V_FAM_SHIRTS": ["top","shirt"], "MEN_V_FAM_JEANS": L, "MEN_V_FAM_POLO_SHIRTS": ["top","polo"],
  "MEN_V_FAM_T_SHIRTS": ["top","tee"], "MEN_V_FAM_BLAZERS": ["jacket","blazer"], "VISTA23-MEN_V_FAM_OVERSHIRTS_VIEW_ALL": ["top","shirt"],
  "MEN_V_FAM_SHOES": ["shoes"], "MEN_V_FAM_ACCESSORIES_BELTS": ["acc","belt"], "MEN_V_FAM_ACCESSORIES_BAGS_TOILETERY": ["acc","bag"],
  "MEN_V_FAM_CASHMERE": None,
}

def merge(name_path, cat_path):
    if not name_path: return cat_path
    if cat_path and len(cat_path) > len(name_path) and cat_path[:len(name_path)] == name_path: return cat_path
    return name_path

def media(colors_xmedia, color_id):
    x = next((x for x in colors_xmedia or [] if x.get("path") == f"/{color_id}"), None)
    if not x: return None, None
    ms = [m for it in x.get("xmediaItems", []) for m in it.get("medias", [])]
    def url(m): return (m.get("extraInfo") or {}).get("deliveryUrl", "").split("?")[0] + "?w=563"
    def num(m):
        n = (m.get("extraInfo") or {}).get("originalName", "")
        return int(n[1:]) if n[1:].isdigit() else 99
    models = [m for m in ms if (m.get("extraInfo") or {}).get("productionType") == "MODEL"]
    model = min(models, key=num) if models else None   # lowest number = full-length shot
    flat = next((m for m in ms if (m.get("extraInfo") or {}).get("originalName") == "o1"), None) \
        or next((m for m in ms if (m.get("extraInfo") or {}).get("originalName") == "t1"), None)
    main = model or flat
    return (url(main) if main else None), (url(flat) if flat and flat is not main else None)

def product_items(b, owner):
    out = []
    g, fb = owner.get(b.get("id"), ("women", None))
    p = (b.get("bundleProductSummaries") or [b])[0]
    det = p.get("detail") or {}
    path = merge(classify((b.get("nameEn") or "") + " | " + (b.get("name") or ""), g), fb)
    if not path: return out
    for col in det.get("colors") or []:
        sizes = [x for x in col.get("sizes") or [] if x.get("isBuyable")]
        if not sizes or not sizes[0].get("price"): continue
        price = int(sizes[0]["price"]) / 100
        old = int(sizes[0]["oldPrice"]) / 100 if sizes[0].get("oldPrice") else None
        main, flat = media(det.get("xmedia"), col.get("id"))
        url = b.get("productUrl") or p.get("productUrl") or ""
        it = {"s": "massimodutti", "g": g, "p": "/".join(path), "n": b.get("name"), "en": b.get("nameEn"),
              "pr": price, "c": color_families(col.get("name","")), "cn": col.get("name",""), "img": main,
              "u": f"https://www.massimodutti.com/il/{url}?pelement={b.get('id')}&colorId={col.get('id')}"}
        if flat: it["img2"] = flat
        if old and old > price: it["old"] = old
        if len(path) == 2 and path[:2] == ["bottom","long"]: it["_d"] = (det.get("longDescription") or "") + " " + (det.get("description") or "")
        out.append(it)
    return out

def collect(log):
    tree = get_json(f"{API}/2/catalog/store/{STORE}/{CATALOG}/category?languageId={LANG}&typeCatalog=1&appId=1")["categories"]
    targets = []   # (gender, category id, fallback, order)
    def walk(cs, g):
        for c in cs:
            key = c.get("key") or ""
            if key in KEYS:
                cid = c.get("viewCategoryId") or c["id"]
                deep = len(KEYS[key] or []) >= 3 or key.startswith("VISTA23-MEN_V_FAM_TROUSERS_SHORTS")
                targets.append((g, cid, KEYS[key], 0 if deep else 1))
            walk(c.get("subcategories", []), g)
    for top in tree:
        if top.get("key") == "WOMEN.": walk(top.get("subcategories", []), "women")
        if top.get("key") == "MEN.": walk(top.get("subcategories", []), "men")
    targets.sort(key=lambda t: t[3])
    owner = {}     # product id -> (gender, fallback); fit categories are read first
    for g, cid, fb, _ in targets:
        try: d = get_json(f"{API}/3/catalog/store/{STORE}/{CATALOG}/category/{cid}/product?languageId={LANG}&appId=1")
        except Exception as ex: log(f"massimodutti cat {cid}: {ex}"); continue
        for pid in d.get("productIds") or []: owner.setdefault(pid, (g, fb))
        time.sleep(0.4)
    log(f"massimodutti: {len(targets)} categories, {len(owner)} products")
    items, ids = [], list(owner)
    for i in range(0, len(ids), 30):
        batch = ids[i:i+30]
        try: d = get_json(f"{API}/3/catalog/store/{STORE}/{CATALOG}/productsArray?productIds={','.join(map(str,batch))}&languageId={LANG}&appId=1")
        except Exception as ex: log(f"massimodutti batch {i}: {ex}"); continue
        for b in d.get("products", []):
            try: items.extend(product_items(b, owner))
            except Exception as ex: log(f"massimodutti product {b.get('id')}: {type(ex).__name__} {ex}")
        time.sleep(0.4)
    return items
