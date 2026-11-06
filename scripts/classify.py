"""Sort a store item into the portal's category tree and colour families.
Works on English names (Zara, H&M) and Hebrew names (Israeli chains)."""
import re

def _rx(words):
    # English: whole words. Hebrew: must start a word (one or two attached prefix letters ו ב ה ל מ ש כ are fine); endings are free.
    return re.compile("|".join(r"(?<![A-Zא-ת])" + w + r"(?![A-Zא-ת])" if w.isascii()
                               else r"(?<![א-ת])[ובהלמשכ]{0,2}" + w for w in words), re.I)

SKIP = _rx(["SOCKS?","LUGGAGE","SUITCASE","CARRY-ON","TAG","PASSPORT","TOILETRY","UMBRELLA","SUNGLASSES","GLASSES","HAIR","SCRUNCHIE",
            "NECKLACE","EARRINGS?","BRACELET","RING","PERFUME","EAU DE","BEANIE","CAP","HAT","GLOVES","MITTENS","SCARF","BANDANA","EARMUFFS",
            "SUIT CARRIER","KEYRING","BRIEFS","BOXERS?","BRA","LINGERIE","PYJAMA","PAJAMA","WALLET","CARD HOLDER","CARDHOLDER","PHONE",
            "גרביים","גרב","מטרייה","משקפ","שיער","שרשרת","עגיל","צמיד","טבעת","בושם","כובע","כפפות","צעיף","תחתונ","חזיי","פיג'מ","ארנק","מחזיק"])
HARD_SKIP = _rx(["SOCKS?","SLIPPERS","TOILETRY","MAKE-UP BAG","גרבי","גרביים","גרביון","גרביונים","נעלי בית","תיק איפור","תיק רחצה","נרתיק איפור"])
SKIP_FAM = re.compile(r"^(HAT|SOCKS|GLOVES|SCARF|SHAWL/FOULARD|GLASSES|UMBRELLA|IMIT JEWELLER|PERFUME|UNDERWEAR|LINGERIE)", re.I)

SHOE_FAM = re.compile(r"SHOE|SANDAL|BOOT|TRAINER|HIGH TOPS|WEDGE|FOOTWEAR|SNEAKER", re.I)
SHOE = _rx(["BOOTS?","TRAINERS?","SNEAKERS?","SANDALS?","HEELS","LOAFERS?","BALLET FLATS","BALLERINAS?","MULES?","SLINGBACK","CLOGS?",
            "DERBY SHOES","SHOES","SLIDES","FLIP FLOPS","ESPADRILLES","OXFORDS?","MOCCASINS?",
            "נעל","מגפ","סניקרס","סנדל","כפכפ","בלרינ","מוקסינ","לואפר","עקב"])
BAG = _rx(["BAGS?","BACKPACK","RUCKSACK","CLUTCH","TOTE","SHOPPER","BUMBAG","BELT BAG","תיק"])
BAG_FAM = re.compile(r"HAND BAG|PURSE WALLET|BAG", re.I)
BELT = _rx(["BELT","BELTS","חגורה","חגורות"])
JUMP = _rx(["JUMPSUIT","PLAYSUIT","DUNGAREES","OVERALLS?","אוברול","סרבל"])
DRESS = _rx(["DRESS","DRESSES","GOWN","שמלה","שמלת","שמלות"])
SKIRT = _rx(["SKIRT","SKORT","חצאית","חצאיות","מכנסצאית"])
SHORTS = _rx(["SHORTS","BERMUDAS?","מכנס קצר","מכנסיים קצרים","קצרים","שורט","ברמודה"])
PANTS = _rx(["TROUSERS","JEANS","PANTS","LEGGINGS","JOGGERS?","JOGGING","CULOTTES?","CHINOS?","SWEATPANTS","TRACKSUIT BOTTOMS",
             "מכנס","מכנסי","מכנסיים","ג'ינס","טייץ","ג'וגר","טרנינג"])
COAT = _rx(["COAT","OVERCOAT","TRENCH","PARKA","CAPE","מעיל","טרנץ'","פרקה"])
JACKET = _rx(["גקט","JACKET","BLAZER","BOMBER","ANORAK","PUFFER","WINDBREAKER","GILET","ג'קט","בלייזר","בומבר","פוך","מעילון","וסט"])
TOP_FAM = re.compile(r"T-SHIRT|TOP|SHIRT|BLOUSE|BODYSUIT|POLO|SWEATER|CARDIGAN|SWEATSHIRT|WAISTCOAT|KNIT", re.I)

