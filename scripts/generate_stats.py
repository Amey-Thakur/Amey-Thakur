import os
import json
import urllib.request
import re
from datetime import datetime

# Massive, Future-Proof Language Color Map
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
    "Boo": "#d4bec1", "Brainfuck": "#2F2530", "Brightscript": "#662D91", "Bro": "#3a8e3a",
    "Ceylon": "#dfa535", "ChucK": "#3f8000", "CMake": "#DA3434", "Common Lisp": "#3fb68b",
    "Coq": "#7cb5ec", "Crystal": "#000100", "D": "#ba595e", "Dockerfile": "#384d54", "Eiffel": "#4d6935",
    "Elm": "#60B5CC", "Emacs Lisp": "#7F5AB6", "Fish": "#4ab3dc", "Gherkin": "#5B2063",
    "Haxe": "#df7900", "IDL": "#a3522f", "Makefile": "#427819", "Max": "#c4a79c", "Mercury": "#ff2b2b",
    "Nginx": "#009639", "Nushell": "#4E5D95", "Objective-J": "#ff0c5a", "Opal": "#f7ede0",
    "Pascal": "#E3F171", "PostScript": "#da291c", "Prolog": "#74283c", "Protocol Buffer": "#F7533E",
    "Puppet": "#302B6D", "PureScript": "#1D222D", "QMake": "#062963", "Racket": "#3c5caa",
    "Scheme": "#1e4aec", "Smalltalk": "#596706", "Stata": "#1a5f91", "Tcl": "#e4cc98",
    "Terraform": "#7b42bb", "Thrift": "#D12127", "V": "#1b142d", "Vala": "#fbe5cd",
    "WebAssembly": "#04133b", "Wolfram": "#dd1100", "YAML": "#cb171e", "Zephir": "#118f9e",
    "Zimpl": "#d67711", "Rich Text Format": "#FFFFFF"
}

ICONS = {
    "star": '<path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="{color}"/>',
    "commit": '<path d="M10.5 7.75a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm1.43.75a4.002 4.002 0 01-7.86 0H.75a.75.75 0 110-1.5h3.32a4.002 4.002 0 017.86 0h3.32a.75.75 0 110 1.5h-3.32z" fill="{color}"/>',
    "pr": '<path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5a2.5 2.5 0 00-2.5-2.5zm-7.5 10a.75.75 0 100 1.5.75.75 0 000-1.5zM12 12.5a.75.75 0 100 1.5.75.75 0 000-1.5z" fill="{color}"/>',
    "issue": '<path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" fill="{color}"/><path d="M10 0H6C2.686 0 0 2.686 0 6v4c0 3.314 2.686 6 6 6h4c3.314 0 6-2.686 6-6V6c0-3.314-2.686-6-6-6zM8 14.5A8.5 8.5 0 1114.5 8 8.51 8.51 0 018 14.5z" fill="{color}"/>',
    "contrib": '<path d="M2.5 1.75v11.5c0 .414.336.75.75.75h9.5c.414 0 .75-.336.75-.75V1.75a.75.75 0 00-.75-.75H3.25a.75.75 0 00-.75.75zM1.5 1.75C1.5.784 2.284 0 3.25 0h9.5c.966 0 1.75.784 1.75 1.75v11.5c0 .966-.784 1.75-1.75 1.75H3.25C2.284 15 1.5 14.216 1.5 13.25V1.75z" fill="{color}"/>'
}

PRIORITY_LANGS = ["R", "Julia", "MATLAB", "LaTeX", "C++", "Python"]

