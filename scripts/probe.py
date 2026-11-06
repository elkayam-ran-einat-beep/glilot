"""Show where a product page states the colour. Usage: probe.py PRODUCT_URL ..."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from common import get

COL = "שחור|לבן|אפור|כחול|נייבי|ירוק|חום|בז|שמנת|אדום|ורוד|בורדו|אוף|קאמל|מוקה|זית"
for u in sys.argv[1:]:
    b = get(u, accept="text/html").decode("utf-8", "replace")
    print("=====", u, len(b), flush=True)
    print("words", {c: len(re.findall(c, b)) for c in COL.split("|") if re.search(c, b)})
    for m in list(re.finditer("שחור|אפור", b))[:4]:
        print("NEAR", re.sub(r"\s+", " ", b[max(0, m.start()-230):m.end()+120]))
    seen = set()
    for m in re.finditer(rf".{{60}}(?:צבע|colou?r|swatch).{{0,90}}(?:{COL}).{{0,40}}", b, re.I):
        t = re.sub(r"\s+", " ", m.group(0))
        if t[:70] not in seen:
            seen.add(t[:70]); print("HIT", t[:230])
        if len(seen) > 7: break
