"""Delta (delta.co.il). Clothes only: its underwear, socks, pajamas and shapewear have no place in the portal.
Its shirt lists also hold thermal wear, multi-packs of undershirts and teens' items, which are dropped by name."""
import re
from idus import run, describe
BASE = "https://www.delta.co.il"
CATS = {
  "women/shirts": ("women", ["top"]), "women/pants": ("women", ["bottom","long"]), "women/sweatshirts": ("women", ["top","hood"]),
  "men/shirts": ("men", ["top"]), "men/pants": ("men", ["bottom","long"]), "men/sweatshirts": ("men", ["top","hood"]),
}
SKIP = re.compile(r"נערות|נוער|ילד|תרמי|מארז|נגיש|תחתונ|פיג'מ|פיג׳מ|\bboxer", re.I)

def collect(log):
    items = []
    for it in run("delta", BASE, CATS, log):
        if SKIP.search(it["n"]): continue
        # Plain shirts: the sorter takes "חולצה" as a blouse for women and a button-up for men
        if it["p"] in ("top/shirt", "top/blouse") and "מכופתר" not in it["n"]:
            it["p"] = "top/tee" if "קצרה" in it["n"] else "top"
        items.append(it)
    log(f"delta: {len(items)} left after dropping thermal wear, packs and teens")
    return items
