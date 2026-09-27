# Chapter 8: how many commits each pair worked on together (author + Co-authored-by)
# Run in the interim_report folder:  python3 chapter8.py
import os, re, subprocess
from collections import Counter
from itertools import combinations

def git(*args):
    return subprocess.run(["git", "-C", "excalidraw", *args], capture_output=True, text=True).stdout

# download the excalidraw repo the first time (takes a minute)
if not os.path.isdir("excalidraw"):
    print("Downloading excalidraw repo...")
    subprocess.run(["git", "clone", "-q", "https://github.com/excalidraw/excalidraw.git"], check=True)

git("checkout", "-q", "1118751f3e4958a0dc3d71934c093584fdb7c6f5")

# people who commit under more than one email -> one GitHub username
ALIASES = {
    "5153846+dwelle@users.noreply.github.com": "dwelle",
    "mark@lazycat.hu": "mtolmacs",
    "viczian.zsolt@gmail.com": "zsviczian",
    "ryan.weihao.di@gmail.com": "ryan-di",
    "ctangonan123@gmail.com": "ctangonan123",
    "barnabas@excalidraw.com": "barnabasmolnar",
    "tamas@excalidraw.com": "tamas-lakatos",
    "anvikudaraya417@gmail.com": "anviik",
    "augustocbx.dev@gmail.com": "augustocbx",
    "augusto.cesar@mpgo.mp.br": "augustocbx",
    "oleksandr.chulkin@yahoo.com": "alechulkin",
    "oleksandr.chulkin@mongodb.com": "alechulkin",
}

def person(name, email):
    email = email.strip().lower()
    if re.search(r"bot|copilot|cursor|claude|anthropic", name + email, re.I):
        return None  # bots and AI tools are not people
    if email in ALIASES:
        return ALIASES[email]
    m = re.match(r"\d+\+(.+)@users\.noreply\.github\.com", email)
    return m.group(1) if m else name.lower()

# one line per commit: author name | author email | co-authors
log = git("log", "--since=2025-09-25", "--until=2026-09-24T23:59:59",
          "--format=%an|%ae|%(trailers:key=Co-authored-by,valueonly,separator=;)")

pairs = Counter()
for line in log.splitlines():
    name, email, coauthors = line.split("|", 2)
    people = {person(name, email)}
    for c in re.findall(r"([^;<]+)<([^>]+)>", coauthors):
        people.add(person(c[0].strip(), c[1]))
    people.discard(None)
    for a, b in combinations(sorted(people, key=str.lower), 2):
        pairs[(a, b)] += 1

print("Pairs that worked on the same commit (25 Sept 2025 - 24 Sept 2026)\n")
for (a, b), n in pairs.most_common():
    print(f"{n:3}  {a} & {b}")

# counter-example: zsviczian & ryan-di
files_9996 = set(git("show", "--name-only", "--format=", "416e8b3e").split())
files_10541 = set(git("show", "--name-only", "--format=", "071b17a2").split())
print("\nCounter-example: ryan-di (#9996) & zsviczian (#10541)")
print("  files both PRs changed:", ", ".join(sorted(files_9996 & files_10541)))
print("  commits together:", pairs[("ryan-di", "zsviczian")])