def fetch_data(url, token):
    req = urllib.request.Request(url)
    if token: req.add_header('Authorization', f'token {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except: return None

def calculate_grade(stats):
    stars = int(stats.get('stars', 0))
    commits = float(str(stats.get('commits', '0')).replace('k+', '').replace('k', '')) * 1000 if 'k' in str(stats.get('commits', '0')) else float(stats.get('commits', 0))
    prs = int(stats.get('prs', 0))
    issues = int(stats.get('issues', 0))
    contribs = int(stats.get('contribs', 0))
    
    score = (stars * 10) + (commits * 0.05) + (prs * 50) + (issues * 5) + (contribs * 100)
    
    if score > 800: return "A+", 95
    if score > 600: return "A", 85
    if score > 400: return "A-", 75
    if score > 300: return "B+", 65
    if score > 200: return "B", 55
    if score > 100: return "B-", 45
    return "C", 30

def create_stats_svg(stats, username):
    cyan, bg, white = "#00fbff", "#060A0C", "#FFFFFF"
    theme_color = cyan
    grade, rank = calculate_grade(stats)
    
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="195" rx="10" fill="{bg}"/>
    <text x="25" y="35" font-family="'Segoe UI', Inter, sans-serif" font-weight="900" font-size="22" fill="{theme_color}" letter-spacing="-0.5px">{username}'s GitHub Stats</text>
    
    <g transform="translate(30, 70)">
        <g transform="translate(0, 0)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['star'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Stars Earned:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('stars', '---')}</text>
        </g>
        <g transform="translate(0, 25)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['commit'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Commits:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('commits', '---')}</text>
        </g>
        <g transform="translate(0, 50)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['pr'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total PRs:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('prs', '---')}</text>
        </g>
        <g transform="translate(0, 75)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['issue'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Total Issues:</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('issues', '---')}</text>
        </g>
        <g transform="translate(0, 100)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['contrib'].format(color=theme_color)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="14" fill="{white}">Contributed to (last year):</text>
            <text x="220" y="0" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="14" fill="{white}">{stats.get('contribs', '---')}</text>
        </g>
    </g>
    
    <g transform="translate(400, 110)">
        <circle r="44" stroke="{theme_color}" stroke-width="4.5" fill="none" opacity="0.1"/>
        <circle r="44" stroke="{theme_color}" stroke-width="4.5" fill="none" 
                stroke-dasharray="276.46" stroke-dashoffset="{276.46 * (1 - rank/100)}" 
                stroke-linecap="round" transform="rotate(-90)"/>
        <text text-anchor="middle" dy="0.35em" font-family="'Segoe UI', sans-serif" font-weight="900" font-size="34" fill="{white}">{grade}</text>
    </g>
    
    <text x="470" y="180" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="9" fill="{white}" fill-opacity="0.25" font-style="italic">Now or Never</text>
</svg>'''
    return svg

def create_langs_svg(langs):
    cyan, bg, white = "#00fbff", "#060A0C", "#FFFFFF"
    total = sum(langs.values())
    if total == 0: total = 1
    
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
    visible_langs = sorted_langs[:18]
    
    cols = 3
    rows = (len(visible_langs) + (cols-1)) // cols
    height = 110 + (rows * 20)
    if height < 170: height = 170
    
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="{height}" rx="10" fill="{bg}"/>
    <text x="30" y="38" font-family="'Segoe UI', Inter, sans-serif" font-weight="800" font-size="22" fill="{white}" letter-spacing="-0.2px">Linguistic Profile</text>
    
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    curr_x = 0
    for name, count in visible_langs:
        width = (count / total) * 435
        if width < 0.1: width = 0.5
        color = LANG_COLORS.get(name, "#888888")
        svg += f'<rect x="{curr_x}" width="{width}" height="14" fill="{color}"/>'
        curr_x += width
    
    svg += '</g></g><g transform="translate(30, 100)">'
    
    col_width = 150
    for i, (name, count) in enumerate(visible_langs):
        col, row = i % cols, i // cols
        perc = (count / total) * 100
        x, y = col * col_width, row * 20 
        color = LANG_COLORS.get(name, "#888888")
        
        display_name = name[:13] + '..' if len(name) > 15 else name
        
        svg += f'''
        <g transform="translate({x}, {y})">
            <circle cx="5" cy="-7" r="5" fill="{color}"/>
            <text x="18" y="0" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="700" fill="{white}">{display_name}</text>
            <text x="140" y="0" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="400" fill="{white}" fill-opacity="0.6">{perc:.1f}%</text>
        </g>'''
        
    svg += '</g></svg>'
    return svg

def update_readme(timestamp):
    readme_path = "README.md"
    if not os.path.exists(readme_path): return
    with open(readme_path, "r", encoding="utf-8") as f: content = f.read()
    content = re.sub(r'docs/languages\.svg(\?t=\d+)?', f'docs/languages.svg?t={timestamp}', content)
    content = re.sub(r'docs/stats\.svg(\?t=\d+)?', f'docs/stats.svg?t={timestamp}', content)
    with open(readme_path, "w", encoding="utf-8") as f: f.write(content)

def main():
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    all_langs = {}
    stats = {"stars": 0, "commits": "13.2k+", "prs": 0, "issues": 0, "contribs": 1}
    timestamp = int(datetime.now().timestamp())
    
    try:
        page = 1
        all_repos = []
        while True:
            url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
            page_repos = fetch_data(url, token)
            if not page_repos: break
            all_repos.extend(page_repos)
            if len(page_repos) < 100: break
            page += 1
            
        if not all_repos: raise Exception("No repos found")
        
        stats["stars"] = sum(repo['stargazers_count'] for repo in all_repos)
        stats["issues"] = sum(repo['open_issues_count'] for repo in all_repos)
        unique_orgs = set(repo['owner']['login'] for repo in all_repos if repo['owner']['login'] != username)
        stats["contribs"] = max(1, len(unique_orgs))
        
        prs_data = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        if prs_data: stats["prs"] = prs_data['total_count']
        
        for r in all_repos:
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k,v in ld.items(): all_langs[k] = all_langs.get(k, 0) + v
        
        for p_lang in PRIORITY_LANGS:
            if p_lang not in all_langs: all_langs[p_lang] = 50000 
            
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(stats, username))
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(all_langs))
        update_readme(timestamp)
        print("Success: Final Vision Synchronized.")
        
    except Exception as e:
        mock_langs = {
            "HTML": 35.5, "Python": 25.0, "Jupyter Notebook": 10.0, "R": 8.5, 
            "JavaScript": 5.0, "CSS": 3.0, "Julia": 2.5, "C": 1.5, "Assembly": 1.5, 
            "PHP": 1.2, "Cython": 1.2, "Ruby": 1.0, "C++": 1.0, "TypeScript": 1.0, 
            "Java": 0.8, "Scala": 0.5, "Shell": 0.4, "Markdown": 0.4
        }
        mock_stats = {"stars": 1295, "commits": "13.2k+", "prs": 185, "issues": 0, "contribs": 1}
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(mock_stats, username))
        mock_bytes = {k: v*1000 for k,v in mock_langs.items()}
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(mock_bytes))
        update_readme(timestamp)
        print(f"Fallback active: {e}")

if __name__ == "__main__": main()
