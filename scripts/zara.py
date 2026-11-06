"""Zara Israel: women's and men's clothing, shoes, bags and belts."""
import time
from common import get_json
from classify import classify, color_families

BASE = "https://www.zara.com/il"
WANT = {
  "WOMAN": ["JACKETS","DRESSES","SHIRTS","TOPS | BODIES","T-SHIRTS","JEANS","TROUSERS","SKIRTS","BLAZERS","KNITWEAR","COATS",
            "PUFFERS | TECHNICAL","SWEATSHIRTS | JOGGERS","SHORTS | BERMUDAS","JUMPERS | CARDIGANS","LEATHER","CO-ORD SETS",
            "SHOES","BAGS","ACCESSORIES"],
  "MAN": ["JACKETS | GILETS","PUFFERS","COATS","SWEATERS | CARDIGANS","SWEATSHIRTS | SWEATPANTS","JEANS","TROUSERS","LEATHER",
          "T-SHIRTS","LONG SLEEVE T-SHIRTS","SHIRTS","POLO SHIRTS","OVERSHIRTS","SUITS","BLAZERS","SUMMERY GARMENTS","VIEW ALL",
          "SHOES","TRAINERS","BAGS | BACKPACKS","ACCESSORIES"],
}
GENDER = {"WOMAN": "women", "MAN": "men"}
# Zara's own fit sub-categories under JEANS / TROUSERS -> portal cut
FITS = {"BARREL":"baggy","WIDE-LEG":"wide","MOM FIT":"baggy","STRAIGHT-LEG":"straight","BAGGY":"baggy","CARGO":"cargo",
        "TAILORED":"tailored","JOGGERS":"jogger","LEGGINGS":"legging","STRAIGHT":"straight","SLIM":"slim","LOOSE":"relaxed",
        "REGULAR":"straight","FLARE":"flare","BALLOON | BARREL":"baggy","SKINNY FIT":"skinny","CHINOS":"chino",
        "SWEATPANTS":"jogger","WIDE LEG | BALLOON":"relaxed","PLEATED":"tailored"}
MEN_FIX = {"baggy":"relaxed","wide":"relaxed","flare":None,"legging":None}
WOMEN_FIX = {"slim":"skinny","relaxed":"baggy","chino":"straight"}

def components(cid, lang):
    d = get_json(f"{BASE}/{lang}/category/{cid}/products?ajax=true")
    for g in d.get("productGroups", []):
        for e in g.get("elements", []):
            for c in e.get("commercialComponents") or []:
                if c.get("type") == "Product": yield c

def pick_image(col, seo_id):
    """Model shot (-p, else -a1/-a2) for the main view, the item on white (-f1, else -e1) for the product view."""
    media = [m for m in col.get("xmedia") or [] if m.get("url")]
    own = [m for m in media if m.get("name","").startswith(seo_id)] or media
    def find(*suffixes):
        for suf in suffixes:
            for m in own:
                if m.get("name","").endswith("-" + suf): return m["url"]
        return None
    main = find("p", "a1", "a2", "a3") or (own[0]["url"] if own else None)
    flat = find("f1", "e1")
    return main, (flat if flat != main else None)

def describe(it):
    """Zara answers the product address with a pointer to the Hebrew page, which holds the description."""
    d = get_json(it["u"] + "&ajax=true")
    if d.get("location"): d = get_json(d["location"])
    p = d.get("product") or {}
    cols = (p.get("detail") or {}).get("colors") or []
    return " ".join(x for x in [(p.get("seo") or {}).get("description")] + [c.get("description") or c.get("rawDescription") for c in cols[:1]] if x)

def collect(log):
    cats = get_json(f"{BASE}/en/categories?ajax=true")["categories"]
    items, seen = [], set()
    for sec in cats:
        if sec.get("name") not in WANT: continue
        g = GENDER[sec["name"]]; found = {}
        def walk(cs):
            for c in cs:
                if c.get("name") in WANT[sec["name"]] and c["name"] not in found:
                    found[c["name"]] = c.get("redirectCategoryId") or c["id"]
                walk(c.get("subcategories", []))
        walk(sec.get("subcategories", []))
        cutmap = {}
        def fits(cs, under):
            for c in cs:
                if under and c.get("name") in FITS:
                    cut = FITS[c["name"]]
                    cut = (MEN_FIX if g == "men" else WOMEN_FIX).get(cut, cut)
                    if cut:
                        found.setdefault(f"{under} / {c['name']}", c["id"])
                        try:
                            for x in components(c["id"], "en"): cutmap.setdefault(x["id"], cut)
                            time.sleep(0.5)
                        except Exception as ex: log(f"zara fit {c['name']}: {ex}")
                fits(c.get("subcategories", []), c["name"] if c.get("name") in ("JEANS","TROUSERS") else under)
        fits(sec.get("subcategories", []), None)
        log(f"zara {g}: fit labels for {len(cutmap)} items")
        for cname, cid in found.items():
            try:
                en = list(components(cid, "en")); time.sleep(0.7)
                he = {c["id"]: c for c in components(cid, "he")}; time.sleep(0.7)
            except Exception as ex:
                log(f"zara {sec['name']}/{cname}: {ex}"); continue
            kept = 0
            for c in en:
                if c["id"] in seen: continue
                seen.add(c["id"])
                if c.get("sectionName") and GENDER.get(c["sectionName"]) != g: continue
                h = he.get(c["id"], {})
                path = classify(c.get("name","") + " | " + (h.get("name") or ""), g, c.get("familyName",""))
                if not path: continue
                if path[:2] == ["bottom","long"] and len(path) == 2 and c["id"] in cutmap: path.append(cutmap[c["id"]])
                cols = (c.get("detail") or {}).get("colors") or []
                col = cols[0] if cols else {}
                if col.get("availability") == "out_of_stock": continue
                hcol = (((h.get("detail") or {}).get("colors")) or [{}])[0]
                seo = c.get("seo") or {}
                hexc = next((a.get("hexColor") for a in c.get("availableColors") or [] if a.get("colorName") == col.get("name")), None) \
                       or ((c.get("colorInfo") or {}).get("mainColorHexCode"))
                img, flat = pick_image(col, seo.get("seoProductId",""))
                price = (col.get("price") or c.get("price") or 0) / 100
                old = col.get("oldPrice") or c.get("oldPrice")
                it = {"s":"zara","g":g,"p":"/".join(path),
                      "n": h.get("name") or c.get("name"),
                      "en": c.get("name"),
                      "pr": round(price, 2),
                      "c": color_families(col.get("name",""), hexc),
                      "cn": hcol.get("name") or col.get("name",""),
                      "img": img.replace("{width}","563") if img else None,
                      "u": f"https://www.zara.com/il/he/{seo.get('keyword','p')}-p{seo.get('seoProductId','')}.html?v1={seo.get('discernProductId', c['id'])}"}
                if flat: it["img2"] = flat.replace("{width}","563")
                if old: it["old"] = round(old/100, 2)
                if "NEW" in (c.get("productTag") or []): it["new"] = 1
                items.append(it); kept += 1
            log(f"zara {g} {cname}: {len(en)} listed, {kept} kept")
    return items
