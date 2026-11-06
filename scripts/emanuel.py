"""Emanuel (emanuel.co.il), its shoes and bags. Women only. Its clothes open under the high-end group, see emanuelwear.py."""
from idus import run, describe
BASE = "https://www.emanuel.co.il"
CATS = {"shoes": ("women", ["shoes"]), "bags": ("women", ["acc","bag"])}
def collect(log): return run("emanuel", BASE, CATS, log, pages=400, brands=True)
