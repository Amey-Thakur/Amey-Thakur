"""
================================================================================
FILE NAME      : languages.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
Analytical engine for the quantification and visualization of programming 
language distribution. Calculations are based on raw byte volume across the 
entire repository portfolio to determine total work density per technology.

TECH STACK     : 
- Python 3     : Facilitates data aggregation and numerical normalization.
- GitHub API   : Source for repository-specific linguistic metadata.
- SVG (XML)    : Graphical format for high-fidelity profile integration.

HOW IT WORKS   :
1. AGGREGATION    : Scans the repository portfolio, intentionally excluding 
                    forks to ensure data represents original development.
2. QUANTIFICATION : Polls the /languages endpoint for every repository to 
                    retrieve precise byte counts.
3. SUMMATION      : Performs a global summation of bytes for every technology.
4. NORMALIZATION  : Converts byte volumes into relative percentages.
5. RESILIENCE     : Utilizes a local cache (languages_cache.json) as a fail-safe.
6. RENDERING      : Finalizes the distribution into a modern SVG bar chart.
================================================================================
"""

import os
import json
import urllib.request
import re
import subprocess
from datetime import datetime, timezone, timedelta

# ==============================================================================
# DESIGN SYSTEM & COLOR TOKENS
# ==============================================================================

# Fail-safe data store used to maintain profile aesthetics during API downtime.
CACHE_FILE = "docs/languages_cache.json"

# Mapping of programming languages to standardized brand hex codes. 
# Enhances visual recognition for developer-facing documentation.
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
    Utilizes localized request headers for authorization and version control.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # Token authentication significantly improves rate limits for 
    # large-scale repository scanning.
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        # Returns None to trigger the Resilience Layer in the main loop.
        return None


# ==============================================================================
# GRAPHICAL SYNTHESIS ENGINE
# ==============================================================================

def create_langs_svg(langs, username):
    """
    Builds the SVG vector graphic representing language distribution. 
    The layout is optimized for high-density displays using spacious margins.
    """
    bg, white = "#000000", "#F0F6FC"
    
    # Sorts technologies by volume and isolates the top 18 for rendering.
    visible_langs = sorted([[k, v] for k, v in langs.items()], key=lambda x: x[1], reverse=True)[:18]
    total_raw     = sum(v for k, v in visible_langs) or 1
    
    # Byte-to-percentage normalization for the accompanying legend.
    for item in visible_langs: 
        item[1] = (item[1] / total_raw) * 100
    
    # Dynamic height calculation based on rows (3-column layout).
    cols   = 3
    rows   = (len(visible_langs) + 2) // 3
    height = max(170, 110 + (rows * 20))
    
    # SVG definition with standard typography and geometry.
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .label {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .perc  {{ font: 400 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.6; }}
    </style>
    
    <!-- Background Frame - borderless black -->
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" class="title">{username}'s Language Usage</text>
    
    <!-- Distribution Bar Visualization -->
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    # Sequential rendering of rectangles to form a continuous bar chart.
    x_off = 0
    for name, perc in visible_langs:
        w = (perc / 100) * 435
        svg += f'<rect x="{x_off}" width="{w}" height="14" fill="{LANG_COLORS.get(name, "#888888")}"/>'
        x_off += w
    
    # Legend synthesis utilizing a modular grid system.
    svg += '</g></g><g transform="translate(30, 100)">'
    for i, (name, perc) in enumerate(visible_langs):
        x, y = (i % 3) * 150, (i // 3) * 20
        svg += f'''<g transform="translate({x}, {y})">
            <circle cx="5" cy="-7" r="5" fill="{LANG_COLORS.get(name, "#888888")}"/>
            <text x="18" y="0" class="label">{name[:13]}</text>
            <text x="140" y="0" text-anchor="end" class="perc">{perc:.1f}%</text>
        </g>'''
    
    svg += '</g></svg>'
    return svg


# ==============================================================================
# CORE SYSTEM UTILITIES
# ==============================================================================

def update_readme(timestamp):
    """
    Injects a unique timestamp into README image sources to bypass the 
    GitHub Camo proxy cache. Ensures visual updates are immediate.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    
    with open(readme_path, "r", encoding="utf-8") as f: 
        content = f.read()
        
    # Standard substitution of the ?t=<timestamp> query string.
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    
    with open(readme_path, "w", encoding="utf-8") as f: 
        f.write(content)


def get_local_hour():
    """
    Predicts the current local hour using the temporal offset of the 
    most recent Git commit.
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
# MAIN ANALYTICAL RUNTIME
# ==============================================================================

def main():
    token      = os.getenv('GITHUB_TOKEN')
    username   = "Amey-Thakur"
    lang_bytes = {}
    
    # Scheduled runs are restricted to 12 AM/PM locally to optimize update frequency.
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Scheduled update bypassed for hour {local_hour}.")
        return

    try:
        # Paginated discovery of all account repositories.
        repos = []
        page  = 1
        while True:
            r_page = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not r_page: break
            repos.extend(r_page)
            if len(r_page) < 100: break
            page += 1
            
        if not repos:
            raise Exception("No repository metadata retrieved.")

        # Aggregation of raw byte counts from original work (excluding forks).
        for r in repos:
            if r.get('fork'): 
                continue
                
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k, v in ld.items(): 
                    lang_bytes[k] = lang_bytes.get(k, 0) + v
        
        if not lang_bytes:
             raise Exception("No linguistic data found.")

        # Saves current state to the resilience cache before serialization.
        os.makedirs("docs", exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(lang_bytes, f)

        # Final SVG synthesis.
        with open("docs/languages.svg", "w", encoding="utf-8") as f: 
            f.write(create_langs_svg(lang_bytes, username))
            
        update_readme(int(datetime.now().timestamp()))
        print("Linguistic distribution successfully updated.")
        
    except Exception as e:
        # Recovery using the local Resilience Cache in the event of API throttling.
        print(f"Update Failure: {e}. Transitioning to Resilience Cache...")
        if os.path.exists(CACHE_FILE):
             with open(CACHE_FILE, "r", encoding="utf-8") as f:
                 lang_bytes = json.load(f)
             
             os.makedirs("docs", exist_ok=True)
             with open("docs/languages.svg", "w", encoding="utf-8") as f:
                 f.write(create_langs_svg(lang_bytes, username))
             print("Successfully recovered metrics from local cache.")
        else:
             print("CRITICAL: Failed to retrieve live data or local backup.")

if __name__ == "__main__": 
    main()
