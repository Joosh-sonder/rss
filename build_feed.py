#!/usr/bin/env python3
"""
Scrapes the MuggleNet HBO Harry Potter TV Series hub page and builds
an RSS 2.0 feed from its "Latest HBO TV Series News" list.

Output: docs/feed.xml  (served for free via GitHub Pages)
"""

import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://mugglenet.com/harry-potter-tv-series/"
FEED_TITLE = "MuggleNet — HBO Harry Potter TV Series News"
FEED_DESCRIPTION = "Latest news headlines from MuggleNet's HBO Harry Potter TV series hub page."
OUTPUT_PATH = "docs/feed.xml"

# You'll set this to your own GitHub Pages URL once it's live, e.g.
# https://yourusername.github.io/mugglenet-rss/feed.xml
SELF_URL = "REPLACE_WITH_YOUR_GITHUB_PAGES_FEED_URL"


def fetch_articles():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RSSBuilderBot/1.0)"}
    resp = requests.get(SOURCE_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    seen_links = set()

    # Article headlines on this page are <h3><a href="...">Title</a></h3>
    # inside the "Latest HBO TV Series News" section. We grab all h3 links
    # that point to a dated MuggleNet article (contains /20xx/ in the path).
    for h3 in soup.find_all("h3"):
        a = h3.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        title = a.get_text(strip=True)
        if not title or not href:
            continue
        if not re.search(r"/20\d{2}/", href):
            continue
        if href in seen_links:
            continue
        seen_links.add(href)
        articles.append({"title": title, "link": href})

    return articles


def build_rss(articles):
    now = format_datetime(datetime.now(timezone.utc))

    items_xml = []
    for art in articles:
        title = escape(art["title"])
        link = escape(art["link"])
        # Use the link as a stable GUID since no per-article date is scraped here.
        items_xml.append(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape(FEED_TITLE)}</title>
    <link>{escape(SOURCE_URL)}</link>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{escape(SELF_URL)}" rel="self" type="application/rss+xml" />
    <description>{escape(FEED_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    <generator>Custom scraper (build_feed.py)</generator>{''.join(items_xml)}
  </channel>
</rss>
"""
    return rss


def main():
    articles = fetch_articles()
    if not articles:
        print("No articles found — page structure may have changed.", file=sys.stderr)
        sys.exit(1)

    rss = build_rss(articles)

    import os
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Wrote {len(articles)} items to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
