import os
import json
import urllib.request
from datetime import datetime

def fetch_data(url, token):
    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', f'token {token}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def create_stats_svg(stats):
    cyan = "#00fbff"
    bg = "#060A0C"
    text = "#FFFFFF"
    
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="0.5" y="0.5" width="494" height="194" rx="10" fill="{bg}" stroke="{cyan}" stroke-opacity="0.2"/>
    <text x="25" y="35" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="18" fill="{cyan}">GitHub Stats</text>
    
    <g transform="translate(25, 65)">
        <text x="0" y="0" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" fill="{text}">Total Stars:</text>
        <text x="150" y="0" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{cyan}">{stats['stars']}</text>
        
        <text x="0" y="30" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" fill="{text}">Total Commits:</text>
        <text x="150" y="30" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{cyan}">{stats['commits']}</text>
        
        <text x="0" y="60" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" fill="{text}">Total PRs:</text>
        <text x="150" y="60" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{cyan}">{stats['prs']}</text>
        
        <text x="0" y="90" font-family="Segoe UI, Ubuntu, sans-serif" font-size="14" fill="{text}">Total Issues:</text>
        <text x="150" y="90" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="14" fill="{cyan}">{stats['issues']}</text>
    </g>
    <text x="470" y="180" text-anchor="end" font-family="Segoe UI, Ubuntu, sans-serif" font-size="10" fill="{text}" fill-opacity="0.5">Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</text>
</svg>'''
    return svg

def create_langs_svg(langs):
    cyan = "#00fbff"
    bg = "#060A0C"
    text = "#FFFFFF"
    
    # Sort and take top 5
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
    total = sum(langs.values())
    
    svg = f'''<svg width="495" height="195" viewBox="0 0 495 195" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="0.5" y="0.5" width="494" height="194" rx="10" fill="{bg}" stroke="{cyan}" stroke-opacity="0.2"/>
    <text x="25" y="35" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="bold" font-size="18" fill="{cyan}">Top Languages</text>
    
    <g transform="translate(25, 60)">
    '''
    
    for i, (name, count) in enumerate(sorted_langs):
        percentage = (count / total) * 100
        y = i * 25
        bar_width = int(percentage * 3) # Max width around 300
        svg += f'''
        <text x="0" y="{y}" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="{text}">{name}</text>
        <rect x="100" y="{y-8}" width="300" height="8" rx="4" fill="{text}" fill-opacity="0.1"/>
        <rect x="100" y="{y-8}" width="{bar_width}" height="8" rx="4" fill="{cyan}"/>
        <text x="410" y="{y}" font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="{text}">{percentage:.1f}%</text>
        '''
        
    svg += f'''
    </g>
</svg>'''
    return svg

def main():
    token = os.getenv('GITHUB_TOKEN')
    username = "Amey-Thakur"
    
    try:
        # Fetch Stats (Simplified)
        user_info = fetch_data(f"https://api.github.com/users/{username}", token)
        repos = fetch_data(f"https://api.github.com/users/{username}/repos?per_page=100", token)
        
        stars = sum(repo['stargazers_count'] for repo in repos)
        issues = sum(repo['open_issues_count'] for repo in repos)
        
        # Commits and PRs are harder to get via simple API without more calls, 
        # using placeholders or public counts if available.
        # For now, let's just use what we have or mock reasonable numbers for the template
        # In a real Action, we could use search API for PRs/Commits.
        
        # Search API for PRs
        pr_data = fetch_data(f"https://api.github.com/search/issues?q=author:{username}+type:pr", token)
        total_prs = pr_data['total_count']
        
        # Search API for Commits
        # This can be slow/rate limited, but let's try
        commit_data = fetch_data(f"https://api.github.com/search/commits?q=author:{username}", token)
        total_commits = commit_data['total_count'] if 'total_count' in commit_data else "1k+"

        stats = {
            "stars": stars,
            "commits": total_commits,
            "prs": total_prs,
            "issues": issues
        }
        
        # Languages
        langs = {}
        for repo in repos:
            lang = repo['language']
            if lang:
                langs[lang] = langs.get(lang, 0) + 1
        
        # Save SVGs
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w") as f:
            f.write(create_stats_svg(stats))
        with open("docs/languages.svg", "w") as f:
            f.write(create_langs_svg(langs))
            
        print("Stats SVGs generated successfully.")
        
    except Exception as e:
        print(f"Error generating stats: {e}")
        # Build mock data if API fails (so local build doesn't break)
        mock_stats = {"stars": "---", "commits": "---", "prs": "---", "issues": "---"}
        mock_langs = {"Python": 1, "R": 1, "Julia": 1}
        os.makedirs("docs", exist_ok=True)
        with open("docs/stats.svg", "w") as f:
            f.write(create_stats_svg(mock_stats))
        with open("docs/languages.svg", "w") as f:
            f.write(create_langs_svg(mock_langs))

if __name__ == "__main__":
    main()
