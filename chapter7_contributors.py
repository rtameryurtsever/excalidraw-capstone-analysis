import os
from getpass import getpass

import pandas as pd
import requests


OWNER = "excalidraw"
REPO = "excalidraw"

# LOAD CHAPTER 6 DATA

df = pd.read_csv("chapter6_all_activities.csv")

activity_order = [
    "Commit",
    "Pull request",
    "Issue",
]

# Number of distinct accounts appearing in the three measured activities during the one-year period
active_accounts = df["actor"].nunique()

print("----------------------------------------")
print("ONE-YEAR ACTIVE ACCOUNTS")
print("----------------------------------------")
print(active_accounts)


# TOP CONTRIBUTORS DURING THE YEAR

contributor_table = (
    df.groupby(["actor", "type"])
      .size()
      .unstack(fill_value=0)
      .reindex(
          columns=activity_order,
          fill_value=0,
      )
)

contributor_table["Total"] = (
    contributor_table["Commit"]
    + contributor_table["Pull request"]
    + contributor_table["Issue"]
)

# Rank by total observed activities
# Tie-break using commits, then PRs, then issues
contributor_table = contributor_table.sort_values(
    by=[
        "Total",
        "Commit",
        "Pull request",
        "Issue",
    ],
    ascending=False,
)

top10 = contributor_table.head(10)

print("\n----------------------------------------")
print("TOP 10")
print("----------------------------------------")
print(top10)

top10.to_csv(
    "chapter7_top10_contributors.csv"
)


# REPOSITORY-WIDE COMMIT CONTRIBUTORS

token = os.getenv("GITHUB_TOKEN")

if not token:
    token = getpass(
        "GitHub token (input hidden): "
    ).strip()

session = requests.Session()

session.headers.update({
    "Accept": "application/vnd.github+json",
    "User-Agent": "capstone-analysis",
})

if token:
    session.headers["Authorization"] = (
        f"Bearer {token}"
    )


def get_page(url, params=None):
    response = session.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return (
        response.json(),
        response.links.get(
            "next", {}
        ).get("url"),
    )


url = (
    f"https://api.github.com/repos/"
    f"{OWNER}/{REPO}/contributors"
)

params = {
    "anon": "1",
    "per_page": 100,
}

contributors = []

while url:

    data, next_url = get_page(
        url,
        params=params,
    )

    params = None

    contributors.extend(data)

    url = next_url


print("\n----------------------------------------")
print("ALL-TIME COMMIT CONTRIBUTORS")
print("----------------------------------------")
print(len(contributors))