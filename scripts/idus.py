"""Israeli Magento shops built on the same template (Golf, Castro, Crazy Line): read category listing pages."""
import re, html, json, time
from common import get
from classify import classify, color_families

LI = re.compile(r'<li data-unique-selector-key="\d+" id="product_category_(\d+)"(.*?)</form>\s*</li>', re.S)

def norm(s): return html.unescape(s or "").replace("’", "'").replace("׳", "'").replace("״", '"').strip()

def parse(page, base):
    out = []
    for pid, body in LI.findall(page):
        sku = re.search(r'data-product-sku="([^"]+)"', body)
        img = re.search(r'<img class="product-image-photo" src="([^"]+)"[^>]*alt="([^"]*)"', body)
        link = re.search(r'<a[^>]+class="product-item-link"[^>]*href="([^"]+)"', body) or re.search(r'href="(' + re.escape(base) + r'/[^"]+)"', body)
        col = re.search(r'swatch_color-selected" style="background:\s*(#[0-9a-fA-F]{6})[^"]*">\s*<span[^>]*>([^<]*)</span>', body)
        cn, hexc = (norm(col.group(2)), col.group(1)) if col else ("", None)
        if not cn:   # colour name from the swatch config: the default option, else the first
            m = re.search(r'"code":"color","label":"[^"]*","options":(\[.*?\]),"position":"\d+","default":"?(\d*)"?', body)
            if m:
                try:
                    opts = json.loads(m.group(1)); d = m.group(2)
                    pick = next((o for o in opts if o["id"] == d), opts[0] if opts else None)
                    if pick: cn = norm(pick["label"])
                except Exception: pass
        prices = re.search(r'"optionPrices":\{"\d+":\{"oldPrice":\{"amount":([\d.]+)\},"basePrice":\{"amount":[\d.]+\},"costPrice":\{"amount":[^}]*\},"finalPrice":\{"amount":([\d.]+)\}', body)
        if prices: old, final = float(prices.group(1)), float(prices.group(2))
        else:
            p = re.search(r'data-price-amount="([\d.]+)"', body); old, final = None, float(p.group(1)) if p else None
        if not (img and final): continue
        s = sku.group(1) if sku else pid
        out.append({"id": pid, "name": norm(img.group(2)), "img": img.group(1),
                    "url": link.group(1) if link else f"{base}/{s}", "hex": hexc, "cn": cn,
                    "pr": round(final, 2), "old": round(old, 2) if old and old > final + 0.01 else None,
                    "oos": 'product_outofstock="true"' in body})
    return out

def describe(it):
    """The shop's description of one item, for items whose name does not give the cut."""
    page = get(it["u"], accept="text/html").decode("utf-8", "replace")
    m = re.search(r'<meta name="description" content="([^"]*)"', page)
    return m.group(1) if m else ""

def merge(name_path, cat_path):
    """The shop's own sub-category wins when it is more specific and agrees with the name."""
    if not name_path: return cat_path
    if cat_path and len(cat_path) > len(name_path) and cat_path[:len(name_path)] == name_path: return cat_path
    return name_path

def run(store, base, cats, log, pages=60):
    items, seen = [], set()
    for path, (g, fallback) in cats.items():
        n = kept = 0
        for p in range(1, pages):
            try: page = get(f"{base}/{path}?p={p}", accept="text/html").decode("utf-8", "replace")
            except Exception as ex: log(f"{store} {path} p{p}: {ex}"); break
            fresh = [r for r in parse(page, base) if r["id"] not in seen]
            if not fresh: break
            for r in fresh:
                seen.add(r["id"]); n += 1
                if r["oos"]: continue
                cpath = merge(classify(r["name"], g), fallback)
                if not cpath: continue
                it = {"s": store, "g": g, "p": "/".join(cpath), "n": r["name"], "pr": r["pr"],
                      "c": color_families(r["cn"], r["hex"]), "cn": r["cn"], "img": r["img"], "u": r["url"]}
                if r["old"]: it["old"] = r["old"]
                items.append(it); kept += 1
            time.sleep(0.5)
        log(f"{store} {g} {path}: {n} listed, {kept} kept")
    return items
