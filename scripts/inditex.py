"""Inditex shops in Israel (Pull & Bear, Stradivarius, Oysho) through the same itxrest catalogue Massimo Dutti uses.
Each shop is described by its store numbers, the category keys to read, and which photo is the model shot and which the item.
Jeans and trousers lists hold fit sub-categories (wide leg, barrel, straight...), and those give the cut."""
import re, time
from common import get_json
from classify import classify, color_families

L = ["bottom", "long"]
FITS = [(r"WIDE.?LEG|PALAZZO", "wide"), (r"BARREL|BAGGY|MOM|BALLOON|BOMBACHO", "baggy"), (r"RECTO|STRAIGHT|STANDARD", "straight"),
        (r"SKINNY", "skinny"), (r"FLARE|BOOTCUT", "flare"), (r"CARGO|PARACHUTE", "cargo"), (r"JOGG", "jogger"),
        (r"VESTIR|TAILOR|SASTRE", "tailored"), (r"CHINO", "chino"), (r"SLIM", "slim")]
MEN_FIX = {"baggy": "relaxed", "wide": "relaxed", "flare": None}
WOMEN_FIX = {"slim": "skinny", "chino": "straight"}
SKIP_NAME = re.compile(r"רחצה|נססר|טואלט|פיג'מ|פיג׳מ|חזיי?[הת]|תחתונ|הריון", re.I)

SHOPS = {
  "pullandbear": dict(host="pullandbear", store=25009552, catalog=20309459,
      genders={"PULL_MUJER_NUEVACOLECCION": "women", "PULL_HOMBRE_NUEVACOLECCION": "men"},
      keys={"NC-PULL_MUJER_ROPA_CAZADORASYCHAQUETAS": ["jacket"], "NC-PULL_MUJER_ROPA_ABRIGOSYGABARDINAS": ["coat"],
            "NC-PULL_MUJER_ROPA_JEANS": L, "NC-PULL_MUJER_ROPA_PANTALONES": L, "NC-PULL_MUJER_ROPA_CAMISETAS": ["top", "tee"],
            "NC-PULL_MUJER_ROPA_TOPS": ["top"], "NC-PULL_MUJER_ROPA_SUDADERAS": ["top", "hood"], "NC-PULL_MUJER_ROPA_PUNTO": ["top", "knit"],
            "NC-PULL_MUJER_ROPA_BLUSASYCAMISAS": ["top"], "NC-PULL_MUJER_ROPA_FALDASYSHORTS": None, "NC-PULL_MUJER_ROPA_VESTIDOS": ["dress"],
            "PULL_MUJER_CALZADO_NC": ["shoes"], "PULL_MUJER_BOLSOS_NC": ["acc", "bag"], "PULL_MUJER_ACCESORIOS_NC": None,
            "NC-PULL_HOMBRE_ROPA_ABRIGOSYCAZADORAS": ["jacket"], "NC-PULL_HOMBRE_ROPA_JEANS": L, "NC-PULL_HOMBRE_ROPA_PANTALONES": L,
            "NC-PULL_HOMBRE_ROPA_SUDADERAS": ["top", "hood"], "NC-PULL_HOMBRE_ROPA_CAMISETAS": ["top", "tee"],
            "NC-PULL_HOMBRE_ROPA_CAMISETASMANGALARGA": ["top", "tee"], "NC-PULL_HOMBRE_ROPA_PUNTO": ["top", "knit"],
            "NC-PULL_HOMBRE_ROPA_CAMISAS": ["top", "shirt"], "NC-PULL_HOMBRE_ROPA_BERMUDAS": ["bottom", "short"],
            "PULL_HOMBRE_CALZADO_NC": ["shoes"], "PULL_HOMBRE_BOLSOS_NC": ["acc", "bag"], "PULL_HOMBRE_ACCESORIOS_NC": None},
      model=["k1", "k2", "m1", "x2", "a2m"], flat=["c1", "a6m", "z1"], width="?w=563"),
  "stradivarius": dict(host="stradivarius", store=55009602, catalog=50331103,
      genders={"STR_MUNDO_INV_MUJER_MENU": "women"},
      keys={"STR_MUNDO_INV_JEANS_TESTPRIMERNIVEL": L, "STR_MUNDO_INV_PANTALONES_TESTPRIMERNIVEL": L,
            "STR_MUNDO_INV_CAMISETAS_TESTPRIMERNIVEL": ["top", "tee"], "STR_MUNDO_INV_CHAQUETAS_TRENCH_TESTPRIMERNIVEL": ["jacket"],
            "STR_MUNDO_INV_TOPS_BODIES_TESTPRIMERNIVEL": ["top"], "STR_MUNDO_INV_FALDAS_TESTPRIMERNIVEL": ["bottom", "skirt"],
            "STR_MUNDO_INV_CAMISAS_TESTPRIMERNIVEL": ["top"], "STR_MUNDO_INV_SUDADERAS_TESTPRIMERNIVEL": ["top", "hood"],
            "STR_MUNDO_INV_JERSEIS_Y_CARDIGANS": ["top", "knit"], "STR_MUNDO_INV_PUNTO_TESTPRIMERNIVEL": ["top", "knit"],
            "STR_MUNDO_INV_ABRIGOS": ["coat"], "STR_MUNDO_INV_VESTIDOS_TESTPRIMERNIVEL": ["dress"],
            "STR_MUNDO_INV_SHORTS_TESTPRIMERNIVEL": ["bottom", "short"], "STR_MUNDO_INV_AMERICANAS": ["jacket", "blazer"],
            "STR_MUNDO_INV_ZAPATOS_TODOS": ["shoes"], "STR_MUNDO_INV_BOLSOS_": ["acc", "bag"], "STR_MUNDO_INV_CINTURONES": ["acc", "belt"]},
      model=["a1", "a2", "a3", "a15", "a16"], flat=["m1", "s1"], width="?w=563"),
  "oysho": dict(host="oysho", store=64009652, catalog=60361120,
      genders={"VER_POR_PRODUCTO": "women"},
      keys={"PR_PANTALONES": L, "PR_TOPS": ["top"], "PR_CHAQUETAS": ["jacket"], "PR_VESTIDOS_MONOS": ["dress"],
            "PR_CAMISETAS": ["top", "tee"], "PR_SHORTS": ["bottom", "short"], "PR_FALDAS": ["bottom", "skirt"],
            "PR_SUDADERAS": ["top", "hood"], "PR_POLOS": ["top", "polo"], "PR_PUNTO": ["top", "knit"],
            "PR_CAMISAS_SOBRECAMISAS": ["top"], "PR_CALZADO": ["shoes"], "PR_BOLSOS_NECESERES": ["acc", "bag"]},
      model=["p1", "t1", "k1", "a1"], flat=["m1", "d1"], width="?w=563", skip_paths={"bottom/long/legging"}, skip_name=r"טייץ|legging"),   # its leggings are sportswear
}

