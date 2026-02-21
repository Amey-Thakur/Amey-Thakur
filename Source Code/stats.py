"""
================================================================================
FILE NAME      : stats.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
I developed this module to analyze my GitHub profile data. It pulls together 
my stars, commits, PRs, and issues, then turns them into a high-quality SVG 
dashboard that I use on my profile README.

TECH STACK     : 
- Python 3     : Handles all the logic, API calls, and data processing.
- GitHub API   : My primary source for repo and interaction data.
- SVG (XML)    : Used for rendering the actual visual dashboard.

HOW IT WORKS   :
1. AUTHENTICATION : I pull my GITHUB_TOKEN so I can make verified API calls.
2. DISCOVERY      : I loop through all my repos, making sure to handle pagination 
                    so I don't miss any data.
3. INFERENCE      : I check my PR history to see which unique projects I've 
                    actually impacted.
4. CALCULATIONS   : I apply a custom grading model (A+, A, etc.) that rewards 
                    contributions and real work over just star counts.
5. RESILIENCE     : I added a local cache (stats_cache.json) as a backup. If the 
                    GitHub API is ever down, the card stays updated with the 
                    last good data instead of breaking.
6. VISUALIZATION  : Everything gets packed into a clean SVG with a custom 
                    percentile ring.
================================================================================
"""

import os
import json
import urllib.request
import re
import subprocess
from datetime import datetime, timezone, timedelta

# ==============================================================================
# CONFIGURATION & ASSETS
# ==============================================================================

# Backup data store to prevent profile blackouts if the API fails.
CACHE_FILE = "docs/stats_cache.json"

# These are the raw SVG paths for my dashboard icons. 
# I swap in a {color} tag so the icons match my theme.
ICONS = {
    "star":    '<path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="none" stroke="{color}" stroke-width="1.2"/>',
    "commit":  '<path d="M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z" fill="{color}"/><path d="M8 3.5a.75.75 0 01.75.75v3.5h2.5a.75.75 0 010 1.5h-3.25a.75.75 0 01-.75-.75v-4.25a.75.75 0 01.75-.75z" fill="{color}"/>',
    "pr":      '<path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5a2.5 2.5 0 00-2.5-2.5zm-7.5 10a.75.75 0 100 1.5.75.75 0 000-1.5zM12 12.5a.75.75 0 100 1.5.75.75 0 000-1.5z" fill="none" stroke="{color}" stroke-width="1.2"/>',
    "issue":   '<path d="M8 15A7 7 0 108 1a7 7 0 000 14zm0 1A8 8 0 118 0a8 8 0 010 16z" fill="{color}"/><path d="M7.002 11a1 1 0 112 0 1 1 0 01-2 0zM7.1 4h1.8l-.45 6h-.9L7.1 4z" fill="{color}"/>',
    "contrib": '<path d="M2 1.75C2 .784 2.784 0 3.75 0h8.5C13.216 0 14 .784 14 1.75v11.5A1.75 1.75 0 0112.25 15h-8.5A1.75 1.75 0 012 13.25V1.75zM3.5 1.75v11.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V1.75a.25.25 0 00-.25-.25h-8.5a.25.25 0 00-.25.25z" fill="{color}"/><path d="M5 3h6v1.5H5V3zm0 3h6v1.5H5V6z" fill="{color}"/>'
}

# ==============================================================================
# DATA RETRIEVAL CORE
# ==============================================================================

