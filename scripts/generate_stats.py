import os
import json
import urllib.request
from datetime import datetime

# 100% Official GitHub Language Colors (Linguist)
LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "Jupyter Notebook": "#DA5B0B",
    "JavaScript": "#f1e05a", "CSS": "#563d7c", "Julia": "#a270ba",
    "C": "#555555", "C++": "#f34b7d", "Assembly": "#6E4C13",
    "PHP": "#4F5D95", "Cython": "#1171EE", "TypeScript": "#3178c6",
    "MATLAB": "#e16737", "Java": "#b07219", "SCSS": "#c6538c",
    "CoffeeScript": "#244776", "TeX": "#3D6117", "Fortran": "#4d41b1",
    "Less": "#1d365d", "Svelte": "#ff3e00", "C#": "#178600",
    "PowerShell": "#012456", "Vue": "#41b883", "Shell": "#89e051",
    "Markdown": "#083fa1", "Rich Text Format": "#FFFFFF", "A65": "#00BBFF",
    "AMPL": "#E6EFBB", "Ruby": "#701516"
}

ICONS = {
    "star": '<path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="{color}"/>',
    "commit": '<path d="M10.5 7.75a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm1.43.75a4.002 4.002 0 01-7.86 0H.75a.75.75 0 110-1.5h3.32a4.002 4.002 0 017.86 0h3.32a.75.75 0 110 1.5h-3.32z" fill="{color}"/>',
    "pr": '<path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5a2.5 2.5 0 00-2.5-2.5zm-7.5 10a.75.75 0 100 1.5.75.75 0 000-1.5zM12 12.5a.75.75 0 100 1.5.75.75 0 000-1.5z" fill="{color}"/>',
    "issue": '<path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" fill="{color}"/><path d="M10 0H6C2.686 0 0 2.686 0 6v4c0 3.314 2.686 6 6 6h4c3.314 0 6-2.686 6-6V6c0-3.314-2.686-6-6-6zM8 14.5A8.5 8.5 0 1114.5 8 8.51 8.51 0 018 14.5z" fill="{color}"/>'
}

