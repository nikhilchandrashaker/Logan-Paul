"""
Logan Paul social media analytics: Vine (2013) to now (Nov 2026).

Reads the CSVs in this folder and writes:
  yt_growth_intervals.csv  main-channel subscriber growth between snapshots
  events_by_era.csv        event counts by era and category
  latest_snapshot.csv      most recent follower/subscriber count per account
  summary.json             headline stats (feeds the dashboard)

Run:  python analysis.py
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent

snap = pd.read_csv(HERE / "platform_snapshots.csv", parse_dates=["snapshot_date"])
events = pd.read_csv(HERE / "events.csv", parse_dates=["event_date"])
eras = pd.read_csv(HERE / "eras.csv", parse_dates=["start_date", "end_date"])

MAIN = "Logan Paul Vlogs"
ROUNDING_FLOOR = 100_000  # most sources round to 0.1M, so smaller gains are noise


def era_for(d):
    for _, r in eras.iterrows():
        if r.start_date <= d <= r.end_date:
            return r.era_name
    return None


def val(platform, account, metric, date):
    m = snap[
        (snap.platform == platform)
        & (snap.account == account)
        & (snap.metric == metric)
        & (snap.snapshot_date == pd.Timestamp(date))
    ]
    return float(m.value.iloc[0])


# 1. Main-channel subscriber growth between consecutive snapshots ------------
yt = (
    snap[(snap.platform == "YouTube") & (snap.account == MAIN) & (snap.metric == "subscribers")]
    .dropna(subset=["snapshot_date"])
    .sort_values("snapshot_date")
    .reset_index(drop=True)
)
rows = []
for i in range(len(yt) - 1):
    a, b = yt.loc[i], yt.loc[i + 1]
    days = (b.snapshot_date - a.snapshot_date).days
    gain = int(b.value - a.value)
    rows.append(
        {
            "start": a.snapshot_date.date().isoformat(),
            "end": b.snapshot_date.date().isoformat(),
            "days": days,
            "subs_start": int(a.value),
            "subs_end": int(b.value),
            "gain": gain,
            "gain_per_30d": round(gain / days * 30),
            "era_at_end": era_for(b.snapshot_date),
            "within_rounding": abs(gain) <= ROUNDING_FLOOR,
        }
    )
intervals = pd.DataFrame(rows)
intervals.to_csv(HERE / "yt_growth_intervals.csv", index=False)

# 2. Latest dated count per account ------------------------------------------
latest = (
    snap.dropna(subset=["snapshot_date"])
    .query("metric in ['subscribers', 'followers']")
    .sort_values("snapshot_date")
    .groupby(["platform", "account"], as_index=False)
    .last()[["platform", "account", "metric", "value", "snapshot_date", "confidence"]]
)
latest.to_csv(HERE / "latest_snapshot.csv", index=False)

# 3. Events by era and category ----------------------------------------------
by_era = pd.crosstab(events.era, events.category)
by_era = by_era.reindex(eras.era_name)
by_era.to_csv(HERE / "events_by_era.csv")

# 4. Headline stats ------------------------------------------------------------
yt_2022 = val("YouTube", MAIN, "subscribers", "2022-06-01")
yt_now = val("YouTube", MAIN, "subscribers", "2026-11-02")
plateau_months = (pd.Timestamp("2026-11-02") - pd.Timestamp("2022-06-01")).days / 30.44
vine_peak = val("Vine", "Logan Paul", "followers", "2017-01-01")
views_total = val("YouTube", MAIN, "total_views", "2026-11-02")
views_28d = val("YouTube", MAIN, "views_last_28d", "2026-11-02")
annualized_views = views_28d * 365 / 28

pre = intervals[intervals.start == "2017-09-13"].iloc[0]
post = intervals[intervals.start == "2018-01-10"].iloc[0]
peak = intervals.loc[intervals.gain_per_30d.idxmax()]

summary = {
    "as_of": "2026-11-02",
    "youtube_main_subscribers": int(yt_now),
    "youtube_main_total_views": int(views_total),
    "vine_followers_at_shutdown": int(vine_peak),
    "youtube_to_vine_ratio": round(yt_now / vine_peak, 2),
    "days_to_10m_subscribers": 333,
    "lifetime_views_per_subscriber": round(views_total / yt_now, 1),
    "views_last_28d": int(views_28d),
    "annualized_views_at_current_pace": int(annualized_views),
    "annualized_pace_pct_of_lifetime_views": round(annualized_views / views_total * 100, 2),
    "subs_gained_last_28d": 0,
    "peak_growth": {
        "window": f"{peak.start} to {peak.end}",
        "gain_per_30d": int(peak.gain_per_30d),
    },
    "plateau": {
        "from": "2022-06-01",
        "to": "2026-11-02",
        "months": round(plateau_months, 1),
        "subs_gained": int(yt_now - yt_2022),
        "gain_per_30d": round((yt_now - yt_2022) / plateau_months),
        "note": "Sources round to 0.1M, so the true gain could be roughly 0.1M to 0.3M",
    },
    "controversy_window": {
        "before_gain_per_30d": int(pre.gain_per_30d),
        "after_gain_per_30d": int(post.gain_per_30d),
        "note": "Correlation only: daily vlogging also ended in May 2018 and growth was already slowing",
    },
    "event_count": int(len(events)),
    "snapshot_rows": int(len(snap)),
}
(HERE / "summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
print()
print(intervals.to_string(index=False))
