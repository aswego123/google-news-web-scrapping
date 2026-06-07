"""
Run this on YOUR machine (BLRTSL02608) — not a server.
It dumps the raw HTML of the Google News interstitial so we can
find data-n-au / c-wiz / canonical patterns to extract the real URL.

Usage:
    python gnews_diagnose.py <google_news_rss_url>

Example:
    python gnews_diagnose.py "https://news.google.com/rss/articles/CBMirwJB...?oc=5"
"""

import sys
import re
import requests
from bs4 import BeautifulSoup

url = sys.argv[1] if len(sys.argv) > 1 else input("Paste a Google News RSS article URL: ").strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

print(f"\n📡 Fetching: {url[:80]}...\n")
res = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)

print(f"Status      : {res.status_code}")
print(f"Final URL   : {res.url}")
print(f"Content-Type: {res.headers.get('content-type', '')}")
print(f"Body length : {len(res.text)} chars")
print()

# ── Pattern hunting ────────────────────────────────────────────────────────────
soup = BeautifulSoup(res.text, "html.parser")

# 1. data-n-au attribute (classic Google News decode target)
data_n_au = soup.find_all(attrs={"data-n-au": True})
print(f"[1] data-n-au elements : {len(data_n_au)}")
for el in data_n_au[:3]:
    print(f"     → {el['data-n-au']}")

# 2. canonical link
canonical = soup.find("link", rel="canonical")
print(f"\n[2] canonical link : {canonical['href'] if canonical else 'NOT FOUND'}")

# 3. meta refresh
meta_refresh = soup.find("meta", attrs={"http-equiv": re.compile("refresh", re.I)})
print(f"[3] meta refresh   : {meta_refresh}")

# 4. c-wiz tags (Google's component wrapper — sometimes embeds URLs)
cwiz = soup.find_all("c-wiz")
print(f"\n[4] c-wiz elements : {len(cwiz)}")
for c in cwiz[:3]:
    print(f"     attrs: {dict(list(c.attrs.items())[:5])}")

# 5. All non-google URLs in the entire HTML
non_google_urls = re.findall(r'https?://(?!(?:www\.)?google|gstatic)[^\s"\'<>]{15,}', res.text)
print(f"\n[5] Non-google URLs found in page ({len(non_google_urls)} total):")
for u in non_google_urls[:10]:
    print(f"     → {u}")

# 6. Raw HTML dump (first 2000 chars) so we can spot patterns manually
print(f"\n[6] Raw HTML (first 2000 chars):")
print("-" * 60)
print(res.text[:2000])
print("-" * 60)

# 7. Script tags — Google often embeds the real URL in JS
scripts = soup.find_all("script")
print(f"\n[7] Script tags: {len(scripts)}")
for i, s in enumerate(scripts[:5]):
    content = s.string or ""
    if any(kw in content for kw in ["data-n-au", "articleUrl", "canonicalUrl", "http"]):
        print(f"  Script [{i}] (first 300 chars): {content[:300]}")