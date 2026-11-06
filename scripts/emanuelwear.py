"""Emanuel (emanuel.co.il), its clothes. Women only. Its shoes and bags open under the shoes group, see emanuel.py."""
from idus import run, describe
BASE = "https://www.emanuel.co.il"
CATS = {
  "clothes/clothing/מכנסיים": ("women", ["bottom","long"]), "בגדים/clothing/גינסים": ("women", ["bottom","long"]),
  "clothes/clothing/שורטס": ("women", ["bottom","short"]), "clothes/clothing/גינסים-קצרים": ("women", ["bottom","short"]),
  "clothes/clothing/חצאיות": ("women", ["bottom","skirt"]), "clothes/clothing/שמלות": ("women", ["dress"]),
  "בגדים/clothing/חולצות": ("women", ["top"]), "clothes/clothing/חולצות-טי": ("women", ["top","tee"]), "clothes/clothing/גופיות": ("women", ["top","tank"]),
  "clothes/clothing/סריגים": ("women", ["top","knit"]), "clothes/clothing/סריגים-ופוטרים": ("women", ["top","knit"]),
  "clothes/clothing/בלייזרים": ("women", ["jacket"]), "clothes/clothing/זקטים": ("women", ["jacket"]), "clothes/clothing/מעילים": ("women", ["coat"]),
}
def collect(log): return run("emanuel", BASE, CATS, log, brands=True)
