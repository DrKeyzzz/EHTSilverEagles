"""Builds index.html: a shareable, self-contained snapshot of the NJ USBands
data for GitHub Pages. Run scraper.fetch_nj_events(), save it to
/tmp/nj_data.json, then run this to regenerate the page, then commit + push.
"""
import json
from pathlib import Path

DATA_PATH = Path("/tmp/nj_data.json")
OUT_PATH = Path(__file__).parent / "index.html"

TEMPLATE = """<!doctype html>
<title>NJ Marching Scores</title>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #faf7f1;
    --surface: #ffffff;
    --surface-2: #f2ecdf;
    --border: #e4dac6;
    --text: #201c14;
    --text-muted: #6f6858;
    --brass: #9c6c1c;
    --brass-soft: #f1e3c4;
    --field: #2c6b4c;
    --field-soft: #dcece2;
    --amber: #91561a;
    --amber-soft: #f3e2c9;
    --slate: #5b6472;
    --slate-soft: #e7e9ee;
    --gold-rank: #8a5a00;
    --silver-rank: #57616f;
    --bronze-rank: #874824;
    --shadow: 0 1px 2px rgba(32,28,20,0.04), 0 8px 20px -12px rgba(32,28,20,0.18);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #12151d;
      --surface: #1a1f2b;
      --surface-2: #212739;
      --border: #2c3345;
      --text: #eef1f7;
      --text-muted: #8b93a8;
      --brass: #dbab48;
      --brass-soft: #3a3220;
      --field: #56aa7d;
      --field-soft: #1e3327;
      --amber: #dda45a;
      --amber-soft: #3a2c18;
      --slate: #a7afc2;
      --slate-soft: #262c3d;
      --gold-rank: #ecc766;
      --silver-rank: #b7bfd1;
      --bronze-rank: #dd9c66;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
    }
  }
  :root[data-theme="dark"] {
    --bg: #12151d;
    --surface: #1a1f2b;
    --surface-2: #212739;
    --border: #2c3345;
    --text: #eef1f7;
    --text-muted: #8b93a8;
    --brass: #dbab48;
    --brass-soft: #3a3220;
    --field: #56aa7d;
    --field-soft: #1e3327;
    --amber: #dda45a;
    --amber-soft: #3a2c18;
    --slate: #a7afc2;
    --slate-soft: #262c3d;
    --gold-rank: #ecc766;
    --silver-rank: #b7bfd1;
    --bronze-rank: #dd9c66;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 24px -12px rgba(0,0,0,0.5);
  }

  * { box-sizing: border-box; }
  html, body { background: var(--bg); }
  body {
    margin: 0;
    padding-inline: 16px;
    padding-block: 20px 48px;
    font-family: "Inter", -apple-system, sans-serif;
    color: var(--text);
    background: var(--bg);
  }
  .wrap { max-width: 760px; margin: 0 auto; }

  .masthead {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    flex-wrap: wrap;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 6px;
  }
  .eyebrow {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--brass);
    font-weight: 600;
    margin: 0 0 6px;
  }
  h1 {
    font-family: "Oswald", sans-serif;
    font-weight: 700;
    font-size: clamp(1.7rem, 5vw, 2.3rem);
    letter-spacing: 0.01em;
    text-transform: uppercase;
    margin: 0;
    text-wrap: balance;
  }
  .snapshot-chip {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.78rem;
    color: var(--text-muted);
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 7px 14px;
    white-space: nowrap;
  }
  .snapshot-chip b { color: var(--text); font-weight: 600; }

  .tracker-panel {
    background: var(--surface-2);
    border: 1px solid var(--brass);
    border-radius: 10px;
    padding: 16px 18px;
    margin: 18px 0 26px;
    box-shadow: var(--shadow);
  }
  .tracker-title {
    font-family: "Oswald", sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--brass);
    margin-bottom: 10px;
  }
  .tracker-row {
    padding: 10px 6px;
    border-bottom: 1px solid var(--border);
    border-radius: 6px;
  }
  .tracker-row:last-child { border-bottom: none; }
  .tracker-row.us-row { background: var(--brass-soft); }
  .tracker-meta {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 4px;
    margin-left: 1.9em;
    white-space: normal;
    overflow-wrap: anywhere;
  }
  .tracker-main {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 10px;
  }
  .tracker-band {
    display: flex;
    gap: 9px;
    align-items: baseline;
    min-width: 0;
  }
  .tracker-rank {
    font-family: "IBM Plex Mono", monospace;
    font-weight: 600;
    flex-shrink: 0;
  }
  .tracker-band-name {
    font-size: 0.92rem;
    overflow-wrap: anywhere;
  }
  .tracker-row.us-row .tracker-band-name,
  .tracker-row.us-row .tracker-rank,
  .tracker-row.us-row .tracker-score { font-weight: 700; }
  .tracker-score {
    font-family: "IBM Plex Mono", monospace;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    flex-shrink: 0;
    white-space: nowrap;
  }
  .tracker-row.rank-1 .tracker-rank, .tracker-row.rank-1 .tracker-band-name, .tracker-row.rank-1 .tracker-score { color: var(--gold-rank); }
  .tracker-row.rank-2 .tracker-rank, .tracker-row.rank-2 .tracker-band-name, .tracker-row.rank-2 .tracker-score { color: var(--silver-rank); }
  .tracker-row.rank-3 .tracker-rank, .tracker-row.rank-3 .tracker-band-name, .tracker-row.rank-3 .tracker-score { color: var(--bronze-rank); }

  .legend {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 0.8rem;
    color: var(--text-muted);
    margin: 14px 0 28px;
  }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .dot.posted { background: var(--field); }
  .dot.pending { background: var(--amber); }
  .dot.upcoming { background: var(--slate); }

  .date-heading {
    font-family: "Oswald", sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 30px 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .date-heading::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  .date-heading:first-of-type { margin-top: 0; }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--slate);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: var(--shadow);
  }
  .card.posted { border-left-color: var(--field); }
  .card.pending { border-left-color: var(--amber); }

  .event-head {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    align-items: flex-start;
  }
  .event-name {
    font-weight: 700;
    font-size: 1.02rem;
    letter-spacing: -0.005em;
  }
  .event-time {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.82rem;
    color: var(--brass);
    font-weight: 600;
    white-space: nowrap;
    text-align: right;
  }
  .event-meta {
    color: var(--text-muted);
    font-size: 0.84rem;
    margin-top: 3px;
  }
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 3px 9px;
    border-radius: 100px;
    margin-left: 9px;
    vertical-align: middle;
    position: relative;
    top: -1px;
  }
  .status-pill.posted { background: var(--field-soft); color: var(--field); }
  .status-pill.pending { background: var(--amber-soft); color: var(--amber); }
  .status-pill.upcoming { background: var(--slate-soft); color: var(--slate); }

  .division { margin-top: 16px; }
  .division-name {
    font-family: "Oswald", sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--brass);
    margin-bottom: 6px;
  }
  table { width: 100%; border-collapse: collapse; }
  th {
    text-align: left;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
    padding: 4px 8px;
    border-bottom: 1px solid var(--border);
  }
  th.num, td.num { text-align: right; }
  td {
    padding: 6px 8px;
    font-size: 0.92rem;
    border-bottom: 1px solid var(--border);
  }
  tbody tr:last-child td { border-bottom: none; }
  td.rank {
    font-family: "IBM Plex Mono", monospace;
    font-weight: 600;
    width: 1.6em;
  }
  td.score {
    font-family: "IBM Plex Mono", monospace;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
  tr.rank-1 td.rank, tr.rank-1 td.score, tr.rank-1 td.band { color: var(--gold-rank); }
  tr.rank-2 td.rank, tr.rank-2 td.score, tr.rank-2 td.band { color: var(--silver-rank); }
  tr.rank-3 td.rank, tr.rank-3 td.score, tr.rank-3 td.band { color: var(--bronze-rank); }
  tr.rank-1 td { font-weight: 700; }

  .empty-msg {
    color: var(--text-muted);
    font-size: 0.88rem;
    font-style: italic;
    margin-top: 10px;
  }

  footer {
    margin-top: 36px;
    padding-top: 16px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.78rem;
    text-align: center;
  }
  footer a { color: var(--brass); text-decoration: none; }
</style>

<div class="wrap">
  <div class="masthead">
    <div>
      <p class="eyebrow">2026 Season &middot; New Jersey</p>
      <h1>Marching Scores</h1>
    </div>
    <div class="snapshot-chip">Snapshot: <b id="fetchedAt">&mdash;</b></div>
  </div>

  <div class="tracker-panel" id="tracker"></div>

  <div class="legend">
    <span class="legend-item"><span class="dot posted"></span> Scores posted</span>
    <span class="legend-item"><span class="dot pending"></span> Awaiting scores</span>
    <span class="legend-item"><span class="dot upcoming"></span> Upcoming</span>
  </div>

  <div id="events"></div>

  <footer>
    Sourced from usbands.org &middot; scores appear once USBands posts them after each class performs.<br>
    This is a snapshot, not a live feed &mdash; ask for a refresh to see the latest results.
  </footer>
</div>

<script>
const DATA = __DATA_JSON__;
const TRACKED_DIVISION = "Open - Group IV";
const HIGHLIGHT_TERM = "egg harbor";

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function fmtFetchedAt(iso) {
  if (!iso) return 'unknown';
  const d = new Date(iso);
  return d.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' });
}

function renderEvent(ev) {
  const hasScores = ev.divisions && ev.divisions.length > 0;
  const statusClass = hasScores ? 'posted' : (ev.is_past ? 'pending' : 'upcoming');
  const statusLabel = hasScores ? 'Scores Posted' : (ev.is_past ? 'Awaiting Scores' : 'Upcoming');

  const card = document.createElement('div');
  card.className = 'card ' + statusClass;

  const head = document.createElement('div');
  head.className = 'event-head';
  head.innerHTML = `
    <div>
      <span class="event-name">${escapeHtml(ev.name)}</span><span class="status-pill ${statusClass}">${statusLabel}</span>
      <div class="event-meta">${escapeHtml(ev.venue || ev.location)} &middot; ${escapeHtml(ev.address || ev.location)}</div>
    </div>
    <div class="event-time">${escapeHtml(ev.time || '')}</div>
  `;
  card.appendChild(head);

  if (hasScores) {
    for (const div of ev.divisions) {
      const block = document.createElement('div');
      block.className = 'division';
      const rows = div.results.map(r => `
        <tr class="rank-${r.rank}">
          <td class="rank">${r.rank}</td>
          <td class="band">${escapeHtml(r.band)}</td>
          <td class="score num">${r.score.toFixed(1)}</td>
        </tr>
      `).join('');
      block.innerHTML = `
        <div class="division-name">${escapeHtml(div.name)}</div>
        <table>
          <thead><tr><th></th><th>Band</th><th class="num">Score</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
      card.appendChild(block);
    }
  } else if (ev.is_past) {
    const msg = document.createElement('div');
    msg.className = 'empty-msg';
    msg.textContent = 'Event has occurred; USBands hasn\\'t posted results yet.';
    card.appendChild(msg);
  }
  return card;
}

function normDivision(name) {
  return name.trim().toLowerCase().replace(/\\s+/g, ' ');
}

function buildTrackerRows() {
  const rows = [];
  for (const ev of DATA.events) {
    for (const div of (ev.divisions || [])) {
      if (normDivision(div.name) === normDivision(TRACKED_DIVISION)) {
        for (const r of div.results) {
          rows.push({ epoch: ev.epoch, date: ev.date, eventName: ev.name, band: r.band, score: r.score });
        }
      }
    }
  }
  // Ranked by score across every NJ event this division has run at, highest first.
  rows.sort((a, b) => b.score - a.score || a.epoch - b.epoch);
  return rows;
}

function renderTracker() {
  const panel = document.getElementById('tracker');
  const rows = buildTrackerRows();
  const title = `<div class="tracker-title">${escapeHtml(TRACKED_DIVISION)} &middot; Leaderboard, High to Low</div>`;
  if (rows.length === 0) {
    panel.innerHTML = title + `<div class="empty-msg">No ${escapeHtml(TRACKED_DIVISION)} scores posted yet this season.</div>`;
    return;
  }
  const body = rows.map((r, i) => {
    const place = i + 1;
    const isUs = r.band.toLowerCase().includes(HIGHLIGHT_TERM);
    const medalClass = place <= 3 ? ` rank-${place}` : '';
    return `
      <div class="tracker-row${medalClass}${isUs ? ' us-row' : ''}">
        <div class="tracker-main">
          <div class="tracker-band">
            <span class="tracker-rank">${place}</span>
            <span class="tracker-band-name">${escapeHtml(r.band)}</span>
          </div>
          <span class="tracker-score">${r.score.toFixed(1)}</span>
        </div>
        <div class="tracker-meta">${escapeHtml(r.eventName)} &middot; ${escapeHtml(r.date)}</div>
      </div>
    `;
  }).join('');
  panel.innerHTML = title + body;
}

function render() {
  document.getElementById('fetchedAt').textContent = fmtFetchedAt(DATA.fetched_at);
  renderTracker();
  const container = document.getElementById('events');
  container.innerHTML = '';
  let lastDate = null;
  for (const ev of DATA.events) {
    if (ev.date && ev.date !== lastDate) {
      const h = document.createElement('div');
      h.className = 'date-heading';
      h.textContent = ev.date;
      container.appendChild(h);
      lastDate = ev.date;
    }
    container.appendChild(renderEvent(ev));
  }
}

render();
</script>
"""


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    data_json = json.dumps(data).replace("</", "<\\/")
    html_out = TEMPLATE.replace("__DATA_JSON__", data_json)
    OUT_PATH.write_text(html_out)
    print(f"Wrote {OUT_PATH} ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()
