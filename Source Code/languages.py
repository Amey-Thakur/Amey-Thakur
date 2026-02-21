"""
================================================================================
FILE NAME      : languages.py
AUTHOR         : Amey Thakur (https://github.com/Amey-Thakur)
                 Mega Satish (https://github.com/msatmod)
RELEASE DATE   : July 5, 2021
LICENCE        : MIT License

DESCRIPTION    : 
This module provides a rigorous analytical framework for quantifying and 
visualizing programming language distribution across a GitHub user profile. 
It focuses on "Total Work Volume" by analyzing raw byte counts.

TECH STACK     : 
- Python 3     : Core data processing and normalization logic.
- GitHub API   : Source for precise linguistic metadata per repository.
- SVG (XML)    : Vector representation for high-fidelity profile integration.

HOW IT WORKS   :
1. AGGREGATION    : Iterates through the entire repository portfolio, intentionally 
                    skipping forked projects to ensure data represents original work.
2. QUANTIFICATION : Polls the /languages endpoint for every repository to retrieve 
                    the precise byte count for every detected language.
3. SUMMATION      : Performs a global weighted summation of bytes across all projects.
4. NORMALIZATION  : Converts raw byte volumes into percentages, ensuring the total 
                    distribution equals exactly 100%.
5. RENDERING      : Synthesizes the results into a spacious, well-aligned SVG bar 
                    chart with localized color tokens.
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

# These color tokens map programming languages to their standard brand colors. 
# This ensures that the generated visualization is immediately intuitive to 
# other developers.
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
    Utilizes a custom Request object to specify the API version and 
    authorization status.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # Authenticated requests have significantly higher rate limits, 
    # which is crucial for iterating through large repository portfolios.
    if token: 
        req.add_header('Authorization', f'token {token}')
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception:
        # Fallback to None if the network is unstable or the repo is inaccessible.
        return None


# ==============================================================================
# GRAPHICAL SYNTHESIS ENGINE
# ==============================================================================

def create_langs_svg(langs, username):
    """
    Constructs a Scalable Vector Graphic (SVG) from the processed language data. 
    The layout is designed to be spacious and legible at various screen resolutions.
    """
    bg, white = "#0D1117", "#F0F6FC"
    
    # STEP 1: RANKING
    # Sort the dictionary items by byte count in descending order 
    # and isolate the top 18 for the visual layout.
    visible_langs = sorted([[k, v] for k, v in langs.items()], key=lambda x: x[1], reverse=True)[:18]
    total_raw     = sum(v for k, v in visible_langs) or 1
    
    # STEP 2: NORMALIZATION
    # Convert absolute byte counts into relative percentages.
    for item in visible_langs: 
        item[1] = (item[1] / total_raw) * 100
    
    # STEP 3: LAYOUT DYNAMICS
    # We calculate the height dynamically based on the number of rows (3 columns).
    cols   = 3
    rows   = (len(visible_langs) + 2) // 3
    height = max(170, 110 + (rows * 20))
    
    # Opening the SVG container with embedded styles for responsive typography.
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .label {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .perc  {{ font: 400 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.6; }}
    </style>
    
    <!-- Background Frame -->
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" class="title">{username}'s Language Usage</text>
    
    <!-- Progress Bar Section -->
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    # Iteratively render rectangles for the bar chart, tracking the x-offset.
    x_off = 0
    for name, perc in visible_langs:
        w = (perc / 100) * 435
        svg += f'<rect x="{x_off}" width="{w}" height="14" fill="{LANG_COLORS.get(name, "#888888")}"/>'
        x_off += w
    
    # Render the legend at the bottom of the card.
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
    Modifies the local README.md file to inject a unique timestamp into 
    image sources. This effectively bypasses the GitHub Camo image cache.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    
    with open(readme_path, "r", encoding="utf-8") as f: 
        content = f.read()
        
    # We target the languages.svg specifically with a global regex substitution.
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    
    with open(readme_path, "w", encoding="utf-8") as f: 
        f.write(content)


def get_local_hour():
    """
    Predicts the current local hour of the developer by inspecting the 
    temporal offset of their latest Git activity.
    """
    try:
        # We use a subprocess to interact with the local git binary directly.
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
    # 1. INITIALIZATION
    token      = os.getenv('GITHUB_TOKEN')
    username   = "Amey-Thakur"
    lang_bytes = {}
    
    # 2. TEMPORAL GATE: Synchronize with the 12:00 mark in the local timezone.
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Scheduled update bypassed for hour {local_hour}.")
        return

    try:
        # 3. REPOSITORY DISCOVERY
        # We paginate through the entire user list to ensure no work is missed.
        repos = []
        page  = 1
        while True:
            r_page = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not r_page: break
            repos.extend(r_page)
            if len(r_page) < 100: break
            page += 1
            
        # 4. LINGUISTIC QUANTIFICATION
        # We aggregate raw byte counts from all non-forked repositories. 
        # Forked repos are skipped to ensure the stats represent original creation.
        for r in repos:
            if r.get('fork'): 
                continue
                
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k, v in ld.items(): 
                    lang_bytes[k] = lang_bytes.get(k, 0) + v
        
        # 5. PERSISTENCE
        # Ensure the output directory is ready before finalizing the SVG.
        os.makedirs("docs", exist_ok=True)
        with open("docs/languages.svg", "w", encoding="utf-8") as f: 
            f.write(create_langs_svg(lang_bytes, username))
            
        # Force a cache update on the profile README.
        update_readme(int(datetime.now().timestamp()))
        print("Linguistic distribution successfully updated.")
        
    except Exception as e:
        print(f"LANGUAGE SYNTHESIS FAILURE: {e}")

if __name__ == "__main__": 
    main()