def fetch_data(url, token):
    """
    Standard function I use to talk to the GitHub API. 
    I'm using urllib because it's built into Python and keeps the script fast.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # I always use a token to get higher rate limits and to see 
    # my private work stats properly.
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        # If this fails, the main loop catches it and falls back to the cache.
        return None


# ==============================================================================
# ANALYTICAL LOGIC
# ==============================================================================

def calculate_grade(stats):
    """
    This is my grading formula. I decided to give higher weights to PRs 
    and community contributions because they prove real engineering activity 
    better than just collecting stars.
    """
    stars = int(stats.get('stars', 0))
    
    # Cleaning up the commit count so I can do math on it.
    commit_raw = str(stats.get('commits', '0'))
    commits = float(commit_raw.replace('k+', '').replace('k', '')) * 1000 if 'k' in commit_raw else float(commit_raw)
    
    prs      = int(stats.get('prs', 0))
    issues   = int(stats.get('issues', 0))
    contribs = int(stats.get('contribs', 0))
    
    # MY SCORING MODEL:
    # stars (x10) | commits (1.5) | PRs (x50) | Issues (x5) | Contribs (x100)
    score = (stars * 10) + (commits * 1.5) + (prs * 50) + (issues * 5) + (contribs * 100)
    
    # Thresholds I set based on high-impact profile activity.
    if score > 20000: return "A+", 98
    if score > 15000: return "A",  90
    if score > 10000: return "A-", 80
    if score > 5000:  return "B+", 65
    if score > 2000:  return "B",  50
    return "C", 30


def create_stats_svg(stats, username):
    """
    This builds the actual SVG card. I use a clean Segoe UI font and 
    a custom circular rank meter for a professional developer look.
    """
    accent, bg, white = "#00D4FF", "#000000", "#F0F6FC"
    grade, rank = calculate_grade(stats)
    
    # SVG with localized styles and a dynamic progress ring.
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title  {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {accent}; }}
        .header {{ font: 700 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .stat   {{ font: 900 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .grade  {{ font: 900 34px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .rank   {{ font: italic 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.45; }}
    </style>
    
    <!-- Main Background - Borderless Black -->
    <rect width="495" height="195" rx="10" fill="{bg}"/>
    <text x="30" y="38" class="title">{username}'s GitHub Stats</text>
    
    <!-- My Stats Data -->
    <g transform="translate(30, 65)">
        <g transform="translate(0, 0)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['star'].format(color=accent)}</svg>
            <text x="35" y="0" class="header">Total Stars:</text>
            <text x="220" y="0" class="stat">{stats.get('stars', '---')}</text>
        </g>
        <g transform="translate(0, 26)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['commit'].format(color=accent)}</svg>
            <text x="35" y="0" class="header">Total Commits:</text>
            <text x="220" y="0" class="stat">{stats.get('commits', '---')}</text>
        </g>
        <g transform="translate(0, 52)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['pr'].format(color=accent)}</svg>
            <text x="35" y="0" class="header">Total PRs:</text>
            <text x="220" y="0" class="stat">{stats.get('prs', '---')}</text>
        </g>
        <g transform="translate(0, 78)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['issue'].format(color=accent)}</svg>
            <text x="35" y="0" class="header">Total Issues:</text>
            <text x="220" y="0" class="stat">{stats.get('issues', '---')}</text>
        </g>
        <g transform="translate(0, 104)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['contrib'].format(color=accent)}</svg>
            <text x="35" y="0" class="header">Contributor to:</text>
            <text x="220" y="0" class="stat">{stats.get('contribs', '---')}</text>
        </g>
    </g>
    
    <!-- Rank Ring Animation (Dasharray math for the percentile circle) -->
    <g transform="translate(400, 105)">
        <circle r="44" stroke="{accent}" stroke-width="4.5" fill="none" opacity="0.1"/>
        <circle r="44" stroke="{accent}" stroke-width="4.5" fill="none" 
                stroke-dasharray="276.46" stroke-dashoffset="{276.46 * (1 - rank/100)}" 
                stroke-linecap="round" transform="rotate(-90)"/>
        <text text-anchor="middle" dy="0.35em" class="grade">{grade}</text>
    </g>
    
    <text x="400" y="180" text-anchor="middle" class="rank">Now or Never</text>
</svg>'''
    return svg


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def update_readme(timestamp):
    """
    I update the README URLs with a timestamp to force GitHub to refresh 
    the images instead of showing a cached version.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    
    with open(readme_path, "r", encoding="utf-8") as f: 
        content = f.read()
        
    # Swapping in the new ?t=<timestamp> query string.
    content = re.sub(r'docs/stats\.svg(\?t=\d+)?', f'docs/stats.svg?t={timestamp}', content)
    
    with open(readme_path, "w", encoding="utf-8") as f: 
        f.write(content)