def has(rx, s): return bool(rx.search(s))

def length(name, mini="mini", midi="midi", maxi="maxi"):
    if has(_rx(["MINI","SHORT","מיני","קצרה"]), name): return mini
    if has(_rx(["MIDI","מידי"]), name): return midi
    if has(_rx(["MAXI","LONG","מקסי","ארוכה"]), name): return maxi
    return None

def pants_cut(name, g):
    order = [("wide",["WIDE-LEG","WIDE LEG","WIDELEG","PALAZZO","CULOTTES?","VOLUME","ווייד","פאלאצו","רחב","רחבה","רחבים","רגל רחבה","פלאצו","קולוט"]),
             ("skinny",["SKINNY","סקיני","צרים"]),
             ("flare",["FLARE","FLARED","BOOTCUT","BELL","מתרחב","מתרחבים","פלייר","בוטקאט","פדלפון"]),
             ("cargo",["CARGO","קרגו","דגמ''ח","דגמ'ח",'דגמ"ח']),
             ("jogger",["JOGGERS?","JOGGING","SWEATPANTS","TRACKSUIT","DRAWSTRING","ג'וגר","טרנינג","פוטר"]),
             ("legging",["LEGGINGS","טייץ"]),
             ("straight",["STRAIGHT","STRAIGHT-LEG","REGULAR","ישר","ישרה","ישרים","סטרייט","רגולר"]),
             ("slim",["SLIM","סלים"]),
             ("tapered",["TAPERED","CARROT","טייפרד","מחודד","מתחדד"]),
             ("baggy",["BAGGY","BALLOON","BARREL","RELAXED","LOOSE","MOM","בגי","באגי","רלוקסד","רלקסד","בארל","מאם","בלון","בוי פרנד","BOYFRIEND","מום","משוחרר","משוחררים"]),
             ("chino",["CHINOS?","צ'ינו"]),
             ("tailored",["TAILORED","SUIT TROUSERS","PLEATED","מחויט","מחויטים","מחוייט","מחוייטים","עם קפלים"])]
    for cut, words in order:
        if has(_rx(words), name):
            if g == "men":
                if cut in ("wide","baggy"): return "relaxed"
                if cut in ("legging","flare"): return None
            else:
                if cut == "slim": return "skinny"
                if cut == "chino": return "straight"
            return cut
    return None

HEAD_BAG = re.compile(r"^\s*(תיק|ארנק)")
HEAD_UPPER = re.compile(r"^\s*(עליונית|גקט|חולצ|טי.?שירט|טופ|גופי|בגד גוף|בודי|סריג|סוודר|קרדיגן|סווטשירט|קפוצ'ון|פולו|וסט|ג'קט|ז'קט|בלייזר|מעיל|קימונו)")

