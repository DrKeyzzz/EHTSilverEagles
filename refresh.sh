#!/bin/bash
# Manual refresh: scrape usbands.org for NJ events, rebuild index.html, push to GitHub Pages.
# Run this only on demand -- never on a timer -- usbands.org's robots.txt asks bots not to crawl it.
set -e
cd "$(dirname "$0")"

python3 scraper.py > /tmp/nj_data.json
python3 build_site.py
git add index.html
git diff --cached --quiet && { echo "No changes."; exit 0; }
git commit -m "Refresh NJ scores $(date -u +%Y-%m-%dT%H:%MZ)"
git push
echo "Pushed. Live at https://drkeyzzz.github.io/nj-marching-scores/ (may take ~1 min to update)."