def key(c): return (c.get("key") or "").split("#")[0]   # Oysho adds display flags after '#'

def merge(name_path, cat_path):
    if not name_path: return cat_path
    if cat_path and len(cat_path) > len(name_path) and cat_path[:len(name_path)] == name_path: return cat_path
    return name_path

def photos(xmedia, colour_id, cfg):
    x = next((x for x in xmedia or [] if x.get("path") == f"/{colour_id}"), None)
    if not x: return None, None
    by = {}
    for it in x.get("xmediaItems", []):
        for m in it.get("medias", []):
            e = m.get("extraInfo") or {}
            if e.get("deliveryUrl"): by.setdefault(e.get("originalName"), e["deliveryUrl"])
    def url(u): return u.split("?")[0] + cfg["width"]
    model = next((by[n] for n in cfg["model"] if n in by), None)
    flat = next((by[n] for n in cfg["flat"] if n in by), None)
    main = model or flat or next((u for n, u in by.items() if n and not n.startswith("r")), None)   # r = colour swatch
    return (url(main) if main else None), (url(flat) if flat and flat != main else None)

def collect_shop(sid, log):
    cfg = SHOPS[sid]
    api = f"https://www.{cfg['host']}.com/itxrest"
    base = f"{api}/3/catalog/store/{cfg['store']}/{cfg['catalog']}"
    tree = get_json(f"{api}/2/catalog/store/{cfg['store']}/{cfg['catalog']}/category?languageId=-52&typeCatalog=1&appId=1")["categories"]
    targets = []   # (order, gender, category id, fallback path)
    def walk(cs, g, under):
        for c in cs:
            k = key(c)
            cid = c.get("viewCategoryId") or c["id"]
            if k in cfg["keys"]:
                targets.append((1, g, cid, cfg["keys"][k]))
                walk(c.get("subcategories", []), g, k if cfg["keys"][k] == L else None)
                continue
            if under:
                fit = next((cut for rx, cut in FITS if re.search(rx, k[len(under):] if k.startswith(under) else k)), None)
                fit = (MEN_FIX if g == "men" else WOMEN_FIX).get(fit, fit)
                if fit: targets.append((0, g, cid, L + [fit]))
            walk(c.get("subcategories", []), g, under)
    for top in tree:
        if key(top) in cfg["genders"]: walk(top.get("subcategories", []), cfg["genders"][key(top)], None)
    targets.sort(key=lambda t: t[0])   # fit lists first, so an item keeps the cut its shop gave it
    owner = {}
    for _, g, cid, fb in targets:
        try: d = get_json(f"{base}/category/{cid}/product?languageId=-52&appId=1")
        except Exception as ex: log(f"{sid} cat {cid}: {ex}"); continue
        for pid in d.get("productIds") or []: owner.setdefault(pid, (g, fb))
        time.sleep(0.4)
    log(f"{sid}: {len(targets)} categories ({sum(1 for t in targets if t[0] == 0)} by fit), {len(owner)} products")
    items, ids = [], list(owner)
    def fetch(batch):
        d = get_json(f"{base}/productsArray?productIds={','.join(map(str, batch))}&languageId=-52&appId=1")
        if "products" not in d and len(batch) > 1:   # one id the shop no longer knows fails the whole batch
            out = []
            for one in batch:
                try: out += fetch([one])
                except Exception: pass
            return out
        return d.get("products") or []
    for i in range(0, len(ids), 30):
        try: products = fetch(ids[i:i+30])
        except Exception as ex: log(f"{sid} batch {i}: {ex}"); continue
        for b in products:
            try: items.extend(product_items(sid, cfg, b, owner))
            except Exception as ex: log(f"{sid} product {b.get('id')}: {type(ex).__name__} {ex}")
        time.sleep(0.4)
    # The same garment sits in several product bundles: keep it once, as the portal page would
    seen, kept = set(), []
    for it in items:
        if it["p"] in cfg.get("skip_paths", ()): continue
        k1, k2 = (it["g"], it["img"].split("?")[0]), (it["g"], it["n"], it["cn"], it["pr"])
        if k1 in seen or k2 in seen: continue
        seen.update((k1, k2)); kept.append(it)
    log(f"{sid}: {len(kept)} of {len(items)} kept after removing repeats")
    return kept

