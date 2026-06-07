"""
Google News redirect resolver using Playwright.
Tests if Playwright can resolve Google News redirect URLs to real publisher URLs.

Install:
    pip install playwright
    playwright install chromium

Usage:
    python gnews_playwright_test.py
"""

import feedparser
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def resolve_google_news_url(google_url: str) -> str:
    """
    Takes a Google News redirect URL and returns the real publisher URL.
    Uses Playwright headless Chromium to follow the JS redirect.
    """
    # Skip if not a Google News URL
    if not google_url.startswith("https://news.google.com"):
        return google_url

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        try:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Go to Google News redirect URL
            page.goto(google_url, wait_until="domcontentloaded")

            # Wait until URL changes away from google.com (JS redirect happens)
            try:
                page.wait_for_url(
                    lambda url: not url.startswith("https://news.google.com"),
                    timeout=30000  # 15 seconds max
                )
            except PlaywrightTimeoutError:
                return None  # redirect didn't happen

            return page.url

        except Exception as e:
            print(f"   Browser error: {e}")
            return None
        finally:
            browser.close()


def main():
    # Step 1: Fetch RSS feed
    print("\n Fetching Google News RSS...\n")
    feed = feedparser.parse("https://news.google.com/rss/search?q=zomato&hl=en-IN&gl=IN&ceid=IN:en")

    if not feed.entries:
        print(" Feed fetch failed — are you running this on your local machine?")
        return

    print(f" Got {len(feed.entries)} articles\n")
    print("-" * 60)

    # Step 2: Test redirect resolution on first 3 articles only
    for i, entry in enumerate(feed.entries[:3], 1):
        print(f"[{i}] {entry.title}")
        print(f"     Source     : {entry.get('source', {}).get('title', 'N/A')}")
        print(f"     Google URL : {entry.link[:70]}...")
        print(f"     Resolving  : ", end="", flush=True)

        real_url = resolve_google_news_url(entry.link)

        if real_url and "google.com" not in real_url:
            print(f" SUCCESS")
            print(f"     Real URL   : {real_url}")
        else:
            print(f" FAILED — still on Google or timed out")

        print()

if __name__ == "__main__":
    main()