def classify(name, g, family=""):
    """Return a path list, or None to leave the item out."""
    n = name or ""; fam = family or ""
    he = n.split(" | ")[-1]
    upper = bool(HEAD_UPPER.match(he))   # Hebrew names start with the garment noun
    if has(HARD_SKIP, n): return None
    if HEAD_BAG.match(he): return ["acc","bag"]
    if SKIP_FAM.search(fam) or (has(SKIP, n) and not has(BAG, n) and not BAG_FAM.search(fam)):
        if not (SHOE_FAM.search(fam) or has(SHOE, n)): return None
    # shoes
    if SHOE_FAM.search(fam) or (has(SHOE, n) and not has(DRESS, n.replace("DRESS SHOES","")) or has(_rx(["DRESS SHOES"]), n)):
        if has(_rx(["BOOTS?","ANKLE BOOT","מגפ"]), n) or "BOOT" in fam.upper(): return ["shoes","boots"]
        if has(_rx(["SANDALS?","SLIDES","FLIP FLOPS","סנדל","כפכפ"]), n) or "SANDAL" in fam.upper(): return ["shoes","sandal"]
        if has(_rx(["TRAINERS?","SNEAKERS?","RUNNING","סניקרס","ספורט"]), n) or re.search("TRAINER|SPORT|RUNNING|ATHLETIC|HIGH TOPS", fam, re.I): return ["shoes","sneak"]
        if g == "men": return ["shoes","dress"]
        if has(_rx(["HEELS?","HEELED","KITTEN","SLINGBACK","PUMPS?","WEDGE","עקב"]), n) or "HEEL" in fam.upper(): return ["shoes","heels"]
        return ["shoes","flats"]
    if (has(BAG, n) or BAG_FAM.search(fam)) and not has(_rx(["BAGGY"]), n) and not has(PANTS, n): return ["acc","bag"]
    if fam.upper().startswith("BELT") or (has(BELT, n) and not re.search(r"WITH BELT|BELTED|חגורה ל|עם חגורה", n, re.I) and not has(PANTS, n) and not has(DRESS, n)):
        return ["acc","belt"]
    if not upper and (has(JUMP, n) or fam.upper().startswith("OVERALL")):
        return ["dress","jump"] if g == "women" else None
    if not upper and (has(DRESS, n) and not has(_rx(["DRESS SHIRT","DRESS TROUSERS","DRESS PANTS"]), n)):
        if g == "men": return None
        l = length(n, "dmini","dmidi","dmaxi"); return ["dress", l] if l else ["dress"]
    if not upper and (has(SKIRT, n)):
        if g == "men": return None
        if has(_rx(["SKORT"]), n): return ["bottom","skirt","mini"]
        l = length(n); return ["bottom","skirt", l] if l else ["bottom","skirt"]
    if not upper and (has(SHORTS, n)):
        if has(_rx(["DENIM","JEANS?","ג'ינס"]), n): sub = "sdenim"
        elif has(_rx(["BERMUDAS?","ברמודה"]), n): sub = "berm"
        elif g == "men" and has(_rx(["SPORT","TRAINING","RUNNING","SWIM","ספורט","בגד ים"]), n): sub = "sport"
        else: sub = "stail" if g == "women" else None
        return ["bottom","short", sub] if sub else ["bottom","short"]
    if not upper and has(_rx(["בגד ים","בגדי ים"]), n) and has(PANTS, n):
        return ["bottom","short","sport"] if g == "men" else None
    if not upper and (has(PANTS, n) or re.match(r"TROUSERS|LEGGINGS", fam, re.I)):
        # with "English | Hebrew" names the English cut wins (shop translations are looser)
        c = (pants_cut(n.split(" | ")[0], g) if " | " in n else None) or pants_cut(n, g)
        return ["bottom","long", c] if c else ["bottom","long"]
    if has(COAT, n) and not has(_rx(["COAT HANGER"]), n):
        return ["coat"]
    if has(JACKET, n):
        if has(_rx(["GILET","WAISTCOAT","וסט"]), n) and not has(_rx(["PUFFER","PADDED","QUILTED","DOWN","פוך","מרופד"]), n): return ["top","vest"]
        if has(_rx(["DENIM","ג'ינס"]), n): return ["jacket","jdenim"]
        if has(_rx(["BLAZER","בלייזר","SUIT JACKET"]), n): return ["jacket","blazer"]
        if has(_rx(["LEATHER","SUEDE","עור"]), n): return ["jacket","jleather"]
        if has(_rx(["BOMBER","בומבר"]), n): return ["jacket","bomber"]
        if has(_rx(["PUFFER","PADDED","QUILTED","ANORAK","DOWN","פוך","מרופד"]), n): return ["jacket","puffer"]
        if has(_rx(["GILET","WAISTCOAT","וסט"]), n): return ["top","vest"]
        return ["jacket"]
    # tops
    if has(_rx(["BODYSUIT","BODY","בגד גוף","בודי"]), n): return ["top","body"] if g == "women" else ["top"]
    if has(_rx(["POLO","פולו"]), n): return ["top","polo"] if g == "men" else ["top","tee"]
    if has(_rx(["T-SHIRT","TEE","T SHIRT","טי שירט","טישירט","טי-שירט"]), n): return ["top","tee"]
    if has(_rx(["TANK","CAMISOLE","VEST TOP","STRAPPY","HALTER","גופייה","גופיית","גופיה","סטרפלס"]), n): return ["top","tank"] if g == "women" else ["top","tee"]
    if has(_rx(["CARDIGAN","JUMPER","SWEATER","PULLOVER","KNIT","סריג","סוודר","קרדיגן"]), n): return ["top","knit"]
    if has(_rx(["HOODIE","SWEATSHIRT","קפוצ'ון","סווטשירט","פוטר"]), n): return ["top","hood"]
    if has(_rx(["WAISTCOAT","GILET","וסט"]), n): return ["top","vest"]
    if has(_rx(["OVERSHIRT","SHIRT","חולצה מכופתרת","חולצת כפתורים","מכופתרת","אוברשירט"]), n): return ["top","shirt"]
    if has(_rx(["BLOUSE","חולצ","בלוזה"]), n): return ["top","blouse"] if g == "women" else ["top","shirt"]
    if has(_rx(["TOP","CORSET","BUSTIER","CROP","טופ","מחוך"]), n): return ["top","croptop"] if g == "women" else ["top","tee"]
    if TOP_FAM.search(fam): return ["top"]
    return None