def product_items(sid, cfg, b, owner):
    out = []
    g, fb = owner.get(b.get("id"), ("women", None))
    p = (b.get("bundleProductSummaries") or [b])[0]
    det = p.get("detail") or {}
    name = b.get("name") or p.get("name") or ""
    if not name or SKIP_NAME.search(name): return out
    if cfg.get("skip_name") and re.search(cfg["skip_name"], name + " " + (b.get("nameEn") or ""), re.I): return out
    path = merge(classify((b.get("nameEn") or "") + " | " + name, g), fb)
    if not path: return out
    slug = b.get("productUrl") or p.get("productUrl") or ""
    for col in det.get("colors") or []:
        sizes = [x for x in col.get("sizes") or [] if x.get("isBuyable")]
        if not sizes or not sizes[0].get("price"): continue
        price = int(sizes[0]["price"]) / 100
        old = int(sizes[0]["oldPrice"]) / 100 if sizes[0].get("oldPrice") else None
        main, flat = photos(det.get("xmedia"), col.get("id"), cfg)
        if not main: continue
        it = {"s": sid, "g": g, "p": "/".join(path), "n": name, "en": b.get("nameEn"), "pr": price,
              "c": color_families(col.get("name", "")), "cn": col.get("name", ""), "img": main,
              "u": f"https://www.{cfg['host']}.com/il/{slug}?pelement={b.get('id')}&cS={col.get('id')}&colorId={col.get('id')}"}
        if flat: it["img2"] = flat
        if old and old > price: it["old"] = old
        if path == L: it["_d"] = (det.get("longDescription") or "") + " " + (det.get("description") or "")
        out.append(it)
    return out
