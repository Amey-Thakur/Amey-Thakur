"""
File: generate_stats.py
Description: Comprehensive GitHub Statistics Visualization Engine.
Authors: Amey Thakur (https://github.com/Amey-Thakur)
         Mega Satish (https://github.com/msatmod)
License: MIT License
Release Date: July 5, 2021
Version: 1.0.0

This module serves as the core analytical engine for the Amey-Thakur profile.
It orchestrates advanced data retrieval from the GitHub REST API, performs multi-dimensional
scoring for professional-grade ranking, and generates high-fidelity SVG visualizations
with a sleek, refined appearance.
"""

import os
import json
import urllib.request
import re
from datetime import datetime

# ==============================================================================
# ANALYTICAL CONFIGURATION & AESTHETIC CONSTANTS
# ==============================================================================

# Massive, Future-Proof Language Color Map (Standardized for Formal Visuals)
LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "Jupyter Notebook": "#DA5B0B", "JavaScript": "#f1e05a",
    "CSS": "#563d7c", "TypeScript": "#3178c6", "Java": "#b07219", "C": "#555555", "C++": "#f34b7d",
    "C#": "#178600", "PHP": "#4F5D95", "Ruby": "#701516", "Swift": "#F05138", "Go": "#00ADD8",
    "Rust": "#dea584", "Objective-C": "#438eff", "Shell": "#89e051", "PowerShell": "#012456",
    "Kotlin": "#A97BFF", "Dart": "#00B4AB", "SQL": "#e38c00", "Scala": "#c22d40", "Perl": "#0298c3",
    "R": "#276DC3", "Haskell": "#5e5086", "Lua": "#000080", "Assembly": "#6E4C13", "MATLAB": "#e16737",
    "Julia": "#a270ba", "Clojure": "#db5855", "Elixir": "#6e4a7e", "OCaml": "#ef7a08", "F#": "#b845fc",
    "Fortran": "#4d41b1", "Erlang": "#B83998", "Groovy": "#427819", "Solidity": "#AA6746",
    "Vim Script": "#199f4b", "CoffeeScript": "#244776", "Markdown": "#083fa1", "Svelte": "#ff3e00",
    "Vue": "#41b883", "SCSS": "#c6538c", "LaTeX": "#3D6117", "TeX": "#3D6117", "Zig": "#ec915c",
    "Nim": "#ffc200", "Nix": "#7e7eff", "Verilog": "#b2b7f8", "VHDL": "#adb2cb", "ActionScript": "#882B0F",
    "Ada": "#02f88c", "Apex": "#1797c0", "Arduino": "#bd79d1", "Augeas": "#9CC134", "AutoHotkey": "#6594b9",
    "Batchfile": "#C1F12E", "BitBake": "#00b0ff", "BlitzBasic": "#0000ff", "Bluespec": "#12223c",
    "Brainfuck": "#2F2530", "Brightscript": "#662D91", "Bro": "#3a8e3a", "Ceylon": "#dfa535",
    "ChucK": "#3f8000", "CMake": "#DA3434", "Common Lisp": "#3fb68b", "Coq": "#7cb5ec",
    "Crystal": "#000100", "D": "#ba595e", "Dockerfile": "#384d54", "Eiffel": "#4d6935", "Elm": "#60B5CC",
    "Emacs Lisp": "#7F5AB6", "Fish": "#4ab3dc", "Gherkin": "#5B2063", "Haxe": "#df7900",
    "IDL": "#a3522f", "Makefile": "#427819", "Max": "#c4a79c", "Mercury": "#ff2b2b", "Nginx": "#009639",
    "Nushell": "#4E5D95", "Objective-J": "#ff0c5a", "Opal": "#f7ede0", "Pascal": "#E3F171",
    "PostScript": "#da291c", "Prolog": "#74283c", "Protocol Buffer": "#F7533E", "Puppet": "#302B6D",
    "PureScript": "#1D222D", "QMake": "#062963", "Racket": "#3c5caa", "Scheme": "#1e4aec",
    "Smalltalk": "#596706", "Stata": "#1a5f91", "Tcl": "#e4cc98", "Terraform": "#7b42bb",
    "Thrift": "#D12127", "V": "#1b142d", "Vala": "#fbe5cd", "WebAssembly": "#04133b",
    "Wolfram": "#dd1100", "YAML": "#cb171e", "Zephir": "#118f9e", "Zimpl": "#d67711", "Rich Text Format": "#FFFFFF"
}

