"""Top Ten (topten-fashion.com). Bags and belts only: the portal has no place for its jewellery, gadgets, wallets or pouches."""
from idus import run, describe
BASE = "https://www.topten-fashion.com"
CATS = {
  "תיקים/צד": ("women", ["acc","bag"]), "תיקים/גב": ("women", ["acc","bag"]), "תיקים/ערב-וקלאץ": ("women", ["acc","bag"]),
  "אקססוריז/חגורות": ("women", ["acc","belt"]),
}
def collect(log): return run("topten", BASE, CATS, log)
