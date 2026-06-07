"""
Deep dig into Google News interstitial page scripts to find the real article URL.
Run on BLRTSL02608.

Usage:
    python gnews_deep_dig.py "https://news.google.com/rss/articles/CBMi6AB..."
"""

import sys
import re
import json
import requests
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

url = sys.argv[1] if len(sys.argv) > 1 else input("Paste article URL: ").strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

res = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
soup = BeautifulSoup(res.text, "html.parser")
full_html = res.text

print(f"Body size: {len(full_html)} chars\n")
print("=" * 60)

# ── Dump ALL script tag contents in full ─────────────────────────
scripts = soup.find_all("script")
print(f"Total script tags: {len(scripts)}\n")

for i, s in enumerate(scripts):
    content = s.string or ""
    if not content:
        continue
    print(f"\n{'='*60}")
    print(f"SCRIPT [{i}] — {len(content)} chars")
    print(f"{'='*60}")
    # Print full content — we need to see everything
    print(content[:5000])
    if len(content) > 5000:
        print(f"... [{len(content)-5000} more chars truncated]")

# ── Regex hunt for anything that looks like a publisher URL ──────
print(f"\n{'='*60}")
print("REGEX HUNT — non-google, non-gstatic URLs in full HTML")
print(f"{'='*60}")

# Look for URLs that are NOT google/gstatic/fonts
publisher_urls = re.findall(
    r'https?://(?!(?:www\.)?(?:google|gstatic|googleapis|googleusercontent))[a-zA-Z0-9\-\.]+\.[a-z]{2,}[^\s"\'\\<>]{5,}',
    full_html
)
# Deduplicate
seen = set()
unique_urls = []
for u in publisher_urls:
    domain = re.match(r'https?://([^/]+)', u)
    if domain and domain.group(1) not in seen:
        seen.add(domain.group(1))
        unique_urls.append(u)

print(f"Unique publisher domains found: {len(unique_urls)}")
for u in unique_urls[:20]:
    print(f"  → {u[:120]}")