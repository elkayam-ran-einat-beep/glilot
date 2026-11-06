"""Crazy Line (crazyline.com), women only."""
from idus import run, describe
BASE = "https://www.crazyline.com"
W = "women"
CATS = {
  "קולקציה/שמלות": (W, ["dress"]), "קולקציה/חולצות": (W, ["top"]), "קולקציה/ג׳ינסים": (W, ["bottom","long"]),
  "קולקציה/מכנסיים-וחצאיות": (W, ["bottom"]), "קולקציה/זקטים-עליוניות": (W, ["jacket"]), "קולקציה/מעילים": (W, ["coat"]),
  "קולקציה/סריגים-וקרדיגנים": (W, ["top","knit"]), "קולקציה/vests-main-0706": (W, ["top","vest"]),
  "קולקציה/קולקציית-עור": (W, None), "קולקציה/main_sets": (W, None), "קולקציה/קולקצית-ערב": (W, None),
  "קולקציה/capes-0110": (W, ["coat"]), "אביזרים/תיקים": (W, ["acc","bag"]), "אביזרים/חגורות": (W, ["acc","belt"]),
  "tamaris-main/shoes-sub-1": (W, ["shoes"]),
}
def collect(log): return run("crazyline", BASE, CATS, log)
