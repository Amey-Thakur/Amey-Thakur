"""
================================================================================
FILE NAME      : languages.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
Analytical engine for the quantification and visualization of programming 
language distribution. Calculations utilize diversity-weighted averaging across 
the repository portfolio to determine localized usage density per technology.

TECH STACK     : 
- Python 3     : Facilitates data aggregation and numerical normalization.
- GitHub API   : Source for repository-specific linguistic metadata.
- SVG (XML)    : Graphical format for high-fidelity profile integration.

HOW IT WORKS   :
1. AGGREGATION    : Scans the repository portfolio, excluding forks, to ensure 
                    data represents original development.
2. QUANTIFICATION : Retrieves byte counts and calculates localized percentage 
                    density per repository.
3. AVERAGING      : Computes the mean density for each technology across total 
                    portfolio volume.
4. NORMALIZATION  : Rescales results to 100% while maintaining visibility floors.
5. RESILIENCE     : Utilizes a local cache (languages_cache.json) for fallback.
6. RENDERING      : Finalizes the distribution into a custom SVG bar chart.
================================================================================
"""

import os
import json
import urllib.request
import re
import subprocess
from datetime import datetime, timezone, timedelta

# ==============================================================================
# DESIGN SYSTEM & ANALYTICAL CONSTANTS
# ==============================================================================

# Fail-safe data store used to maintain profile aesthetics during API downtime.
CACHE_FILE = "docs/languages_cache.json"

# Languages prioritized for specific analytical visibility within the dashboard.
PRIORITY_LANGS = ["R", "Julia", "MATLAB", "LaTeX", "C++", "Python"]

# Standard brand hex codes for professional technology representation.
LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "Jupyter Notebook": "#DA5B0B", 
    "JavaScript": "#f1e05a", "CSS": "#563d7c", "TypeScript": "#3178c6", 
    "Java": "#b07219", "C": "#555555", "C++": "#f34b7d", "Go": "#00ADD8", 
    "Rust": "#dea584", "Shell": "#89e051", "R": "#276DC3", "Julia": "#a270ba", 
    "MATLAB": "#e16737", "LaTeX": "#3D6117", "C#": "#178600", "PHP": "#4F5D95"
}


# ==============================================================================
# NETWORK UTILITIES
# ==============================================================================

