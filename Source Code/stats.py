"""
================================================================================
FILE NAME      : stats.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
Statistical analysis module for the synthesis of GitHub performance metrics. 
Aggregates quantitative markers (Stars, Commits, Pull Requests, Issues) into 
a visually calibrated SVG dashboard for profile documentation.

TECH STACK     : 
- Python 3     : Core logic and data processing.
- GitHub API   : Primary source for repository and interaction metadata.
- SVG (XML)    : Vector-based graphical rendering for high-definition displays.

HOW IT WORKS   :
1. AUTHENTICATION : Loads a GITHUB_TOKEN for verified API access.
2. DISCOVERY      : Polls the repository list with pagination to ensure 
                    comprehensive data capture.
3. INFERENCE      : Analyzes Pull Request history to identify unique 
                    repository contexts.
4. CALCULATIONS   : Applies a weighted grading system to assign a performance 
                    rank based on contribution volume.
5. RESILIENCE     : Utilizes a local cache (stats_cache.json) to serve fallback 
                    data if the GitHub API is unavailable.
6. VISUALIZATION  : Synthesizes data into a professional SVG with dynamic 
                    progress rings and iconography.
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

# Backup data store used to prevent profile blackouts if the API is restricted.
CACHE_FILE = "docs/stats_cache.json"

# Vector paths for dashboard icons. {color} acts as a placeholder for 
# theme-consistent rendering.
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
    Executes an authenticated HTTP GET request to the GitHub API. 
    Urllib is utilized to maintain a minimal dependency footprint.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # Authenticated requests enable higher rate limits and access to 
    # private repository metrics.
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        # Fallback to Resilience Layer if network errors occur.
        return None


# ==============================================================================
# ANALYTICAL LOGIC
# ==============================================================================

def calculate_grade(stats):
    """
    Assigns a performance tier using a weighted scoring algorithm. 
    The logic prioritizes Pull Requests and ecosystem contributions 
    to reward active engineering over passive metrics.
    """
    stars = int(stats.get('stars', 0))
    
    # Normalizes commit strings (e.g., "10k+") for numerical synthesis.
    commit_raw = str(stats.get('commits', '0'))
    commits = float(commit_raw.replace('k+', '').replace('k', '')) * 1000 if 'k' in commit_raw else float(commit_raw)
    
    prs      = int(stats.get('prs', 0))
    issues   = int(stats.get('issues', 0))
    contribs = int(stats.get('contribs', 0))
    
    # SCORING PARAMETERS:
    # stars (x10) | commits (1.5) | PRs (x50) | Issues (x5) | Contribs (x100)
    score = (stars * 10) + (commits * 1.5) + (prs * 50) + (issues * 5) + (contribs * 100)
    
    # Performance thresholds calibrated for high-volume profiles.
    if score > 20000: return "A+", 98
    if score > 15000: return "A",  90
    if score > 10000: return "A-", 80
    if score > 5000:  return "B+", 65
    if score > 2000:  return "B",  50
    return "C", 30


def create_stats_svg(stats, username):
    """
    Constructs the SVG visual using standard typography and geometry. 
    A borderless black aesthetic is used for seamless profile integration.
    """
    accent, bg, white = "#00D4FF", "#000000", "#F0F6FC"
    grade, rank = calculate_grade(stats)
    
    # SVG definition with embedded styles and dynamic progress ring.
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title  {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {accent}; }}
        .header {{ font: 700 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .stat   {{ font: 900 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .grade  {{ font: 900 34px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .rank   {{ font: italic 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.45; }}
    </style>
    
    <!-- Background Frame -->
    <rect width="495" height="195" rx="10" fill="{bg}"/>
    <text x="30" y="38" class="title" fill="{accent}">{username}'s GitHub Stats</text>
    
    <!-- Quantitative Metrics Analysis -->
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
    
    <!-- Percentile Visualization (Dasharray calculation for progress ring) -->
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
    Applies a cache-busting timestamp to the README image URLs. 
    This bypasses the GitHub Camo proxy image cache.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    
    with open(readme_path, "r", encoding="utf-8") as f: 
        content = f.read()
        
    # Updates the ?t=<timestamp> query string via regex substitution.
    content = re.sub(r'docs/stats\.svg(\?t=\d+)?', f'docs/stats.svg?t={timestamp}', content)
    
    with open(readme_path, "w", encoding="utf-8") as f: 
        f.write(content)


def get_local_hour():
    """
    Detects the local hour by parsing the timezone offset from the latest 
    Git commit. Ensures temporal alignment without regional hardcoding.
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
    
    # Execution is gated at 12 AM/PM for scheduled runs to optimize resource 
    # usage. Manual or Push events bypass this gate.
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Scheduled run bypassed for local hour {local_hour}.")
        return

    try:
        # STEP 1: PORTFOLIO SCAN
        all_repos = []
        page = 1
        while True:
            repos = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not repos: break
            all_repos.extend(repos)
            if len(repos) < 100: break
            page += 1
            
        if not all_repos:
            raise Exception("No repository data retrieved.")

        stats["stars"]  = sum(r.get('stargazers_count', 0) for r in all_repos)
        stats["issues"] = sum(r.get('open_issues_count', 0) for r in all_repos)
        
        # STEP 2: IMPACT ANALYSIS
        # Aggregates unique repository contexts from Pull Request activity.
        pr_search = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        if pr_search:
            stats["prs"] = pr_search.get('total_count', 0)
            unique_contexts = set()
            for r in all_repos: unique_contexts.add(r.get('owner', {}).get('login'))
            for item in pr_search.get('items', []):
                repo_url = item.get('repository_url', '')
                match = re.search(r'/repos/([^/]+)/', repo_url)
                if match: unique_contexts.add(match.group(1))
            
            # Exclusion of own profile ensures distinct external project impact count.
            stats["contribs"] = max(1, len(unique_contexts) - (1 if username in unique_contexts else 0))

        # STEP 3: COMMIT RECONCILIATION
        # Extracts total contributions from the Streak API for profile consistency.
        stats["commits"] = "0"
        try:
            req_streak = urllib.request.Request(f"https://github-readme-streak-stats.herokuapp.com/?user={username}")
            with urllib.request.urlopen(req_streak) as res_streak:
                streak_svg = res_streak.read().decode('utf-8')
                match = re.search(r'([0-9,]+)\s*</text>\s*</g>\s*<!-- Total Contributions label', streak_svg)
                if match:
                    contrib_count = int(match.group(1).replace(',', ''))
                    stats["commits"] = f"{int(contrib_count / 100) / 10}k" if contrib_count >= 1000 else str(contrib_count)
                else:
                    raise Exception("Regex match failed")
        except Exception:
            # Fallback to standard API volume if primary metrics fail.
            commit_data = fetch_data(f"https://api.github.com/search/commits?q=author:{username}", token)
            final_count = commit_data.get('total_count', 0) if commit_data else 0
            stats["commits"] = f"{int(final_count / 100) / 10}k" if final_count >= 1000 else str(final_count)

        # STEP 4: PERSISTENCE & DATA INTEGRITY GUARD
        # Validation of API response volume before cache serialization. 
        # Prevents overwriting local data with null or empty results from 
        # successful but incomplete API returns.
        if stats.get('stars', 0) > 0:
            stats['last_updated'] = datetime.now(timezone.utc).isoformat()
            os.makedirs("docs", exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f)
        else:
            print("Validation Failure: Insufficient metric volume. Cache update bypassed.")

        # Final SVG serialization.
        with open("docs/stats.svg", "w", encoding="utf-8") as f: 
            f.write(create_stats_svg(stats, username))
            
        update_readme(int(datetime.now().timestamp()))
        print(f"Stats successfully synthesized. Commits: {stats['commits']}")
        
    except Exception as e:
        # Graceful recovery via the Resonance Cache if the API endpoint fails.
        print(f"Synthesis Failure: {e}. Transitioning to Resilience Cache...")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                stats = json.load(f)
            
            os.makedirs("docs", exist_ok=True)
            with open("docs/stats.svg", "w", encoding="utf-8") as f:
                f.write(create_stats_svg(stats, username))
            print("Successfully recovered metrics from local cache.")
        else:
            print("CRITICAL: Failed to retrieve live data or local backup.")

if __name__ == "__main__": 
    main()
