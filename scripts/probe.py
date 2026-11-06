import sys,os,re,html,urllib.request; sys.path.insert(0,os.path.dirname(__file__))
from common import UA
def fetch(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA,"Accept":"text/html,application/json"}),timeout=40)
    return r, r.read().decode("utf-8","replace")
for a in sys.argv[1:]:
    mode,_,u=a.partition("::") if "::" in a else ("head","",a)
    try:
        r,b=fetch(u)
        print("OK",u,r.status,r.geturl(),len(b))
        if mode=="links":
            seen=set()
            for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>',b,re.S):
                href=m.group(1); t=re.sub(r"<[^>]+>|\s+"," ",m.group(2)).strip()
                if href in seen or not t or len(t)>40: continue
                seen.add(href); print("  ",href,"|",html.unescape(t))
        elif mode=="grep":
            pat=os.environ.get("PAT","product-item-info|toolbar-number|\"@type\":\"Product|impressions|dataLayer")
            for m in list(re.finditer(pat,b))[:3]: print("   ...",b[max(0,m.start()-300):m.start()+1500].replace("\n"," "))
        else:
            hints=[h for h in ["Shopify","Magento","mage/","woocommerce","wp-content","__NEXT_DATA__","_nuxt","demandware","dwanalytics","vtex","konimbo","algolia","graphql","cdn.shopify","static/version","itxrest","salesforce","Wix","bigcommerce","sfcc","/on/demandware.store"] if h.lower() in b.lower()]
            t=re.search(r"<title[^>]*>(.*?)</title>",b,re.S)
            print("    hints:",hints,"| title:",html.unescape(t.group(1).strip())[:90] if t else "")
    except Exception as e: print("ERR",u,e)
