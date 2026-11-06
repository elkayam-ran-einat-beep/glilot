"""Every shop that runs on Shopify, described in one table. A shop that sells both shoes and clothes can have two entries
sharing a label ("s"): its shoes open under the shoes group and its clothes under another."""
import collections, json, os, re, time
from common import get, get_json
from classify import classify, color_families

SHOPS = {
    "renuar":          dict(name="רנואר", base="https://renuar.co.il", tier="afford"),
    "twentyfourseven": dict(name="24/7", base="https://twentyfourseven.co.il", tier="afford"),
    "fox":             dict(name="פוקס", base="https://fox.co.il", tier="afford", strict=True),
    "mania":           dict(name="מאניה ג'ינס", base="https://www.maniajeans.co.il", tier="chains",
                            swatch=r'href="/products/([^"]+)"[^>]*title="([^"]+)"\s+aria-label="צבע'),
    "itaybrands":      dict(name="איתי ברנדס", base="https://itaybrands.co.il", tier="afford",
                            swatch=r'href="/products/([^"]+)"\s*>\s*<div class="color-swatch" data-tooltip="([^"]+)"'),
    "stevemaddenwear": dict(name="סטיב מאדן", s="stevemadden", base="https://stevemadden.co.il", tier="chains", only="wear"),
    "maskit":          dict(name="משכית", base="https://maskit.com", tier="high"),
    "replay":          dict(name="ריפליי", base="https://replayjeans.co.il", tier="chains"),
    "mrsomething":     dict(name="Mr Something", base="https://mrsomething.co.il", tier="high", brands=True, skip_vendor=r"^Alchemist$"),
    "storywear":       dict(name="סטורי", s="story", base="https://storyonline.co.il", tier="high", only="wear", brands=True, flat=r"_S_\d+_FNT"),
    "story":           dict(name="סטורי", base="https://storyonline.co.il", tier="shoes", only="shoes", brands=True, flat=r"_S_\d+_FNT"),
    "stevemadden":     dict(name="סטיב מאדן", base="https://stevemadden.co.il", tier="shoes", only="shoes"),
    "originals":       dict(name="אוריג'ינלס", base="https://originals.co.il", tier="shoes", only="shoes", brands=True, skip_type=r"ריצה|ספורט"),
    "tikhatikim":      dict(name="תיק התיקים", base="https://tikhatikim.co.il", tier="shoes", only="shoes", brands=True,
                            skip_type=r"מזווד|טרולי|ארגונית|ארנק|מחשב|לפטופ", skip_title=r"מזווד|טרולי|ארנק|משלוח"),
    "footlocker":      dict(name="פוט לוקר", base="https://footlocker.co.il", tier="sport", brands=True),
    "megasport":       dict(name="מגה ספורט", base="https://www.megasport.co.il", tier="sport", brands=True),
    "columbia":        dict(name="קולומביה", base="https://columbia.co.il", tier="sport"),
    "ripcurl":         dict(name="ריפ קרל", base="https://ripcurl.co.il", tier="sport"),
}

KIDS = re.compile(r"ילד|נוער|(?<![א-ת])בנות|(?<![א-ת])בנים|פעוט|תינוק|\bkids?\b|\bjuniors?\b", re.I)
WOMEN = re.compile(r"נשים|לאישה|\bwom[ae]n('?s)?\b|\bladies\b", re.I)
MEN = re.compile(r"גברים|לגבר|\bm[ae]n('?s)?\b", re.I)
COLOUR_OPTION = re.compile(r"^(colou?r|צבע|צבעים|color_description)\s*$", re.I)
# When the name says nothing, the shop's own product type decides (first match wins)
SKIP_TYPE = re.compile(r"תחתונ|גרבי|כובע|כפפות|בגד.?ים|בגדי.?ים|גלישה|מזווד|ארנק|ביגוד תרמי|חם צוואר|\bsocks\b|swim|underwear|\bhats?\b|accessor|אביזר|service|\bhome\b|אחר", re.I)
BY_TYPE = [
    (r"סניקרס|sneaker", ["shoes", "sneak"]), (r"מגפ", ["shoes", "boots"]), (r"סנדל|כפכפ", ["shoes", "sandal"]), (r"מוקסין", ["shoes", "flats"]),
    (r"נעל|shoes", ["shoes"]), (r"תיק", ["acc", "bag"]), (r"שמל|dress", ["dress"]), (r"חצאי|skirt", ["bottom", "skirt"]),
    (r"טייצ", ["bottom", "long", "legging"]), (r"קצרים|shorts", ["bottom", "short"]), (r"מכנס|ג'ינס|pants|denim|jeans|sweatpants", ["bottom", "long"]),
    (r"מעיל|coat", ["coat"]), (r"ג'קט|גקט|jacket|פליס", ["jacket"]), (r"סריג|knit", ["top", "knit"]), (r"קפוצ|סווטשירט|hoodie", ["top", "hood"]),
    (r"גופי", ["top", "tank"]), (r"טי.?שירט|t-?shirt", ["top", "tee"]), (r"פולו|polo", ["top", "polo"]), (r"חולצ|shirt|top|פוטר", ["top"]),
]
# Spellings the shops use that the sorter does not know
SPELL = [(r"^טי(?=\s)", "טי שירט"), (r"קפוצון", "קפוצ'ון"), (r"טרנץ(?!')", "טרנץ'"), (r"(?<![א-ת'])גינס", "ג'ינס"), (r"דגמח", 'מכנס דגמ"ח'),
         (r"סקורט", "חצאית"), (r"סינקרס|סניקס", "סניקרס"), (r"מיולז", "נעלי מיולז"), (r"קבקב", "כפכפ"), (r"(?<![א-ת])מגף", "מגפיים"),
         (r"''", "'"), (r"טישרט|טישירט", "טי שירט"), (r"מוקסין(?![א-ת])", "מוקסינים"), (r"\bPant\b", "Pants"), (r"\bTshirt\b", "T-Shirt"), (r"חלצת", "חולצת"), (r"סוויטשירט", "סווטשירט")]