# colour families: id, Hebrew name, swatch hex, keywords (English + Hebrew)
COLORS = [
  ("black","שחור","#1b1b1b",["black","jet","שחור","בלאק"]),
  ("white","לבן","#fbfbf9",["white","optic white","לבן","וייט","ווייט"]),
  ("ecru","שמנת","#ece4d4",["ecru","cream","off-white","off white","oyster","vanilla","ivory","bone","oatmeal","שמנת","אוף וויט","אוף-וויט","אקרו","קרם","ניוטרל"]),
  ("beige","בז'","#cfb99a",["beige","sand","stone","camel","taupe","mink","nude","biscuit","khaki beige","בז'","בז","חול","קאמל","טאופ","ניוד","אבן","שמפניה","מוקה"]),
  ("brown","חום","#6e4b35",["brown","chocolate","tan","cognac","coffee","mocha","chestnut","caramel","toffee","קרמל","טופי","חום","שוקולד","קוניאק"]),
  ("grey","אפור","#9a9893","grey gray charcoal anthracite marl silver-grey אפור אנתרציט פחם מלאנג' גריי".split()),
  ("navy","כחול נייבי","#23304a",["navy","נייבי","כחול כהה"]),
  ("blue","כחול","#5f7fa6",["blue","indigo","denim","sky","cobalt","azure","turquoise","כחול","תכלת","טורקיז","ג'ינס","גינס","אינדיגו","בלו","דנים"]),
  ("green","ירוק","#6b6a3f",["green","khaki","olive","mint","sage","bottle","emerald","ירוק","זית","חאקי","מנטה","ליים","פיסטוק"]),
  ("red","אדום","#a3252a",["red","scarlet","אדום"]),
  ("burgundy","בורדו","#5e1a26",["burgundy","maroon","wine","bordeaux","oxblood","marsala","מרסלה","בורדו","יין"]),
  ("pink","ורוד","#e3b5b8",["pink","fuchsia","rose","blush","raspberry","magenta","פטל","ורוד","פוקסיה"]),
  ("yellow","צהוב","#e2c443",["yellow","mustard","lemon","צהוב","חרדל","בננה","לימון"]),
  ("orange","כתום","#d07a3a",["orange","rust","coral","terracotta","כתום","חמרה","קורל","טרקוטה"]),
  ("purple","סגול","#7d5a8c",["purple","lilac","mauve","violet","plum","lavender","aubergine","חציל","סגול","לילך","לבנדר"]),
  ("metal","מטאלי","#c0b283",["silver","gold","metallic","bronze","pewter","כסף","כסוף","זהב","מטאלי"]),
  ("print","הדפס","linear-gradient(135deg,#1b1b1b 0 33%,#e3b5b8 33% 66%,#5f7fa6 66%)",["print","multicolour","multicolor","stripe","striped","check","floral","animal","leopard","zebra","הדפס","צבעוני","פסים","משבצות","פרחוני","מנומר"]),
]
_HEX = {"black":(27,27,27),"white":(250,250,248),"ecru":(236,228,212),"beige":(207,185,154),"brown":(110,75,53),"grey":(154,152,147),
        "navy":(35,48,74),"blue":(95,127,166),"green":(107,106,63),"red":(163,37,42),"burgundy":(94,26,38),"pink":(227,181,184),
        "yellow":(226,196,67),"orange":(208,122,58),"purple":(125,90,140)}

def color_families(name, hexcode=None):
    s = (name or "").lower(); out = []
    for cid, _, _, words in COLORS:
        # Hebrew colour words must start a word ("כחול" must not count as "חול")
        if any((w.lower() in s) if w.isascii() else re.search(r"(?<![\u05d0-\u05ea])" + re.escape(w), s) for w in words): out.append(cid)
    if "navy" in out and "blue" in out and "light" not in s: out.remove("blue")
    if "grey" in out and "silver-grey" in s and "metal" in out: out.remove("metal")
    if not out and hexcode and re.match(r"#?[0-9a-f]{6}$", hexcode, re.I):
        h = hexcode.lstrip("#"); rgb = tuple(int(h[i:i+2],16) for i in (0,2,4))
        out = [min(_HEX, key=lambda k: sum((a-b)**2 for a,b in zip(_HEX[k], rgb)))]
    return out
