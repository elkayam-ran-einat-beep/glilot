"""Delta (delta.co.il). Clothes only: its underwear, socks, pajamas and shapewear have no place in the portal."""
from idus import run, describe
BASE = "https://www.delta.co.il"
CATS = {
  "women/shirts": ("women", ["top"]), "women/pants": ("women", ["bottom","long"]), "women/sweatshirts": ("women", ["top","hood"]),
  "men/shirts": ("men", ["top"]), "men/pants": ("men", ["bottom","long"]), "men/sweatshirts": ("men", ["top","hood"]),
}
def collect(log): return run("delta", BASE, CATS, log)
