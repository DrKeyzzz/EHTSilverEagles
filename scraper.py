"""Scrapes usbands.org for New Jersey marching band competitions and their posted scores.

Only fetches on demand (no background polling) - each call to fetch_nj_events()
makes one request for the events list plus one request per NJ event found.
"""
from __future__ import annotations

import html as html_module
import re
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

BASE_URL = "https://usbands.org"
EVENTS_URL = f"{BASE_URL}/events/"
DETAIL_URL = f"{BASE_URL}/events/details.php?ID={{event_id}}"

USER_AGENT = (
    "Mozilla/5.0 (compatible; personal-use script checking NJ event results; "
    "run manually, not a crawler)"
)

CARD_RE = re.compile(
    r'<div class="card shadow mb-3 bg-white border-0 shadow" id="event-(?P<id>\d+)" '
    r'data-time="(?P<epoch>\d+)">.*?'
    r'<div class="event(?P<past>\s+past)?">'
    r'(?:<span class="checkmark[^"]*">[^<]*</span>)?'
    r'<a href="details\.php\?ID=\d+"[^>]*class="eventtitle""?\s*>(?P<name>.*?)</a>\s*'
    r'<div class="location">\s*(?P<location>.*?)</div>',
    re.DOTALL,
)

TITLE_RE = re.compile(r'<h1 class="text-white mb-2 event-title">(.*?)</h1>', re.DOTALL)
DATE_RE = re.compile(r'calendar\.svg[^>]*/>\s*([^<]+?)\s*</div>')
TIME_RE = re.compile(r'clock\.svg[^>]*/>\s*([^<]+?)\s*</div>')
VENUE_RE = re.compile(r'class="event-meta__venue[^"]*"[^>]*>.*?/>\s*([^<]+?)\s*</a>', re.DOTALL)
ADDRESS_RE = re.compile(r'class="event-meta__address">([^<]+)</span>')

DIVISION_SPLIT_RE = re.compile(r'<div class="scores-division">')
DIVISION_NAME_RE = re.compile(r'<div class="scores-division__name">(.*?)</div>', re.DOTALL)
ROW_RE = re.compile(
    r'<div class="scores-cell scores-rank"><span class="rank-num">(?P<rank>\d+)</span></div>'
    r'<div class="scores-cell scores-band">'
    r'(?:<a[^>]*>(?P<band_a>.*?)</a>|<div class="band-name">(?P<band_div>.*?)</div>|(?P<band_plain>[^<]*))'
    r'</div>'
    r'<div class="scores-cell scores-score">(?P<score>[\d.]+)</div>',
    re.DOTALL,
)


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _clean(text: str) -> str:
    return html_module.unescape(re.sub(r"\s+", " ", text)).strip()


@dataclass
class ScoreRow:
    rank: int
    band: str
    score: float


@dataclass
class Division:
    name: str
    results: list[ScoreRow] = field(default_factory=list)


@dataclass
class EventSummary:
    id: int
    name: str
    location: str
    epoch: int
    is_past: bool


@dataclass
class EventDetail:
    id: int
    name: str
    location: str
    epoch: int
    is_past: bool
    date: str = ""
    time: str = ""
    venue: str = ""
    address: str = ""
    divisions: list[Division] = field(default_factory=list)
    url: str = ""
    error: str | None = None


def fetch_event_list() -> list[EventSummary]:
    html_text = _fetch(EVENTS_URL)
    events = []
    for m in CARD_RE.finditer(html_text):
        events.append(
            EventSummary(
                id=int(m.group("id")),
                name=_clean(m.group("name")),
                location=_clean(m.group("location")),
                epoch=int(m.group("epoch")),
                is_past=bool(m.group("past")),
            )
        )
    return events


def fetch_event_detail(summary: EventSummary) -> EventDetail:
    url = DETAIL_URL.format(event_id=summary.id)
    detail = EventDetail(
        id=summary.id,
        name=summary.name,
        location=summary.location,
        epoch=summary.epoch,
        is_past=summary.is_past,
        url=url,
    )
    try:
        html_text = _fetch(url)
    except Exception as exc:  # network hiccup on one event shouldn't kill the batch
        detail.error = str(exc)
        return detail

    title_m = TITLE_RE.search(html_text)
    if title_m:
        detail.name = _clean(title_m.group(1))
    date_m = DATE_RE.search(html_text)
    if date_m:
        detail.date = _clean(date_m.group(1))
    time_m = TIME_RE.search(html_text)
    if time_m:
        detail.time = _clean(time_m.group(1))
    venue_m = VENUE_RE.search(html_text)
    if venue_m:
        detail.venue = _clean(venue_m.group(1))
    addr_m = ADDRESS_RE.search(html_text)
    if addr_m:
        detail.address = _clean(addr_m.group(1))

    scores_idx = html_text.find('class="scores-tab"')
    if scores_idx != -1:
        # Scores tab runs until the next sibling tab-pane closes; grab a generous window.
        scores_html = html_text[scores_idx : scores_idx + 20000]
        end_idx = scores_html.find('<div class="tab-pane')
        if end_idx != -1:
            scores_html = scores_html[:end_idx]

        chunks = DIVISION_SPLIT_RE.split(scores_html)[1:]  # drop preamble before first division
        for chunk in chunks:
            name_m = DIVISION_NAME_RE.search(chunk)
            if not name_m:
                continue
            division = Division(name=_clean(name_m.group(1)))
            for row_m in ROW_RE.finditer(chunk):
                band = row_m.group("band_a") or row_m.group("band_div") or row_m.group("band_plain") or ""
                division.results.append(
                    ScoreRow(
                        rank=int(row_m.group("rank")),
                        band=_clean(band),
                        score=float(row_m.group("score")),
                    )
                )
            if division.results:
                division.results.sort(key=lambda r: r.rank)
                detail.divisions.append(division)

    return detail


def is_nj(summary: EventSummary) -> bool:
    return summary.location.strip().upper().endswith(", NJ")


def fetch_nj_events() -> dict:
    """Single entry point: fetch the events list, keep NJ-only, fetch each detail page.

    Returns a JSON-serializable dict with a fetched_at timestamp and the event list.
    """
    all_events = fetch_event_list()
    nj_events = [e for e in all_events if is_nj(e)]

    details = [fetch_event_detail(e) for e in nj_events]
    details.sort(key=lambda d: d.epoch)

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": len(details),
        "events": [_event_to_dict(d) for d in details],
    }


def _event_to_dict(d: EventDetail) -> dict:
    payload = asdict(d)
    return payload


if __name__ == "__main__":
    import json

    print(json.dumps(fetch_nj_events(), indent=2))
