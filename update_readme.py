"""
Auto-updates the Projects section of README.md using GitHub API.
Run by GitHub Actions daily.
"""

import os
import re
import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "Chaitu0304")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# Repos to always show first (your best work)
FEATURED = ["PGLIFE", "Future-Track", "Smart-Instore-Navigation"]
# Repos to skip (profile README repo itself, forks you don't want shown)
SKIP = ["Chaitu0304"]

LANG_EMOJI = {
    "PHP": "🐘", "JavaScript": "🟨", "TypeScript": "🔷",
    "Python": "🐍", "HTML": "🌐", "CSS": "🎨",
    "Java": "☕", "C": "⚙️", "C++": "⚙️", "Shell": "🐚",
}

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def build_projects_section(repos):
    featured_rows = []
    other_rows = []

    for repo in repos:
        name = repo["name"]
        if name in SKIP or repo.get("fork"):
            continue

        url = repo["html_url"]
        desc = repo.get("description") or "—"
        lang = repo.get("language") or "—"
        stars = repo["stargazers_count"]
        emoji = LANG_EMOJI.get(lang, "📁")
        star_str = f"⭐ {stars}" if stars > 0 else "—"

        row = f"| {emoji} [**{name}**]({url}) | {desc} | {lang} | {star_str} |"

        if name in FEATURED:
            featured_rows.append((FEATURED.index(name), row))
        else:
            other_rows.append(row)

    featured_rows.sort(key=lambda x: x[0])
    featured_sorted = [r for _, r in featured_rows]

    featured_table = (
        "| # | Project | Description | Tech | Stars |\n"
        "|---|---------|-------------|------|-------|\n"
        + "\n".join(f"| {i+1} {r.split('|', 1)[1]}" for i, r in enumerate(featured_sorted))
    )

    other_table = (
        "| # | Project | Description | Tech |\n"
        "|---|---------|-------------|------|\n"
        + "\n".join(f"| {i+len(featured_sorted)+1} {r.split('|', 1)[1].rsplit('|', 1)[0]}|" for i, r in enumerate(other_rows))
    )

    return f"""## 🚀 Projects

> Auto-updated via GitHub Actions · Last refresh: {__import__('datetime').date.today()}

### 🌟 Featured Projects

{featured_table}

### 🔧 All Other Projects

{other_table}

> 💡 *More projects coming soon — actively building!*"""

def update_readme(section_md):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Replace everything between ## 🚀 Projects and the next ## heading
    pattern = r"(## 🚀 Projects.*?)(?=\n---|\n## )"
    new_content = re.sub(pattern, section_md, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README.md updated successfully.")

if __name__ == "__main__":
    print(f"🔍 Fetching repos for {USERNAME}...")
    repos = fetch_repos()
    print(f"📦 Found {len(repos)} repositories.")
    section = build_projects_section(repos)
    update_readme(section)
