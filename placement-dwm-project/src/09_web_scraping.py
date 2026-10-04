"""Optional experiment: extract an HTML table using a CSS selector.

Example: python src/09_web_scraping.py https://example.org/salaries --selector 'table tr'
"""
import argparse
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import TABLE_DIR

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PlacementAnalyticsCourseProject/1.0)"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="public page URL; check its terms and robots.txt first")
    parser.add_argument("--selector", default="table tr", help="CSS selector for table rows")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        parser.error("url must be an absolute http:// or https:// URL")

    response = requests.get(args.url, headers=HEADERS, timeout=(5, 20))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            for row in soup.select(args.selector)]
    rows = [row for row in rows if row]
    if not rows:
        raise SystemExit(f"No table rows found for selector: {args.selector!r}")
    width = max(map(len, rows))
    rows = [row + [""] * (width - len(row)) for row in rows]
    frame = pd.DataFrame(rows[1:], columns=rows[0]) if len(rows) > 1 else pd.DataFrame(rows)
    output = TABLE_DIR / "scraped_data.csv"
    frame.to_csv(output, index=False)
    print(f"Saved {len(frame)} rows to {output}")
    print(frame.head().to_string(index=False))


if __name__ == "__main__":
    main()
