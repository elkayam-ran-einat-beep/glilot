"""Golf (golf-il.co.il)."""
from idus import run, describe
BASE = "https://www.golf-il.co.il"
CATS = {
  "women/shirts-and-tops": ("women", ["top"]), "women/jeans": ("women", ["bottom","long"]),
  "women/pants": ("women", ["bottom","long"]), "women/dresses-and-overalls": ("women", ["dress"]),
  "women/skirts": ("women", ["bottom","skirt"]), "women/sweater-and-knitted-shirts": ("women", ["top","knit"]),
  "women/cardigans": ("women", ["top","knit"]), "women/jackets-and-coats": ("women", ["jacket"]),
  "women/sets": ("women", None), "shoes/shoes-women": ("women", ["shoes"]), "women/accessories": ("women", None),
  "men/t-shirts": ("men", ["top","tee"]), "men/polo-shirts": ("men", ["top","polo"]), "men/button-up-shirts": ("men", ["top","shirt"]),
  "men/denim": ("men", ["bottom","long"]), "men/pants": ("men", ["bottom","long"]),
  "men/sweaters-and-knitted-shirts": ("men", ["top","knit"]), "men/sweatshirts": ("men", ["top","hood"]),
  "men/jackets-and-coats": ("men", ["jacket"]), "men/g-collection": ("men", None),
  "men/shoes": ("men", ["shoes"]), "men/accessories": ("men", None),
}
def collect(log): return run("golf", BASE, CATS, log)
