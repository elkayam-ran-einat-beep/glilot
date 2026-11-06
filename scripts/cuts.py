"""Give long trousers a cut. Names are tried first, then the shop's description.
Descriptions mention other wide or straight things (waistbands, belts), so only explicit phrases about the leg or fit count."""
import html, json, os, re, time
from classify import pants_cut

HE = r"(?<![א-ת])[ובהלמשכ]{0,2}"
FIT = r"ג[י]?זר[הת]\s+"                     # "גזרה" / "גזרת" / "גיזרה"
PANTS = r"מכנס\S*\s+"
LEG = r"רגל(?:יים)?\s+"
CUTS = [
    ("wide", r"wide[ -]?leg|palazzo|culottes?|" + HE + r"(?:" + LEG + "|" + FIT + "|" + PANTS + r")רחב|" + HE + r"(?:ווייד|וייד|פלאצו|פאלאצו|קולוט)"),
    ("skinny", r"\bskinny\b|" + HE + r"סקיני|" + HE + r"(?:" + LEG + "|" + FIT + "|" + PANTS + r")צר(?:ה|ים)?(?![א-ת])"),
    ("flare", r"\bflared?\b|boot ?cut|" + HE + r"(?:מתרחב|פלייר|בוטקאט|פדלפון)"),
    ("cargo", r"\bcargo\b|" + HE + r"(?:קרגו|דגמ\W{0,2}ח)"),
    ("jogger", r"\bjoggers?\b|sweatpants|" + HE + r"(?:ג'וגר|טרנינג)"),
    ("legging", r"\bleggings?\b|" + HE + r"טייץ"),
    ("straight", r"straight|" + HE + r"(?:" + LEG + "|" + FIT + "|" + PANTS + r")ישר|" + HE + r"(?:סטרייט|רגולר)"),
    ("slim", r"\bslim\b|" + HE + r"סלים"),
    ("tapered", r"\btapered\b|\bcarrot\b|" + HE + r"(?:טייפרד|" + LEG + "מחודד|" + FIT + "מחודד|" + PANTS + r"מחודד|" + LEG + "מתחדד|" + FIT + "מתחדד|" + PANTS + "מתחדד)"),
    ("baggy", r"\bbaggy\b|\bballoon\b|\bbarrel\b|\brelaxed\b|\bloose\b|mom fit|" + HE + r"(?:באגי|בגי|בלון|רלוקסד|רלקסד|בארל|מאם פיט|" + FIT + r"משוחרר|" + PANTS + r"משוחרר)|(?<![א-ת])מום(?![א-ת])"),
    ("chino", r"\bchinos?\b|" + HE + r"צ'ינו"),
    ("tailored", r"\btailored\b|" + HE + r"מחוי?יט"),
]
CUTS = [(c, re.compile(r, re.I)) for c, r in CUTS]

def _for_gender(cut, g):
    """Same mapping as classify.pants_cut: the tree has different cuts for women and men."""
    if g == "men":
        if cut in ("wide", "baggy"): return "relaxed"
        if cut in ("legging", "flare"): return None
    else:
        if cut == "slim": return "skinny"
        if cut == "chino": return "straight"
    return cut

def clean(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text.replace("’", "'").replace("׳", "'").replace("״", '"').replace("”", '"'))

def find_cut(text, g):
    text = clean(text)
    for cut, rx in CUTS:
        if rx.search(text):
            mapped = _for_gender(cut, g)
            if mapped: return mapped
    return None

def refine(items, module, store, out_dir, log, max_fetch=2500):
    """Fill in the cut of uncut long trousers and drop the temporary "_d" description. Pages that had to be fetched are cached by address."""
    cache_path = os.path.join(out_dir, f"cuts-{store}.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    describe = getattr(module, "describe", None)
    fresh, seen = {}, {}
    from_name = from_desc = fetched = errors = 0
    for it in items:
        desc = it.pop("_d", None)
        if it["p"] != "bottom/long": continue
        text = it["n"] + " " + (it.get("en") or "")
        cut = pants_cut(clean(text), it["g"]) or find_cut(text, it["g"])
        if cut:
            from_name += 1
        else:
            if desc is None and describe:
                u = it["u"]
                if u in cache:
                    fresh[u] = cache[u]; cut = cache[u] or None
                elif u in fresh:
                    cut = fresh[u] or None
                elif fetched < max_fetch and errors < 15:
                    fetched += 1
                    try:
                        fresh[u] = find_cut(describe(it), it["g"]) or ""
                        cut = fresh[u] or None; errors = 0
                    except Exception as ex:
                        errors += 1; log(f"   {store} description failed: {ex}")
                    time.sleep(0.4)
            elif desc:
                cut = find_cut(desc, it["g"])
            if cut: from_desc += 1
        if cut: it["p"] = f"bottom/long/{cut}"
    if describe:
        with open(cache_path, "w", encoding="utf-8") as f: json.dump(fresh, f, ensure_ascii=False, separators=(",", ":"))
    left = sum(1 for i in items if i["p"] == "bottom/long")
    log(f"   cuts: {from_name} from the name, {from_desc} from the description, {left} still without a cut ({fetched} pages read)")