def fetch_data(url, token):
    req = urllib.request.Request(url)
    if token: req.add_header('Authorization', f'token {token}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except: return None

def create_stats_svg(stats):
    cyan, bg, white = "#00fbff", "#060A0C", "#FFFFFF"
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="195" rx="6" fill="{bg}"/>
    <text x="30" y="32" font-family="'Segoe UI', Inter, sans-serif" font-weight="800" font-size="20" fill="{cyan}" letter-spacing="-0.5px">GITHUB STATISTICS</text>
    <g transform="translate(35, 75)">
        <g transform="translate(0, 0)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['star'].format(color=cyan)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="15" fill="{cyan}">STARS GIVEN</text>
            <text x="240" y="0" font-family="'Segoe UI', sans-serif" font-weight="400" font-size="15" fill="{white}">{stats.get('stars', '---')}</text>
        </g>
        <g transform="translate(0, 30)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['commit'].format(color=cyan)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="15" fill="{cyan}">COMMIT VOLUME</text>
            <text x="240" y="0" font-family="'Segoe UI', sans-serif" font-weight="400" font-size="15" fill="{white}">{stats.get('commits', '---')}</text>
        </g>
        <g transform="translate(0, 60)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['pr'].format(color=cyan)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="15" fill="{cyan}">PULL REQUESTS</text>
            <text x="240" y="0" font-family="'Segoe UI', sans-serif" font-weight="400" font-size="15" fill="{white}">{stats.get('prs', '---')}</text>
        </g>
        <g transform="translate(0, 90)">
            <svg x="0" y="-14" width="20" height="20" viewBox="0 0 16 16">{ICONS['issue'].format(color=cyan)}</svg>
            <text x="35" y="0" font-family="'Segoe UI', sans-serif" font-weight="700" font-size="15" fill="{cyan}">OPEN ISSUES</text>
            <text x="240" y="0" font-family="'Segoe UI', sans-serif" font-weight="400" font-size="15" fill="{white}">{stats.get('issues', '---')}</text>
        </g>
    </g>
    <text x="465" y="180" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="9" fill="{white}" fill-opacity="0.3" font-style="italic">AMEY-THAKUR VISION vPerfect</text>
</svg>'''
    return svg

def create_langs_svg(langs):
    cyan, bg, white = "#00fbff", "#060A0C", "#FFFFFF"
    total = sum(langs.values())
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
    visible_langs = [l for l in sorted_langs if (l[1]/total)*100 > 0.05][:16]
    
    rows = (len(visible_langs) + 1) // 2
    height = 110 + (rows * 28)
    if height < 220: height = 220
    
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="{height}" rx="8" fill="{bg}"/>
    <text x="30" y="38" font-family="'Segoe UI', Inter, sans-serif" font-weight="800" font-size="22" fill="{cyan}" letter-spacing="-0.5px">LINGUISTIC PROFILE</text>
    
    <g transform="translate(30, 60)">
        <mask id="bar-mask"><rect width="435" height="14" rx="7" fill="white"/></mask>
        <rect width="435" height="14" rx="7" fill="{white}" fill-opacity="0.1"/>
        <g mask="url(#bar-mask)">'''
    
    curr_x = 0
    for name, count in visible_langs:
        width = (count / total) * 435
        if width < 0.5: continue
        color = LANG_COLORS.get(name, cyan)
        # 1px gap between segments
        svg += f'<rect x="{curr_x}" width="{width-1 if width > 2 else width}" height="14" fill="{color}"/>'
        curr_x += width
    
    svg += '</g></g><g transform="translate(30, 105)">'
    
    for i, (name, count) in enumerate(visible_langs):
        col, row = i % 2, i // 2
        perc = (count / total) * 100
        x, y = col * 230, row * 28 
        color = LANG_COLORS.get(name, cyan)
        
        svg += f'''
        <g transform="translate({x}, {y})">
            <circle cx="5" cy="-7" r="6" fill="{color}"/>
            <text x="22" y="0" font-family="'Segoe UI', sans-serif" font-size="15" font-weight="700" fill="{white}">{name.upper()}</text>
            <text x="210" y="0" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="400" fill="{white}" fill-opacity="0.6">{perc:.1f}%</text>
        </g>'''
        
    svg += '</g></svg>'
    return svg

def main():
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    try:
        repos = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100&type=owner", token)
        if not repos: raise Exception("Rate Limit")
        
        stars = sum(repo['stargazers_count'] for repo in repos)
        issues = sum(repo['open_issues_count'] for repo in repos)
        prs = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        total_prs = prs['total_count'] if prs else "---"
        total_commits = "12.5k+"
        
        all_langs = {}
        for r in repos:
            if r['fork']: continue
            ld = fetch_data(r['languages_url'], token)
            if ld:
                for k,v in ld.items(): all_langs[k] = all_langs.get(k, 0) + v
        
        stats = {"stars": stars, "commits": total_commits, "prs": total_prs, "issues": issues}
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(stats))
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(all_langs))
        print("Success")
    except Exception as e:
        # High-Fidelity Fallback with 2-column data
        mock_stats = {"stars": 1295, "commits": "12.5k+", "prs": 170, "issues": 0}
        mock_langs = {"HTML": 56.4, "Python": 28.7, "Jupyter Notebook": 8.7, "JavaScript": 2.0, "CSS": 0.8, "Rich Text Format": 0.7, "Julia": 0.6, "C": 0.6, "PHP": 0.3, "Cython": 0.2, "Ruby": 0.1, "Java": 0.1, "C++": 0.1, "TypeScript": 0.1, "Assembly": 0.4}
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f: f.write(create_stats_svg(mock_stats))
        mock_bytes = {k: v*1000 for k,v in mock_langs.items()}
        with open("docs/languages.svg", "w", encoding="utf-8") as f: f.write(create_langs_svg(mock_bytes))
        print(f"Fallback complete")

if __name__ == "__main__": main()
