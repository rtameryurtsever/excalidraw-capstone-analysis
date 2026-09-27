# Excalidraw Capstone Analysis

This repository contains the analysis scripts and generated data used for the
Capstone Software Development interim report of Group 41 on Excalidraw.

## Repository snapshot

The static repository analysis refers to the Excalidraw repository at commit:

`1118751f3e4958a0dc3d71934c093584fdb7c6f5`

dated 24 September 2026.

The GitHub activity analyses in Chapters 6–8 use the observation period:

**25 September 2025 – 24 September 2026**

## Scripts

### Chapter 6 — GitHub activity

`chapter6_activity.py`

Retrieves three types of GitHub activity for the observation period:

- commits
- pull requests opened
- issues opened

The script excludes pull requests returned through GitHub's Issues endpoint from
the issue count to avoid double-counting.

It generates:

- `chapter6_all_activities.csv`
- `chapter6_monthly_activity.csv`
- `chapter6_activity_plot.png`

These outputs are used for the activity counts and activity-over-time analysis
in Chapter 6.

### Chapter 7 — Contributors

`chapter7_contributors.py`

Uses `chapter6_all_activities.csv` to:

- count distinct active accounts
- aggregate commits, opened pull requests, and opened issues per account
- rank the top contributors using the same three activity metrics
- retrieve the repository-wide commit-contributor count from GitHub

It generates:

- `chapter7_top10_contributors.csv`

### Chapter 8 — Collaboration

`chapter8.py`

Uses Git commit authors and `Co-authored-by` metadata to identify potential
collaborator pairs during the same one-year observation period.

The script:

- checks out the Excalidraw repository snapshot used in the report
- normalizes selected contributor aliases
- excludes non-human co-authors such as bots and AI tools
- counts contributor pairs appearing together on commits
- supports the counter-example analysis by comparing files changed by selected
  commits

The script was used to identify candidate collaborator pairs only. The evidence
for coordination and awareness in Chapter 8 was established manually by
inspecting GitHub pull-request conversations, reviews, and inline comments.

## GitHub API authentication

The Chapter 6 and Chapter 7 scripts may request a GitHub personal access token
at runtime to avoid the unauthenticated API rate limit. The token is used only
for API authentication and is not stored in the scripts or repository.

## Requirements

The Chapter 6 and Chapter 7 scripts require Python and the packages listed in
`requirements.txt`.

Install them with:

```bash
python -m pip install -r requirements.txt