# High-Fidelity Outlined Icons (Sourced from Professional Standard Sets)
ICONS = {
    "star": '<path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="none" stroke="{color}" stroke-width="1.2"/>',
    "commit": '<path d="M8 0a8 8 0 100 16A8 8 0 008 0zM1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0z" fill="{color}"/><path d="M8 3.5a.75.75 0 01.75.75v3.5h2.5a.75.75 0 010 1.5h-3.25a.75.75 0 01-.75-.75v-4.25a.75.75 0 01.75-.75z" fill="{color}"/>',
    "pr": '<path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5a2.5 2.5 0 00-2.5-2.5zm-7.5 10a.75.75 0 100 1.5.75.75 0 000-1.5zM12 12.5a.75.75 0 100 1.5.75.75 0 000-1.5z" fill="none" stroke="{color}" stroke-width="1.2"/>',
    "issue": '<path d="M8 15A7 7 0 108 1a7 7 0 000 14zm0 1A8 8 0 118 0a8 8 0 010 16z" fill="{color}"/><path d="M7.002 11a1 1 0 112 0 1 1 0 01-2 0zM7.1 4h1.8l-.45 6h-.9L7.1 4z" fill="{color}"/>',
    "contrib": '<path d="M2 1.75C2 .784 2.784 0 3.75 0h8.5C13.216 0 14 .784 14 1.75v11.5A1.75 1.75 0 0112.25 15h-8.5A1.75 1.75 0 012 13.25V1.75zM3.5 1.75v11.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V1.75a.25.25 0 00-.25-.25h-8.5a.25.25 0 00-.25.25z" fill="{color}"/><path d="M5 3h6v1.5H5V3zm0 3h6v1.5H5V6z" fill="{color}"/>'
}

# Languages prioritized for specific analytical visibility
PRIORITY_LANGS = ["R", "Julia", "MATLAB", "LaTeX", "C++", "Python"]

# ==============================================================================
# DATA RETRIEVAL CORE
# ==============================================================================