def get_local_hour():
    """
    I use my last Git commit to figure out my local timezone offset. 
    This way the script runs exactly at midnight for me, wherever I am.
    """
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%ai'], capture_output=True, text=True, check=True)
        match  = re.search(r'([+-])(\d{2})(\d{2})$', result.stdout.strip())
        
        if not match: 
            return datetime.now(timezone.utc).hour
            
        sign, h, m = match.groups()
        offset = (int(h) * 3600 + int(m) * 60) * (-1 if sign == '-' else 1)
        
        return datetime.now(timezone(timedelta(seconds=offset))).hour
    except Exception:
        return datetime.now(timezone.utc).hour


# ==============================================================================
# MAIN EXECUTION FLOW
# ==============================================================================

def main():
    token    = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    stats    = {"stars": 0, "commits": 0, "prs": 0, "issues": 0, "contribs": 0}
    
    # I only want this to run at 12 AM/PM when triggered on a schedule.
    # If I run it manually or push a change, it bypasses this check.
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Skipping: It's {local_hour} locally, not midnight or noon.")
        return

    try:
        # STEP 1: Scan all my repos.
        all_repos = []
        page = 1
        while True:
            repos = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not repos: break
            all_repos.extend(repos)
            if len(repos) < 100: break
            page += 1
            
        if not all_repos:
            raise Exception("API Discovery Failed")

        stats["stars"]  = sum(r.get('stargazers_count', 0) for r in all_repos)
        stats["issues"] = sum(r.get('open_issues_count', 0) for r in all_repos)
        
        # STEP 2: Figure out how many unique projects I've contributed to.
        pr_search = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        if pr_search:
            stats["prs"] = pr_search.get('total_count', 0)
            unique_contexts = set()
            for r in all_repos: unique_contexts.add(r.get('owner', {}).get('login'))
            for item in pr_search.get('items', []):
                repo_url = item.get('repository_url', '')
                match = re.search(r'/repos/([^/]+)/', repo_url)
                if match: unique_contexts.add(match.group(1))
            
            # I exclude my own profile so this only counts *external* project impact.
            stats["contribs"] = max(1, len(unique_contexts) - (1 if username in unique_contexts else 0))

        # STEP 3: Handle the commit count baseline. 
        # I set this to 17,000 to cover my legacy work from 2019 onwards.
        baseline_commits = int(os.getenv('COMMIT_BASELINE', 17000))
        commit_data      = fetch_data(f"https://api.github.com/search/commits?q=author:{username}", token)
        raw_commits       = commit_data.get('total_count', 0) if commit_data else 0
        
        # Adding live API data to my baseline.
        final_count = max(raw_commits, baseline_commits + (raw_commits % 1000 if raw_commits > 0 else 0))
        formatted_c = final_count / 1000
        stats["commits"] = f"{formatted_c:g}k+" if final_count >= 1000 else str(final_count)

        # STEP 4: Save everything. I update the backup cache file first.
        os.makedirs("docs", exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f)

        # Write the final SVG.
        with open("docs/stats.svg", "w", encoding="utf-8") as f: 
            f.write(create_stats_svg(stats, username))
            
        update_readme(int(datetime.now().timestamp()))
        print(f"Done! My commits are now at: {stats['commits']}")
        
    except Exception as e:
        # If the API hits a rate limit, I fall back to my last saved cache.
        print(f"API Error: {e}. I'm loading my backup data instead.")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
            
            os.makedirs("docs", exist_ok=True)
            with open("docs/stats.svg", "w", encoding="utf-8") as f:
                f.write(create_stats_svg(stats, username))
            print("Successfully restored my stats from cache.")
        else:
            print("Serious Error: No live data and no cache found.")

if __name__ == "__main__": 
    main()
