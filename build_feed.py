#!/usr/bin/env python3
"""
Scrapes the MuggleNet HBO Harry Potter TV Series hub page and builds
an RSS 2.0 feed from its "Latest HBO TV Series News" list.

Output: docs/feed.xml  (served for free via GitHub Pages)

Each item gets a stable pubDate: if we've seen that article link before
(from a previous run), we reuse its original pubDate. Only genuinely new
articles get stamped with the current time. This prevents old articles
from being treated as "new" on every run.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://mugglenet.com/harry-potter-tv-series/"
FEED_TITLE = "MuggleNet — HBO Harry Potter TV Series News"
FEED_DESCRIPTION = "Latest news headlines from MuggleNet's HBO Harry Potter TV series hub page."
OUTPUT_PATH = "docs/feed.xml"

# Your live GitHub Pages feed URL.
SELF_URL = "https://joosh-sonder.github.io/rss/feed.xml"


def fetch_articles():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RSSBuilderBot/1.0)"}
    resp = requests.get(SOURCE_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    seen_links = set()

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


def load_existing_pubdates(path):
    """Return {link: pubDate_string} from a previously-generated feed, if any."""
    dates = {}
    if not os.path.exists(path):
        return dates
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for item in root.findall("./channel/item"):
            link_el = item.find("link")
            pubdate_el = item.find("pubDate")
            if link_el is not None and pubdate_el is not None:
                dates[link_el.text.strip()] = pubdate_el.text.strip()
    except Exception as e:
        print(f"Warning: could not parse existing feed for dates: {e}", file=sys.stderr)
    return dates


def build_rss(articles, existing_dates):
    now = datetime.now(timezone.utc)
    build_time = format_datetime(now)

    items_xml = []
    new_count = 0
    for i, art in enumerate(articles):
        link_plain = art["link"]
        if link_plain in existing_dates:
            pubdate_str = existing_dates[link_plain]
        else:
            pubdate_str = format_datetime(now - timedelta(seconds=i))
            new_count += 1

        title = escape(art["title"])
        link = escape(link_plain)
        items_xml.append(f"""
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{pubdate_str}</pubDate>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{escape(FEED_TITLE)}</title>
    <link>{escape(SOURCE_URL)}</link>
    <atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{escape(SELF_URL)}" rel="self" type="application/rss+xml" />
    <description>{escape(FEED_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>{build_time}</lastBuildDate>
    <generator>Custom scraper (build_feed.py)</generator>{''.join(items_xml)}
  </channel>
</rss>
"""
    print(f"{new_count} new article(s) this run.")
    return rss


def main():
    articles = fetch_articles()
    if not articles:
        print("No articles found — page structure may have changed.", file=sys.stderr)
        sys.exit(1)

    existing_dates = load_existing_pubdates(OUTPUT_PATH)
    rss = build_rss(articles, existing_dates)

    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Wrote {len(articles)} items to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()