def fetch_data(url, token):
    """
    Performs authenticated HTTP GET requests to the GitHub REST API.
    
    Args:
        url (str): Target REST API endpoint.
        token (str): GitHub Personal Access Token for authentication.
        
    Returns:
        dict/list: Parsed JSON response or None if request fails.
    """
    req = urllib.request.Request(url)
    if token: req.add_header('Authorization', f'token {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception: return None

# ==============================================================================
# ANALYTICAL & SCORING LOGIC
# ==============================================================================

def calculate_grade(stats):
    """
    Executes a multi-dimensional scoring algorithm to determine rank.
    
    This algorithm balances raw contribution volume with quality metrics
    like stars and organizational diversity.
    
    Args:
        stats (dict): Aggregated user statistics.
        
    Returns:
        tuple: (Grade string, Rank percentage int)
    """
    stars = int(stats.get('stars', 0))
    # Handle both integer and '13.8k+' string formatted commit counts
    commit_raw = str(stats.get('commits', '0'))
    commits = float(commit_raw.replace('k+', '').replace('k', '')) * 1000 if 'k' in commit_raw else float(commit_raw)
    prs = int(stats.get('prs', 0))
    issues = int(stats.get('issues', 0))
    contribs = int(stats.get('contribs', 0))
    
    # Weighted scoring formula (Production Tuned)
    score = (stars * 10) + (commits * 1.5) + (prs * 50) + (issues * 5) + (contribs * 100)
    
    if score > 8000: return "A+", 95
    if score > 6000: return "A", 85
    if score > 4000: return "A-", 75
    if score > 3000: return "B+", 65
    if score > 2000: return "B", 55
    if score > 1000: return "B-", 45
    return "C", 30

# ==============================================================================
# VISUALIZATION ENGINES (SVG GENERATION)
# ==============================================================================

def create_stats_svg(stats, username):
    """
    Generates a high-fidelity SVG for GitHub Statistics.
    
    Features a circular progress rank and unbolded refined typography.
    """
    cyan, bg, white = "#00fbff", "#060A0C", "#FFFFFF"
    theme_color = cyan
    grade, rank = calculate_grade(stats)
    
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="195" rx="10" fill="{bg}"/>
    <text x="25" y="32" font-family="'Segoe UI', Inter, sans-serif" font-weight="600" font-size="22" fill="{theme_color}" letter-spacing="-0.2px">{username}'s GitHub Stats</text>
    
    <g transform="translate(30, 65)">
        <g transform="translate(0, 0)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['star'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Stars Earned:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('stars', '---')}</text>
        </g>
        <g transform="translate(0, 26)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['commit'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Commits:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('commits', '---')}</text>
        </g>
        <g transform="translate(0, 52)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['pr'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total PRs:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('prs', '---')}</text>
        </g>
        <g transform="translate(0, 78)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['issue'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Issues:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('issues', '---')}</text>
        </g>
        <g transform="translate(0, 104)">
            <svg x="0" y="-14" width="18" height="18" viewBox="0 0 16 16">{ICONS['contrib'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Contributed to (last year):</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('contribs', '---')}</text>
        </g>
    </g>
    
    <g transform="translate(400, 105)">
        <circle r="44" stroke="{theme_color}" stroke-width="4.5" fill="none" opacity="0.1"/>
        <circle r="44" stroke="{theme_color}" stroke-width="4.5" fill="none" 
                stroke-dasharray="276.46" stroke-dashoffset="{276.46 * (1 - rank/100)}" 
                stroke-linecap="round" transform="rotate(-90)"/>
        <text text-anchor="middle" dy="0.35em" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="34" fill="{white}">{grade}</text>
    </g>
    
    <text x="400" y="180" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="10" fill="{white}" fill-opacity="0.3" font-style="italic">Now or Never</text>
</svg>'''
    return svg

def create_langs_svg(langs):
    """
    Generates a localized Linguistic Profile SVG using Analytical Synthesis.
    
    Implements Diversity-Weighted Averaging and a Visibility Floor for Priority
    Languages to ensure professional representation and 100% mathematical sum.
    """
    bg, white = "#060A0C", "#FFFFFF"
    
    # Sort and filter for the top 18 visible languages
    visible_langs = []
    seen = set()
    
    # Step 1: Guarantee Priority Languages (if they have ANY data)
    for p_lang in PRIORITY_LANGS:
        if p_lang in langs and len(visible_langs) < 18:
            visible_langs.append([p_lang, langs[p_lang]])
            seen.add(p_lang)
            
    # Step 2: Fill remaining slots with highest density languages
    sorted_remaining = sorted([(k,v) for k,v in langs.items() if k not in seen], key=lambda x: x[1], reverse=True)
    for name, density in sorted_remaining:
        if len(visible_langs) < 18:
            visible_langs.append([name, density])
            seen.add(name)
            
    # Final sort for visual consistency
    visible_langs = sorted(visible_langs, key=lambda x: x[1], reverse=True)
    
    # Mathematical Normalization to 100% (Largest Remainder Method simplified)
    total_raw = sum(v for k,v in visible_langs)
    if total_raw == 0: total_raw = 1
    
    # Initial proportional distribution
    for item in visible_langs:
        item[1] = (item[1] / total_raw) * 100
        
    # Visibility Floor: Ensure Priority Languages are visible (min 1.0% if they exist)
    for item in visible_langs:
        if item[0] in PRIORITY_LANGS and item[1] < 1.0:
            item[1] = 1.0
            
    # Re-normalize to exactly 100.0% after floor adjustments
    total_adj = sum(item[1] for item in visible_langs)
    for item in visible_langs:
        item[1] = (item[1] / total_adj) * 100
        
    # Layout Calculations
    cols = 3
    rows = (len(visible_langs) + (cols-1)) // cols
    height = 110 + (rows * 20)
    if height < 170: height = 170
    
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" font-family="'Segoe UI', Inter, sans-serif" font-weight="600" font-size="22" fill="{white}" letter-spacing="-0.2px">Amey-Thakur's Most Used Languages</text>
    
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    curr_x = 0
    for name, perc in visible_langs:
        width = (perc / 100) * 435
        if width < 0.1: width = 0.5
        color = LANG_COLORS.get(name, "#888888")
        svg += f'<rect x="{curr_x}" width="{width}" height="14" fill="{color}"/>'
        curr_x += width
    
    svg += '</g></g><g transform="translate(30, 100)">'
    
    col_width = 150
    for i, (name, perc) in enumerate(visible_langs):
        col, row = i % cols, i // cols
        x, y = col * col_width, row * 20 
        color = LANG_COLORS.get(name, "#888888")
        display_name = name[:13] + '..' if len(name) > 15 else name
        
        svg += f'''
        <g transform="translate({x}, {y})">
            <circle cx="5" cy="-7" r="5" fill="{color}"/>
            <text x="18" y="0" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="400" fill="{white}">{display_name}</text>
            <text x="140" y="0" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="400" fill="{white}" fill-opacity="0.6">{perc:.1f}%</text>
        </g>'''
        
    svg += '</g></svg>'
    return svg

# ==============================================================================
# SYSTEM SYNCHRONIZATION
# ==============================================================================

def update_readme(timestamp):
    """
    Performs cache-busting synchronization on the README.md asset links.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    with open(readme_path, "r", encoding="utf-8") as f: content = f.read()
    # Apply unique timestamp to force GitHub to bypass previous image caches
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    content = re.sub(r'docs/stats\.svg(\?t=\d+)?', f'docs/stats.svg?t={timestamp}', content)
    with open(readme_path, "w", encoding="utf-8") as f: f.write(content)

def main():
    """
    Orchestrates Analytical Synthesis of user metrics and visualizations.
    """
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    all_langs_density = {}
    stats = {"stars": 0, "commits": "13.8k+", "prs": 0, "issues": 0, "contribs": 1}
    timestamp = int(datetime.now().timestamp())
    
    try:
        all_repos = []
        page = 1
        while True:
            url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
            page_repos = fetch_data(url, token)
            if not page_repos: break
            all_repos.extend(page_repos)
            if len(page_repos) < 100: break
            page += 1
            
        if not all_repos: raise Exception("No repos found")
        
        stats["stars"] = sum(repo.get('stargazers_count', 0) for repo in all_repos)
        stats["issues"] = sum(repo.get('open_issues_count', 0) for repo in all_repos)
        
        unique_orgs = set()
        for r in all_repos:
            if r.get('owner', {}).get('login') != username:
                unique_orgs.add(r['owner']['login'])
        stats["contribs"] = max(1, len(unique_orgs))
        
        prs_data = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        if prs_data: stats["prs"] = prs_data.get('total_count', 0)
        
        # Analytical Synthesis: Diversity-Weighted Language Averaging
        repo_count = len(all_repos)
        for r in all_repos:
            ld = fetch_data(r['languages_url'], token)
            if ld:
                # Calculate local distribution for this repo
                r_total = sum(ld.values())
                if r_total > 0:
                    for k, v in ld.items():
                        density = (v / r_total)
                        all_langs_density[k] = all_langs_density.get(k, 0) + (density / repo_count)
            else:
                # Fallback: Boost priority languages if they are in repo name but data missing (Rmd/Boilerplate)
                for p_lang in PRIORITY_LANGS:
                    if p_lang.lower() in r['name'].lower():
                        all_langs_density[p_lang] = all_langs_density.get(p_lang, 0) + (0.1 / repo_count)

        # Write high-fidelity SVGs to docs/
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(stats, username))
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(all_langs_density))
        update_readme(timestamp)
        print("Success: Analytical Synthesis Master Synchronized.")
        
    except Exception as e:
        fallback_langs = {"HTML": 35.5, "Python": 25.0, "Jupyter Notebook": 10.0, "R": 8.5, "JavaScript": 5.0} # Fallback only
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(stats, username))
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(fallback_langs))
        update_readme(timestamp)
        print(f"Resilient Fallback Active: {e}")

if __name__ == "__main__":
    main()