_cache = {}

def _products(base, log):
    if base not in _cache:
        ps = []
        for page in range(1, 200):
            try: batch = get_json(f"{base}/products.json?limit=250&page={page}").get("products") or []
            except Exception as ex: log(f"{base} p{page}: {ex}"); break
            if not batch: break
            ps += batch; time.sleep(0.4)
        _cache[base] = ps
    return _cache[base]

def _genders(p, shop):
    for hay in (p["title"], p.get("vendor") or "", " | ".join(p.get("tags") or [])):
        w, m = bool(WOMEN.search(hay)), bool(MEN.search(hay))
        if w and m: return ["women", "men"]
        if w: return ["women"]
        if m: return ["men"]
    return [] if shop.get("strict") else ["women"]

def _path(title, g, ptype):
    name = title.replace("׳", "'").replace("״", '"').replace("’", "'")
    for a, b in SPELL: name = re.sub(a, b, name, flags=re.I)
    path = classify(name, g)
    if path or not ptype or SKIP_TYPE.search(ptype): return path
    for rx, fallback in BY_TYPE:
        if re.search(rx, ptype, re.I): return fallback
    return None

class Shop:
    def __init__(self, sid): self.id, self.cfg = sid, SHOPS[sid]

    def collect(self, log):
        c = self.cfg
        items, dropped = [], collections.Counter()
        unsorted_names = []
        for p in _products(c["base"], log):
            vs = [v for v in p.get("variants", []) if v.get("available")]
            title, ptype, vendor = p["title"], p.get("product_type") or "", (p.get("vendor") or "").strip()
            hint = ptype or " | ".join(p.get("tags") or [])   # shops without a type often say it in their tags
            if not vs: continue
            if KIDS.search(title) or KIDS.search(vendor) or KIDS.search(ptype) or any(KIDS.fullmatch(t.strip()) for t in p.get("tags") or []):
                dropped["kids"] += 1; continue
            if (c.get("skip_type") and re.search(c["skip_type"], ptype)) or (c.get("skip_title") and re.search(c["skip_title"], title)) \
               or (c.get("skip_vendor") and re.search(c["skip_vendor"], vendor)):
                dropped["shop rule"] += 1; continue
            genders = _genders(p, c)
            if not genders: dropped["no gender"] += 1; continue
            opts = [o.get("name", "") for o in p.get("options", [])]
            ci = next((i for i, o in enumerate(opts) if COLOUR_OPTION.match(o)), None)
            cn = (vs[0].get(f"option{ci+1}") or "") if ci is not None else ""
            imgs = [i["src"] for i in p.get("images", [])]
            flat = next((u for u in imgs if c.get("flat") and re.search(c["flat"], u)), None)
            price = min(float(v["price"]) for v in vs)
            old = max(float(v.get("compare_at_price") or 0) for v in vs)
            for g in genders:
                path = _path(title, g, hint)
                if not path: unsorted_names.append(title); continue
                is_shoes = path[0] == "shoes" or path[:2] == ["acc", "bag"]
                if (c.get("only") == "shoes" and not is_shoes) or (c.get("only") == "wear" and is_shoes):
                    dropped["other group"] += 1; continue
                it = {"s": c.get("s", self.id), "g": g, "p": "/".join(path), "n": title, "pr": price,
                      "c": color_families(cn) or color_families(title), "cn": cn, "img": imgs[0] if imgs else None,
                      "u": f"{c['base']}/products/{p['handle']}"}
                it["_h"] = p["handle"]
                if c.get("brands") and vendor: it["v"] = vendor
                if flat and flat != it["img"]: it["img2"] = flat
                if old > price + 0.01: it["old"] = old
                if path == ["bottom", "long"]: it["_d"] = p.get("body_html") or ""
                items.append(it)
        self._colours_from_pages(items, log)
        log(f"{self.id}: {len(items)} kept, dropped {dict(dropped)}, not sorted {len(unsorted_names)}: {unsorted_names[:25]}")
        return items

    def _colours_from_pages(self, items, log):
        """Shops that keep colour only in the swatches of the product page. One page names all the colours of a model, and what was read is kept."""
        c = self.cfg
        rx = c.get("swatch")
        if rx:
            path = os.path.join(os.environ.get("GLILOT_OUT") or ".", f"colours-{self.id}.json")
            known = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
            read, errors = 0, 0
            for it in items:
                h = it["_h"]
                if it["c"] or (h in known and not known[h]): continue
                if h not in known and read < 3000 and errors < 15:
                    read += 1
                    try:
                        page = get(it["u"], accept="text/html").decode("utf-8", "replace")
                        known[h] = ""
                        for sib, name in re.findall(rx, page): known[sib] = name
                        errors = 0
                    except Exception as ex:
                        errors += 1; log(f"   {self.id} colour page failed: {ex}")
                    time.sleep(0.3)
                if known.get(h):
                    it["cn"] = known[h]; it["c"] = color_families(known[h])
            with open(path, "w", encoding="utf-8") as f: json.dump(known, f, ensure_ascii=False, separators=(",", ":"))
            log(f"   colours: {read} pages read, {sum(not i['c'] for i in items)} of {len(items)} still without a colour")
        for it in items: it.pop("_h", None)
