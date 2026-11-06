"""Shoofra (shoofra.co.il, WooCommerce). The shop pages carry everything on the card: name, brand, colour, price, photos.
Each card is one colour of a shoe."""
import html, re, time, urllib.parse
from common import get
from classify import classify, color_families

BASE = "https://www.shoofra.co.il"
SEX = {"women": "נשים", "men": "גברים"}
CARD = re.compile(r'<li class="product"(.*?)(?=<li class="product"|</ul>\s*</div>\s*<nav|\Z)', re.S)

def attr(block, name):
    m = re.search(rf'data-{name}="([^"]*)"', block)
    return html.unescape(m.group(1)).strip() if m else ""

def collect(log):
    items, seen, unsorted_names = [], set(), []
    for g, sex in SEX.items():
        q = urllib.parse.quote(sex)
        for page in range(1, 120):
            url = f"{BASE}/shop/page/{page}/?sex={q}" if page > 1 else f"{BASE}/shop/?sex={q}"
            try: body = get(url, accept="text/html").decode("utf-8", "replace")
            except Exception as ex: log(f"shoofra {g} p{page}: {ex}"); break
            cards = CARD.findall(body)
            if not cards: break
            for c in cards:
                name = attr(c, "name"); pid = attr(c, "product_id"); colour = attr(c, "color")
                if not name or (pid, colour) in seen: continue
                seen.add((pid, colour))
                path = classify(name, g)
                if not path: unsorted_names.append(name); continue
                link = re.search(r'href="(https://www\.shoofra\.co\.il/brands/[^"]+)"', c)
                imgs = re.findall(r'<img src="([^"]+/wp-content/uploads/[^"]+)"', c)
                if not link or not imgs: continue
                try: now, was = float(attr(c, "price_sale") or attr(c, "price")), float(attr(c, "price") or 0)
                except ValueError: continue
                it = {"s": "shoofra", "g": g, "p": "/".join(path), "n": name, "v": attr(c, "brand"), "pr": min(now, was or now),
                      "c": color_families(colour), "cn": colour, "img": imgs[0], "u": html.unescape(link.group(1))}
                if max(now, was) > min(now, was or now) + 0.01: it["old"] = max(now, was)
                items.append(it)
            time.sleep(0.5)
    log(f"shoofra: {len(items)} kept, {len(unsorted_names)} not sorted, e.g. {unsorted_names[:12]}")
    return items