def fetch_data(url, token):
    """
    Handles authenticated communication with the GitHub REST API.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None


# ==============================================================================
# GRAPHICAL SYNTHESIS ENGINE
# ==============================================================================

def create_langs_svg(langs, username):
    """
    Constructs the SVG visual with legacy title styles and priority-weighted 
    layout logic.
    """
    bg, white = "#000000", "#F0F6FC"
    
    # Isolation of dominant languages with priority-aware sorting.
    visible_langs = sorted([[k, v] for k, v in langs.items()], key=lambda x: x[1], reverse=True)[:18]
    
    # Mathematical Normalization to 100.0%.
    total_raw = sum(v for k, v in visible_langs) or 1
    for item in visible_langs:
        item[1] = (item[1] / total_raw) * 100
        
    # Visibility Floor: Ensures target languages maintain minimal visual impact.
    for item in visible_langs:
        if item[0] in PRIORITY_LANGS and item[1] < 1.0:
            item[1] = 1.0
            
    # Re-normalization after floor adjustments to ensure 100% calibration.
    total_adj = sum(v for k, v in visible_langs) or 1
    for item in visible_langs:
        item[1] = (item[1] / total_adj) * 100
        
    # Descending sort for visual hierarchy.
    visible_langs = sorted(visible_langs, key=lambda x: x[1], reverse=True)
    
    # Layout dimensions based on 3-column grid density.
    cols   = 3
    rows   = (len(visible_langs) + 2) // 3
    height = max(170, 110 + (rows * 20))
    
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Background Frame -->
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="22" fill="{white}" letter-spacing="-0.2px">{username}'s Most Used Languages</text>
    
    <!-- Distribution Bar Visualization -->
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    x_off = 0
    for name, perc in visible_langs:
        w = (perc / 100) * 435
        if w < 0.1: w = 0.5
        svg += f'<rect x="{x_off}" width="{w}" height="14" fill="{LANG_COLORS.get(name, "#888888")}"/>'
        x_off += w
    
    svg += '</g></g><g transform="translate(30, 100)">'
    for i, (name, perc) in enumerate(visible_langs):
        x, y = (i % 3) * 150, (i // 3) * 20
        d_name = name[:13] + '..' if len(name) > 15 else name
        svg += f'''<g transform="translate({x}, {y})">
            <circle cx="5" cy="-7" r="5" fill="{LANG_COLORS.get(name, "#888888")}"/>
            <text x="18" y="0" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="400" fill="{white}">{d_name}</text>
            <text x="140" y="0" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="400" fill="{white}" fill-opacity="0.6">{perc:.1f}%</text>
        </g>'''
    
    svg += '</g></svg>'
    return svg


# ==============================================================================
# CORE SYSTEM UTILITIES
# ==============================================================================

def update_readme(timestamp):
    """
    Applies cache-busting synchronization to README asset links.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    with open(readme_path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    with open(readme_path, "w", encoding="utf-8") as f: f.write(content)


def get_local_hour():
    """
    Detects local hour using the temporal offset of the most recent Git commit.
    """
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%ai'], capture_output=True, text=True, check=True)
        match  = re.search(r'([+-])(\d{2})(\d{2})$', result.stdout.strip())
        if not match: return datetime.now(timezone.utc).hour
        sign, h, m = match.groups()
        offset = (int(h) * 3600 + int(m) * 60) * (-1 if sign == '-' else 1)
        return datetime.now(timezone(timedelta(seconds=offset))).hour
    except Exception: return datetime.now(timezone.utc).hour


# ==============================================================================
# MAIN ANALYTICAL RUNTIME
# ==============================================================================

def main():
    token      = os.getenv('GITHUB_TOKEN')
    username   = "Amey-Thakur"
    all_langs_density = {}
    
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Scheduled update bypassed for hour {local_hour}.")
        return

    try:
        repos = []
        page  = 1
        while True:
            r_page = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not r_page: break
            repos.extend(r_page)
            if len(r_page) < 100: break
            page += 1
            
        if not repos: raise Exception("No repository metadata retrieved.")

        # Diversity-Weighted Language Averaging Engine.
        # This calculates mean density per technology across the total portfolio.
        repo_count = len(repos)
        for r in repos:
            if r.get('fork'):
                repo_count -= 1
                continue
                
            ld = fetch_data(r['languages_url'], token)
            if ld:
                r_total = sum(ld.values())
                if r_total > 0:
                    for k, v in ld.items():
                        density = (v / r_total)
                        all_langs_density[k] = all_langs_density.get(k, 0) + (density / len(repos)) # Normalize by total repos

        # STEP 5: PERSISTENCE & INTEGRITY GUARD
        if sum(all_langs_density.values()) > 0:
            cache_payload = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "data": all_langs_density
            }
            os.makedirs("docs", exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f)
        else:
            print("Validation Failure: Null density detected. Cache persistence bypassed.")

        with open("docs/languages.svg", "w", encoding="utf-8") as f: 
            f.write(create_langs_svg(all_langs_density, username))
            
        update_readme(int(datetime.now().timestamp()))
        print("Linguistic distribution successfully updated.")
        
    except Exception as e:
        print(f"Update Failure: {e}. Transitioning to Resilience Cache...")
        if os.path.exists(CACHE_FILE):
             with open(CACHE_FILE, "r", encoding="utf-8") as f:
                 cache_content = json.load(f)
                 all_langs_density = cache_content.get('data', cache_content) if isinstance(cache_content, dict) else cache_content
             
             os.makedirs("docs", exist_ok=True)
             with open("docs/languages.svg", "w", encoding="utf-8") as f:
                 f.write(create_langs_svg(all_langs_density, username))
             print("Successfully recovered metrics from local cache.")
        else:
             print("CRITICAL: Failed to retrieve live data or local backup.")

if __name__ == "__main__": 
    main()
