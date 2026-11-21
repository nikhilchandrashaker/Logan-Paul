# Logan Paul: Vine to Now

A social media analytics project covering Logan Paul's career from his first Vine (2013) to November 2026. It asks one question: how did his audience grow across platforms, and what does the growth curve look like around the big business and controversy moments?

## What's in the folder

| File | What it is |
|---|---|
| `platform_snapshots.csv` | 47 follower, subscriber, view and engagement counts (44 dated, 3 undated), each with a source URL and confidence |
| `events.csv` | 37 dated career events grouped into six eras |
| `eras.csv` | Era definitions (Vine rise, YouTube vlog boom, Controversy & reset, Entrepreneur pivot, Prime & WWE ascent, Mogul era) |
| `ventures.csv` | Business ventures with the metrics reported for each and how reliable they are |
| `analysis.py` | Reads the CSVs and writes the outputs below |
| `yt_growth_intervals.csv` | Main-channel subscriber growth between consecutive snapshots |
| `latest_snapshot.csv` | Most recent count per account |
| `events_by_era.csv` | Event counts by era and category |
| `summary.json` | Headline stats used by the dashboard |
| `dashboard.html` | Interactive dashboard (also published as an artifact) |

Run `python analysis.py` (needs pandas) to regenerate the outputs.

## Headline results

- The main YouTube channel reached 10M subscribers in 333 days (Aug 2017), the fastest in YouTube history per YouTube. Peak pace was about 1.5M subscribers per 30 days.
- Pace fell in every later interval. It was about 857K per 30 days before the Jan 2018 YouTube sanctions and about 541K after, but daily vlogging also ended in May 2018, so the data cannot separate the two.
- The channel sits at 23.6M subscribers (Nov 2, 2026) and gained 0 in the prior 28 days. Since June 2022 it added about 200K subscribers in 53 months, which is within the rounding of the sources.
- The channel still gets about 8.5M views per 28 days (roughly 111M a year, 1.8% of its 6.23B lifetime views).
- Instagram grew from about 22.99M (Jun 2022) to 25.9M (Sep 2026).

## Method

1. Counts and events were collected from published sources (trackers such as vidIQ and Social Blade, press coverage, WWE and court-reporting sites). Every row carries `source_url` and a `confidence` of high, medium or low.
2. Growth between snapshots is `gain / days * 30`. Intervals whose gain is 100K or less are flagged `within_rounding` because most sources round to 0.1M.
3. Era boundaries are defined in `eras.csv` and every event is assigned to one era.

## Limitations

- No platform APIs were used, so there is no video-level data (views, likes, upload cadence). Counts come from third-party trackers and press.
- Coverage is thin for 2019 to 2021 (one subscriber snapshot, April 2020).
- Vine totals at shutdown range from 9.3M to 9.47M across sources.
- Sources conflict on when his WWE contract began (2022 or 2023).
- Prime Hydration sales figures are claims or press estimates, not audited. CryptoZoo litigation entries are allegations and procedural events; Paul has denied wrongdoing.
- Timing overlaps are correlations and do not show cause.

## Next steps

- Pull video-level data from the YouTube Data API (views, likes, comments, upload dates) to test whether upload cadence or format explains the slowdown.
- Fill 2019 to 2021 using Wayback Machine captures of Social Blade pages.
- Add TikTok and X time series.
