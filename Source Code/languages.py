"""
File: languages.py
Description: A specialized analytical module for the empirical synthesis of linguistic distribution.
PART OF THE AMEY-THAKUR COMPUTATIONAL FRAMEWORK.

ALGORITHMIC TAXONOMY:
1. Temporal Inference: Dynamic Git-log-based offset deduction.
2. Weighted Linguistic Summation: Byte-based quantification of total work output.
3. Graphical Rendering: Vector-based visualization with high-fidelity normalization.
"""

import os
import json
import urllib.request
import re
import subprocess
from datetime import datetime, timezone, timedelta

# ==============================================================================
# CONFIGURATION AND PARAMETERS
# ==============================================================================

LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "Jupyter Notebook": "#DA5B0B", "JavaScript": "#f1e05a",
    "CSS": "#563d7c", "TypeScript": "#3178c6", "Java": "#b07219", "C": "#555555", "C++": "#f34b7d",
    "Go": "#00ADD8", "Rust": "#dea584", "Shell": "#89e051", "R": "#276DC3", "Julia": "#a270ba",
    "MATLAB": "#e16737", "LaTeX": "#3D6117", "C#": "#178600", "PHP": "#4F5D95"
}

PRIORITY_LANGS = ["R", "Julia", "MATLAB", "LaTeX", "C++", "Python"]

# ==============================================================================
# DATA ACQUISITION LAYER
# ==============================================================================

def fetch_data(url, token):
    """
    Executes an authenticated HTTP GET request to the GitHub REST API.
    """
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    if token: req.add_header('Authorization', f'token {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception: return None

# ==============================================================================
# GRAPHICAL SYNTHESIS (SVG)
# ==============================================================================

def create_langs_svg(langs, username):
    """
    Synthesizes language distribution data into an SVG visualization with normalization.
    """
    bg, white = "#0D1117", "#F0F6FC"
    
    # Sort and filter for the top 18 visible languages
    visible_langs = sorted([[k, v] for k, v in langs.items()], key=lambda x: x[1], reverse=True)[:18]
    total_raw = sum(v for k, v in visible_langs) or 1
    
    # Normalization to 100%
    for item in visible_langs: item[1] = (item[1] / total_raw) * 100
    
    cols, rows = 3, (len(visible_langs) + 2) // 3
    height = max(170, 110 + (rows * 20))
    
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 22px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .label {{ font: 400 12px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; }}
        .perc {{ font: 400 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: {white}; opacity: 0.6; }}
    </style>
    <rect width="494" height="{height-1}" x="0.5" y="0.5" rx="10" fill="{bg}" stroke="#30363d"/>
    <text x="30" y="38" class="title">{username}'s Linguistic Distribution</text>
    
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    x_off = 0
    for name, perc in visible_langs:
        w = (perc / 100) * 435
        svg += f'<rect x="{x_off}" width="{w}" height="14" fill="{LANG_COLORS.get(name, "#888888")}"/>'
        x_off += w
    
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
# SYSTEM UTILITIES
# ==============================================================================

def update_readme(timestamp):
    """
    Updates the README markdown document with current visual parameters.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    with open(readme_path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    with open(readme_path, "w", encoding="utf-8") as f: f.write(content)

def get_local_hour():
    """
    Infers the user's current hour from Git commit metadata.
    """
    try:
        result = subprocess.run(['git', 'log', '-1', '--format=%ai'], capture_output=True, text=True, check=True)
        match = re.search(r'([+-])(\d{2})(\d{2})$', result.stdout.strip())
        if not match: return datetime.now(timezone.utc).hour
        sign, h, m = match.groups()
        offset = (int(h) * 3600 + int(m) * 60) * (-1 if sign == '-' else 1)
        return datetime.now(timezone(timedelta(seconds=offset))).hour
    except Exception: return datetime.now(timezone.utc).hour

def main():
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    lang_bytes = {}
    
    local_hour = get_local_hour()
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and local_hour not in [0, 12]:
        print(f"Langs schedule bypass: Hour {local_hour}")
        return

    try:
        repos = []
        page = 1
        while True:
            r_page = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}", token)
            if not r_page: break
            repos.extend(r_page)
            if len(r_page) < 100: break
            page += 1
            
        for r in repos:
            if r.get('fork'): continue
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k, v in ld.items(): lang_bytes[k] = lang_bytes.get(k, 0) + v
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(lang_bytes, username))
        update_readme(int(datetime.now().timestamp()))
        print("Success: Langs visualized.")
    except Exception as e:
        print(f"Langs Error: {e}")

if __name__ == "__main__": main()
