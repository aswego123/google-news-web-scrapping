import feedparser
import requests

feed = feedparser.parse("https://news.google.com/rss/search?q=zomato&hl=en-GB&gl=GB&ceid=GB:en")

headers = {"User-Agent": "Mozilla/5.0"}

for entry in feed.entries:
    google_url = entry.link
    
    # Follow the redirect to get the real URL
    try:
        res = requests.get(google_url, headers=headers, allow_redirects=True, timeout=5)
        real_url = res.url  # final destination after redirect
    except Exception:
        real_url = google_url  # fallback to google url if it fails
    
    print(entry.title)
    print(real_url)
    print("---")