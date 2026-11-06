import gzip, json, urllib.request, urllib.error, urllib.parse, subprocess, time
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

def _curl(url, accept):
    """Some shops refuse Python's HTTP client but accept curl with browser headers."""
    cmd = ["curl", "-sS", "-L", "--compressed", "--max-time", "60", "-A", UA, "-H", f"Accept: {accept}",
           "-H", "Accept-Language: he-IL,he;q=0.9,en;q=0.8", "-H", 'sec-ch-ua: "Chromium";v="130", "Google Chrome";v="130"',
           "-H", "sec-ch-ua-mobile: ?0", "-H", 'sec-ch-ua-platform: "Windows"', "-H", "Sec-Fetch-Dest: empty",
           "-H", "Sec-Fetch-Mode: cors", "-H", "Sec-Fetch-Site: same-origin", "-w", "\n%{http_code}", url]
    out = subprocess.run(cmd, capture_output=True, timeout=90).stdout
    body, _, code = out.rpartition(b"\n")
    if code.strip() != b"200": raise RuntimeError(f"curl HTTP {code.decode().strip()} for {url}")
    return body

def get(url, accept="application/json", tries=3, headers=None):
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@!$'()*~")   # Hebrew paths
    h = {"User-Agent": UA, "Accept": accept, "Accept-Language": "he-IL,he;q=0.9,en;q=0.8"}
    h.update(headers or {})
    for i in range(tries):
        try:
            body = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40).read()
            return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body   # some shops compress without being asked
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                try: return _curl(url, accept)
                except Exception:
                    if i == tries - 1: raise
            elif e.code == 404 or i == tries - 1: raise
        except Exception:
            if i == tries - 1: raise
        time.sleep(3 * (i + 1))

def get_json(url, **kw): return json.loads(get(url, **kw))
