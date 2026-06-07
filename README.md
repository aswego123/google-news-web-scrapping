# Google News URL Resolver — POC

Google News RSS feeds return redirect URLs (`news.google.com/...`) instead of real article URLs. This POC investigates how to resolve them to the actual publisher URLs (e.g. `economictimes.com/...`).

---

## The Problem

Google News redirects work via JavaScript running in the browser. Static HTTP requests download the page but never execute the JS — so the real URL never appears. `requests` + BeautifulSoup cannot solve this.

---

## Scripts

| File | Purpose |
|---|---|
| `google-news-script.py` | First attempt — uses `requests` to follow redirects. Works for simple redirects, fails for JS-based ones. |
| `gnews_diagnose.py` | Diagnostic tool — fetches the Google News interstitial page and hunts for the real URL in HTML attributes, meta tags, and script tags. |
| `gnews_diagnose-2.py` | Deeper diagnostic — dumps all script tag contents and regex-searches for publisher URLs in the full HTML. |
| `gnews_playwright-final.py` | **Working solution** — uses Playwright headless Chromium to execute the JS redirect and capture the final URL. |

---

## Conclusion

- Static scraping (`requests`) cannot resolve Google News redirects — the real URL is fetched at runtime via JS.
- Playwright (headless browser) works. ~70–80% success rate expected; some sites show consent gates.

---

## Setup

**1. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Install Playwright's Chromium browser (one-time):**
```bash
playwright install chromium
```

---

## Usage

**Run the working Playwright resolver:**
```bash
python gnews_playwright-final.py
```
Fetches the top 3 results from a Google News RSS feed for "zomato" and resolves each to its real publisher URL.

**Run a diagnostic on a specific article URL:**
```bash
python gnews_diagnose.py "https://news.google.com/rss/articles/CBMi..."
python gnews_diagnose-2.py "https://news.google.com/rss/articles/CBMi..."
```


## Java / Spring Boot Integration

See `Google-news-implementation.txt` for the full guide on integrating this into a Spring Boot service using the [Playwright for Java](https://playwright.dev/java/) library — no Python sidecar needed.

----------------------------------------------------------------------------------------------------


Additional information -

The script is a detective tool — it downloads the Google News redirect page and searches through it trying to find the real article URL (like `economictimes.com/...`) hiding somewhere in the HTML or JavaScript.


Think of it like this:

When you click a Google News link, Google shows you a page that says *"wait, let me take you to the article..."* and then your browser gets redirected. That redirect happens via JavaScript running in your browser.

We were trying to find **where in that page's code** the real URL is written, so we could extract it without needing a browser.

The script looked in 2 places:
- **Script tags** — JavaScript code blocks in the page
- **Regex hunt** — scanned the entire page for any non-Google URLs

**Result:** The real URL wasn't there at all. Google's page loads, then makes a *separate network call* to fetch the real URL at runtime — meaning it only exists after JavaScript actually executes in a browser.

**That's why `requests` + BeautifulSoup can never work here** — they download the page but don't run JavaScript. It's like getting a recipe that says *"call this phone number for the ingredients"* but you have no phone.

That's what led us to Playwright — because Playwright actually runs a real browser that executes the JavaScript.