from getpass import getpass
import os
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests


OWNER = "excalidraw"
REPO = "excalidraw"

SNAPSHOT_SHA = "1118751f3e4958a0dc3d71934c093584fdb7c6f5"

START = datetime(2025, 9, 25, 0, 0, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 24, 23, 59, 59, tzinfo=timezone.utc)

API = f"https://api.github.com/repos/{OWNER}/{REPO}"

session = requests.Session()
session.headers.update({
    "Accept": "application/vnd.github+json",
    "User-Agent": "capstone-analysis",
})

# Authentication.
token = os.getenv("GITHUB_TOKEN")

if not token:
    token = getpass("GitHub token (input hidden): ").strip()

if token:
    session.headers["Authorization"] = f"Bearer {token}"


def get_page(url, params=None):
    """Retrieve one GitHub API page and return its data and next-page URL."""

    response = session.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    next_url = response.links.get(
        "next", {}
    ).get("url")

    return data, next_url


activities = []


# 1. COMMITS

print("Collecting commits...")

params = {
    "sha": SNAPSHOT_SHA,
    "since": START.isoformat(),
    "until": END.isoformat(),
    "per_page": 100,
}

url = f"{API}/commits"
batch = 1

while url:

    commits, next_url = get_page(
        url,
        params=params,
    )

    # Parameters are only needed on the first request
    params = None

    print(
        f"  Commit batch {batch}: "
        f"{len(commits)} records"
    )

    for commit in commits:

        date = pd.to_datetime(
            commit["commit"]["committer"]["date"],
            utc=True,
        )

        if commit.get("author"):
            actor = commit["author"]["login"]
        else:
            actor = commit["commit"]["author"]["name"]

        activities.append({
            "type": "Commit",
            "date": date,
            "actor": actor,
            "url": commit["html_url"],
            "description":
                commit["commit"]["message"].split("\n")[0],
        })

    url = next_url
    batch += 1


# 2. PULL REQUESTS

print("Collecting pull requests...")

params = {
    "state": "all",
    "sort": "created",
    "direction": "desc",
    "per_page": 100,
}

url = f"{API}/pulls"
batch = 1

while url:

    pulls, next_url = get_page(
        url,
        params=params,
    )

    params = None

    print(
        f"  PR batch {batch}: "
        f"{len(pulls)} records"
    )

    reached_start = False

    for pull in pulls:

        created = pd.to_datetime(
            pull["created_at"],
            utc=True,
        )

        if created < pd.Timestamp(START):
            reached_start = True
            continue

        if created > pd.Timestamp(END):
            continue

        activities.append({
            "type": "Pull request",
            "date": created,
            "actor": pull["user"]["login"],
            "url": pull["html_url"],
            "description": pull["title"],
        })

    if reached_start:
        break

    url = next_url
    batch += 1


# 3. ISSUES

print("Collecting issues...")

params = {
    "state": "all",
    "sort": "created",
    "direction": "desc",
    "per_page": 100,
}

url = f"{API}/issues"
batch = 1

while url:

    issues, next_url = get_page(
        url,
        params=params,
    )

    params = None

    print(
        f"  Issue batch {batch}: "
        f"{len(issues)} records"
    )

    reached_start = False

    for issue in issues:

        created = pd.to_datetime(
            issue["created_at"],
            utc=True,
        )

        if created < pd.Timestamp(START):
            reached_start = True
            continue

        if created > pd.Timestamp(END):
            continue

        # GitHub's Issues endpoint also returns PRs
        # We exclude them to avoid counting PRs twice
        if "pull_request" in issue:
            continue

        activities.append({
            "type": "Issue",
            "date": created,
            "actor": issue["user"]["login"],
            "url": issue["html_url"],
            "description": issue["title"],
        })

    if reached_start:
        break

    url = next_url
    batch += 1


# CREATE DATAFRAME

df = pd.DataFrame(activities)

df = df.sort_values("date")

df.to_csv(
    "chapter6_all_activities.csv",
    index=False,
)


# TOTAL COUNTS

totals = (
    df["type"]
    .value_counts()
    .reindex(
        ["Commit", "Pull request", "Issue"],
        fill_value=0,
    )
)

print("\n----------------------------------------")
print("TOTAL ACTIVITIES")
print("----------------------------------------")

print(totals)

print(
    f"\nAll activities: {len(df)}"
)


# MONTHLY COUNTS

df["month"] = (
    df["date"]
    .dt.tz_convert("UTC")
    .dt.tz_localize(None)
    .dt.to_period("M")
)

monthly = (
    df.groupby(["month", "type"])
    .size()
    .unstack(fill_value=0)
    .reindex(
        columns=[
            "Commit",
            "Pull request",
            "Issue",
        ],
        fill_value=0,
    )
)

monthly["Total"] = monthly.sum(axis=1)

monthly.to_csv(
    "chapter6_monthly_activity.csv"
)

print("\n----------------------------------------")
print("MONTHLY ACTIVITY")
print("----------------------------------------")

print(monthly)


# PEAK MONTH

peak_month = monthly["Total"].idxmax()
peak_total = monthly.loc[
    peak_month,
    "Total"
]

print("\n----------------------------------------")
print("HIGHEST-ACTIVITY MONTH")
print("----------------------------------------")

print(
    f"{peak_month}: "
    f"{peak_total} activities"
)


# PLOT

plot_data = monthly[
    ["Commit", "Pull request", "Issue"]
].copy()

plot_data.index = plot_data.index.astype(str)

ax = plot_data.plot(
    marker="o",
    figsize=(11, 6),
)

ax.set_title(
    "Excalidraw GitHub activity\n"
    "25 September 2025–24 September 2026"
)

ax.set_xlabel("Month")
ax.set_ylabel("Number of activities")

ax.grid(
    axis="y",
    alpha=0.3,
)

plt.xticks(
    rotation=45,
    ha="right",
)

plt.tight_layout()

plt.savefig(
    "chapter6_activity_plot.png",
    dpi=300,
    bbox_inches="tight",
)

plt.close()


print("\nCreated:")
print("  chapter6_all_activities.csv")
print("  chapter6_monthly_activity.csv")
print("  chapter6_activity_plot.png")