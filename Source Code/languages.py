"""
================================================================================
FILE NAME      : languages.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
I wrote this module to visualize my programming language distribution on GitHub. 
It calculates my language usage based on the raw byte volume of code I've written 
across all my repositories.

TECH STACK     : 
- Python 3     : Used for all data aggregation and math.
- GitHub API   : I use this to get the exact language breakdown for each repo.
- SVG (XML)    : The output format for the final language distribution bar.

HOW IT WORKS   :
1. AGGREGATION    : I scan all my original repositories, intentionally skipping 
                    forks so the data only reflects my own work.
2. QUANTIFICATION : I hit the /languages endpoint for every single project to 
                    get the raw byte counts.
3. SUMMATION      : I calculate the global sum of every byte I've committed.
4. NORMALIZATION  : I convert those bytes into local percentages.
5. RESILIENCE     : I maintain a backup (languages_cache.json). If the API is 
                    ever throttled, I serve my last known work volume instead.
6. RENDERING      : I pack the results into a clean, modern SVG bar chart.
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

# I save my last successful run data here as a fail-safe backup.
CACHE_FILE = "docs/languages_cache.json"

# These are the standard brand colors for each language. I use these to make 
# the graph intuitive for anyone looking at my profile.
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
    My standard helper for talking to the GitHub REST API. 
    It handles authentication and JSON parsing in one place.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # I use my token to get better rate limits. This is important when 
    # I'm looping through all my repositories in one go.
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        # If the API is unstable, I return None and let the main logic handle it.
        return None


# ==============================================================================
# GRAPHICAL SYNTHESIS ENGINE
# ==============================================================================

def create_langs_svg(langs, username):
    """
    I use this function to build the final SVG image. I designed it to be 
    spacious and easy to read on high-resolution displays as well as mobile.
    """
    bg, white = "#000000", "#F0F6FC"
    
    # I sort the languages by byte count and pull the top 18 for the card.
    visible_langs = sorted([[k, v] for k, v in langs.items()], key=lambda x: x[1], reverse=True)[:18]
    total_raw     = sum(v for k, v in visible_langs) or 1
    
    # I convert absolute bytes into relative percentages for the legend.
    for item in visible_langs: 
        item[1] = (item[1] / total_raw) * 100
    
    # Calculating a dynamic height so the card grows if I add more languages.
    cols   = 3
    rows   = (len(visible_langs) + 2) // 3
    height = max(170, 110 + (rows * 20))
    
    # SVG skeleton with custom typography and layout settings.
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .label {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .perc  {{ font: 400 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.6; }}
    </style>
    
    <!-- Background Frame - borderless black to blend with profile -->
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" class="title">{username}'s Language Usage</text>
    
    <!-- Distribution Bar - I mask it with rounded corners -->
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    # Building the continuous bar by tracking the horizontal offset.
    x_off = 0
    for name, perc in visible_langs:
        w = (perc / 100) * 435
        svg += f'<rect x="{x_off}" width="{w}" height="14" fill="{LANG_COLORS.get(name, "#888888")}"/>'
        x_off += w
    
    # Drawing the legend dots and labels in a 3-column grid.
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
    I use this to swap out the cache-busting timestamp in my README 
    so visitors always see my most current data.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    
    with open(readme_path, "r", encoding="utf-8") as f: 
        content = f.read()
        
    # Standard regex replace to update the URL parameter.
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    
    with open(readme_path, "w", encoding="utf-8") as f: 
        f.write(content)


def get_local_hour():
    """
    I look at my last Git commit to figure out my timezone offset. 
    It ensures the script respects my local clock.
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
    
    # I only allow scheduled runs at specific hours locally.
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Bypassing scheduled run for hour {local_hour}.")
        return

    try:
        # Paginating through all my repositories.
        repos = []
        page  = 1
        while True:
            r_page = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not r_page: break
            repos.extend(r_page)
            if len(r_page) < 100: break
            page += 1
            
        if not repos:
            raise Exception("Discovery Failed")

        # I iterate through all my original repositories (no forks) 
        # to get the code byte counts.
        for r in repos:
            if r.get('fork'): 
                continue
                
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k, v in ld.items(): 
                    lang_bytes[k] = lang_bytes.get(k, 0) + v
        
        if not lang_bytes:
             raise Exception("No bytes found.")

        # Saving my results to the backup cache first.
        os.makedirs("docs", exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(lang_bytes, f)

        # Writing the final SVG for my profile.
        with open("docs/languages.svg", "w", encoding="utf-8") as f: 
            f.write(create_langs_svg(lang_bytes, username))
            
        update_readme(int(datetime.now().timestamp()))
        print("Success! My language stats are updated.")
        
    except Exception as e:
        # If anything breaks, I attempt to load my last saved data.
        print(f"API Error: {e}. I'm recovering from my backup cache.")
        if os.path.exists(CACHE_FILE):
             with open(CACHE_FILE, "r", encoding="utf-8") as f:
                 lang_bytes = json.load(f)
             
             os.makedirs("docs", exist_ok=True)
             with open("docs/languages.svg", "w", encoding="utf-8") as f:
                 f.write(create_langs_svg(lang_bytes, username))
             print("Recovered from my local cache.")
        else:
             print("Serious Error: No live data and no cache backup exists.")

if __name__ == "__main__": 
    main()
