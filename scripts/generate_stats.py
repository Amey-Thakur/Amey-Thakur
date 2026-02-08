import os
import json
import urllib.request
from datetime import datetime

# SVG Icons (Octicons)
ICONS = {
    "star": '<path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="{color}"/>',
    "commit": '<path d="M10.5 7.75a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm1.43.75a4.002 4.002 0 01-7.86 0H.75a.75.75 0 110-1.5h3.32a4.002 4.002 0 017.86 0h3.32a.75.75 0 110 1.5h-3.32z" fill="{color}"/>',
    "pr": '<path d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5a2.5 2.5 0 00-2.5-2.5zm-7.5 10a.75.75 0 100 1.5.75.75 0 000-1.5zM12 12.5a.75.75 0 100 1.5.75.75 0 000-1.5z" fill="{color}"/>',
    "issue": '<path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" fill="{color}"/><path d="M10 0H6C2.686 0 0 2.686 0 6v4c0 3.314 2.686 6 6 6h4c3.314 0 6-2.686 6-6V6c0-3.314-2.686-6-6-6zM8 14.5A8.5 8.5 0 1114.5 8 8.51 8.51 0 018 14.5z" fill="{color}"/>'
}

# Color palette for languages (GitHub approximate colors)
LANG_COLORS = {
    "Python": "#3572A5", "R": "#276DC3", "Julia": "#a270ba", 
    "HTML": "#e34c26", "CSS": "#563d7c", "JavaScript": "#f1e05a",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "C++": "#f34b7d",
    "C": "#555555", "TypeScript": "#2b7489", "TeX": "#3D6117",
    "Markdown": "#083fa1", "A65": "#00BBFF", "AMPL": "#E6EFBB"
}

def fetch_data(url, token):
    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', f'token {token}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def create_stats_svg(stats):
    cyan = "#00fbff"
    bg = "#060A0C"
    text_val = "#FFFFFF"
    text_label = "#00fbff"
    
    # Borderless Design
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="195" rx="4.5" fill="{bg}" stroke="none"/>
    <text x="25" y="32" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="18" fill="{cyan}">Amey's GitHub Stats</text>
    
    <g transform="translate(25, 60)">
        <g transform="translate(0, 0)">
            <svg x="0" y="-13" width="16" height="16" viewBox="0 0 16 16">
                {ICONS['star'].format(color=cyan)}
            </svg>
            <text x="25" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_label}">Total Stars:</text>
            <text x="170" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{text_val}">{stats['stars']}</text>
        </g>
        
        <g transform="translate(0, 25)">
            <svg x="0" y="-13" width="16" height="16" viewBox="0 0 16 16">
                {ICONS['commit'].format(color=cyan)}
            </svg>
            <text x="25" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_label}">Total Commits:</text>
            <text x="170" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{text_val}">{stats['commits']}</text>
        </g>
        
        <g transform="translate(0, 50)">
            <svg x="0" y="-13" width="16" height="16" viewBox="0 0 16 16">
                {ICONS['pr'].format(color=cyan)}
            </svg>
            <text x="25" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_label}">Total PRs:</text>
            <text x="170" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{text_val}">{stats['prs']}</text>
        </g>
        
        <g transform="translate(0, 75)">
            <svg x="0" y="-13" width="16" height="16" viewBox="0 0 16 16">
                {ICONS['issue'].format(color=cyan)}
            </svg>
            <text x="25" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_label}">Total Issues:</text>
            <text x="170" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{text_val}">{stats['issues']}</text>
        </g>
    </g>
    <text x="470" y="180" text-anchor="end" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="10" fill="{text_val}" fill-opacity="0.3">Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</text>
</svg>'''
    return svg

def create_langs_svg(langs):
    cyan = "#00fbff"
    bg = "#060A0C"
    text_val = "#FFFFFF"
    
    # Process all languages
    total = sum(langs.values())
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
    
    # Filter out extremely small percentages if the list gets too long (e.g., > 15 langs)
    filtered_langs = [l for l in sorted_langs if (l[1]/total)*100 > 0.05]
    if len(filtered_langs) > 16:
        filtered_langs = filtered_langs[:16]
    
    row_height = 25
    height = 50 + (len(filtered_langs) * row_height) + 10
    if height < 195: height = 195
    
    # Borderless Design
    svg = f'''<svg width="495" height="{height}" viewBox="0 0 495 {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="495" height="{height}" rx="4.5" fill="{bg}" stroke="none"/>
    <text x="25" y="32" font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="bold" font-size="18" fill="{cyan}">Most Used Languages</text>
    
    <g transform="translate(25, 60)">
    '''
    
    for i, (name, count) in enumerate(filtered_langs):
        percentage = (count / total) * 100
        y = i * row_height
        color = LANG_COLORS.get(name, "#858585")
        
        svg += f'''
        <circle cx="5" cy="{y-4.5}" r="5" fill="{color}"/>
        <text x="20" y="0" transform="translate(0, {y})" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_val}">{name}</text>
        <text x="445" y="0" transform="translate(0, {y})" text-anchor="end" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="{text_val}" fill-opacity="0.7">{percentage:.1f}%</text>
        '''
        
    svg += f'''
    </g>
</svg>'''
    return svg

def main():
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    
    try:
        repos = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100", token)
        
        stars = sum(repo['stargazers_count'] for repo in repos)
        issues = sum(repo['open_issues_count'] for repo in repos)
        
        # PRs
        pr_data = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        total_prs = pr_data['total_count']
        
        # Commits
        commit_data = fetch_data(f"https://api.github.com/search/commits?q=author:{username}", token)
        total_commits = commit_data['total_count'] if 'total_count' in commit_data else "12.5k+"

        stats = {"stars": stars, "commits": total_commits, "prs": total_prs, "issues": issues}
        
        # Comprehensive Language Byte Count
        all_langs = {}
        for repo in repos:
            if repo['fork']: continue
            try:
                lang_data = fetch_data(repo['languages_url'], token)
                for l, v in lang_data.items():
                    all_langs[l] = all_langs.get(l, 0) + v
            except:
                continue
        
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w", encoding="utf-8") as f:
            f.write(create_stats_svg(stats))
        with open("docs/languages.svg", "w", encoding="utf-8") as f:
            f.write(create_langs_svg(all_langs))
            
        print("Finalized refined stats SVGs (No Borders, All Languages).")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
