import os
import json
import requests
from fastmcp import FastMCP
from google.genai import Client

mcp = FastMCP("github-card-tools")

@mcp.tool()
def scrape_github(username: str) -> dict:
    """Scrapes GitHub user data and their top repositories."""
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    
    headers = {}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
        
    user_resp = requests.get(user_url, headers=headers)
    if user_resp.status_code != 200:
        return {"error": "User not found or API limit reached."}
    
    user_data = user_resp.json()
    
    repos_resp = requests.get(repos_url, headers=headers)
    repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
    
    top_repos = sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
    
    repo_details = []
    languages = {}
    for repo in top_repos:
        repo_details.append({
            "name": repo.get("name"),
            "stars": repo.get("stargazers_count"),
            "language": repo.get("language"),
            "description": repo.get("description")
        })
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
            
    return {
        "name": user_data.get("name") or username,
        "avatar_url": user_data.get("avatar_url"),
        "bio": user_data.get("bio"),
        "location": user_data.get("location"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "top_repos": repo_details,
        "most_used_languages": languages
    }

@mcp.tool()
def analyze_profile(github_data: dict) -> dict:
    """Analyzes a GitHub profile using Gemini 2.5 Flash to determine developer vibe, top skills, fun fact, and card theme."""
    if "error" in github_data:
        return github_data
        
    if not os.getenv("GEMINI_API_KEY"):
        # Dynamically build a custom, personalized response based on the actual github_data
        name = github_data.get("name") or "A passionate developer"
        languages = list(github_data.get("most_used_languages", {}).keys())
        top_skills = languages[:3] if languages else ["Python", "JavaScript", "HTML"]
        while len(top_skills) < 3:
            for skill in ["Python", "JavaScript", "HTML"]:
                if skill not in top_skills and len(top_skills) < 3:
                    top_skills.append(skill)
                    
        # Determine theme dynamically based on languages
        card_theme = "builder"
        lang_set = {l.lower() for l in languages}
        if any(l in lang_set for l in ["jupyter notebook", "r", "julia"]):
            card_theme = "researcher"
        elif any(l in lang_set for l in ["c++", "c", "assembly", "shell", "rust"]):
            card_theme = "hacker"
        elif any(l in lang_set for l in ["css", "html", "typescript", "javascript"]):
            card_theme = "builder"
            if "css" in lang_set and len(lang_set) <= 2:
                card_theme = "designer"
                
        # Personalize developer vibe
        if github_data.get("bio"):
            vibe = f"{name} is a developer who describes themselves as: \"{github_data.get('bio')}\""
        else:
            vibe = f"{name} is a detail-oriented developer specializing in {', '.join(top_skills[:2])}."
            
        # Personalize fun fact
        fun_fact = f"Tends to focus heavily on {top_skills[0]} repositories with {github_data.get('public_repos', 0)} total public projects."
        top_repos = github_data.get("top_repos", [])
        if top_repos:
            repo_name = top_repos[0].get("name", "")
            repo_lang = top_repos[0].get("language", top_skills[0]) or top_skills[0]
            fun_fact = f"Active creator of repositories like '{repo_name}', showcasing excellent work in {repo_lang}."
            
        return {
            "developer_vibe": vibe,
            "top_skills": top_skills,
            "fun_fact": fun_fact,
            "card_theme": card_theme
        }
        
    client = Client() # Uses GEMINI_API_KEY from env
    
    prompt = f"""
    Analyze this GitHub profile data:
    {json.dumps(github_data, indent=2)}
    
    Return ONLY a JSON object with these exactly keys:
    - "developer_vibe": A 1 sentence personality summary of the developer.
    - "top_skills": A list of their top 3 skills or languages.
    - "fun_fact": Something clever inferred from their repos or bio.
    - "card_theme": Choose exactly one of: "hacker", "builder", "researcher", "designer", "open-source-hero".
      * "researcher": If they focus on data science, analytics, machine learning, Python, Jupyter Notebooks, or research.
      * "hacker": If they focus on cybersecurity, low-level programming, Linux, C/C++, system tools, or scripting.
      * "builder": If they focus on web development, full-stack, frontend, backend, building apps (JavaScript, React, HTML, CSS, TypeScript, Go).
      * "designer": If they focus on UI/UX, CSS art, creative coding, front-end aesthetics.
      * "open-source-hero": If they have highly starred repositories or contribute massively to open source.
      
    Select the theme that best matches the developer's repositories and skills. For data-heavy, analytical, or notebook-based work, choose "researcher".
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
        
    try:
        return json.loads(text.strip())
    except Exception as e:
        return {
            "error": f"Failed to parse analysis: {str(e)}", 
            "developer_vibe": "A mysterious developer.", 
            "top_skills": ["Code"], 
            "fun_fact": "Too complex to understand.", 
            "card_theme": "researcher"
        }

@mcp.tool()
def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generates a self-contained HTML string for a beautiful dev card."""
    if "error" in github_data:
        return f"<div class='error'>Error generating card: {github_data.get('error')}</div>"
        
    theme = analysis.get("card_theme", "hacker")
    
    # Beautiful premium themes matching the layout in Image 2
    theme_styles = {
        "researcher": {
            "bg": "#131927",
            "text": "#cbd5e1",
            "accent": "#0f1422",
            "border": "#5d5fef",
            "pill_bg": "#222d44",
            "pill_text": "#cbd5e1",
            "badge_bg": "#5d5fef",
            "badge_text": "#ffffff",
            "font": "'Inter', -apple-system, sans-serif"
        },
        "hacker": {
            "bg": "#050505",
            "text": "#39ff14",
            "accent": "#0a0f0a",
            "border": "#39ff14",
            "pill_bg": "#142214",
            "pill_text": "#39ff14",
            "badge_bg": "#39ff14",
            "badge_text": "#050505",
            "font": "'Courier New', Courier, monospace"
        },
        "builder": {
            "bg": "#0c0a09",
            "text": "#e7e5e4",
            "accent": "#1c1917",
            "border": "#ea580c",
            "pill_bg": "#292524",
            "pill_text": "#fafaf9",
            "badge_bg": "#ea580c",
            "badge_text": "#ffffff",
            "font": "'Inter', -apple-system, sans-serif"
        },
        "designer": {
            "bg": "#170f1d",
            "text": "#f472b6",
            "accent": "#0e0912",
            "border": "#ec4899",
            "pill_bg": "#2e183b",
            "pill_text": "#fdf2f8",
            "badge_bg": "#ec4899",
            "badge_text": "#ffffff",
            "font": "'Inter', -apple-system, sans-serif"
        },
        "open-source-hero": {
            "bg": "#0b0f19",
            "text": "#fbbf24",
            "accent": "#060910",
            "border": "#fbbf24",
            "pill_bg": "#1e293b",
            "pill_text": "#fef3c7",
            "badge_bg": "#fbbf24",
            "badge_text": "#0b0f19",
            "font": "'Inter', -apple-system, sans-serif"
        }
    }
    
    styles = theme_styles.get(theme, theme_styles["researcher"])
    
    repos_html = ""
    for repo in github_data.get("top_repos", [])[:3]:
        lang = repo.get('language') or 'None'
        repos_html += f'''
        <div style="font-size: 0.95em; color: {styles['text']}; margin-bottom: 8px; text-align: left;">
            <strong style="color: #ffffff; font-weight: 600;">{repo.get('name')}</strong>: {lang} (⭐ {repo.get('stars')})
        </div>
        '''
        
    skills_html = "".join([f"<span style='background: {styles['pill_bg']}; color: {styles['pill_text']}; padding: 6px 12px; border-radius: 6px; font-size: 0.85em; font-weight: 500; margin-right: 8px;'>{s}</span>" for s in analysis.get("top_skills", [])])
    
    # Enclose vibe in double quotes if it doesn't already have them
    vibe = analysis.get('developer_vibe', '')
    if vibe and not (vibe.startswith('"') and vibe.endswith('"')):
        vibe = f'"{vibe}"'
        
    html = f'''
    <div style="background-color: {styles['bg']}; color: {styles['text']}; font-family: {styles['font']}; padding: 30px; border-radius: 16px; width: 100%; box-sizing: border-box; border: 2px solid {styles['border']}; box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: left;">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
            <img src="{github_data.get('avatar_url')}" alt="{username}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover;">
            <div>
                <h2 style="margin: 0; font-size: 1.4em; font-weight: bold; color: #ffffff;">{github_data.get('name')}</h2>
                <div style="font-size: 0.95em; color: #94a3b8; margin-top: 2px;">@{username}</div>
            </div>
        </div>
        
        <p style="font-style: italic; font-size: 1.05em; color: #cbd5e1; line-height: 1.4; margin: 0 0 20px 0;">{vibe}</p>
        
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;">
            {skills_html}
        </div>
        
        <div style="background-color: {styles['accent']}; display: flex; justify-content: space-around; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; border: 1px solid #1e293b;">
            <div>
                <div style="font-size: 1.25em; font-weight: bold; color: #ffffff;">{github_data.get('public_repos')}</div>
                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 2px;">Repos</div>
            </div>
            <div style="border-left: 1px solid #334155; height: 35px; align-self: center;"></div>
            <div>
                <div style="font-size: 1.25em; font-weight: bold; color: #ffffff;">{github_data.get('followers')}</div>
                <div style="font-size: 0.85em; color: #94a3b8; margin-top: 2px;">Followers</div>
            </div>
        </div>
        
        <h3 style="margin: 0 0 12px 0; font-size: 0.85em; font-weight: bold; letter-spacing: 1px; color: #94a3b8; text-transform: uppercase;">Top Projects</h3>
        <div style="margin-bottom: 20px;">
            {repos_html}
        </div>
        
        <hr style="border: 0; border-top: 1px solid #334155; margin: 15px 0;">
        
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px;">
            <div style="font-size: 0.85em; color: #94a3b8; line-height: 1.4; margin: 0; max-width: 75%;">
                {analysis.get('fun_fact')}
            </div>
            <span style="background-color: {styles['badge_bg']}; color: {styles['badge_text']}; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap;">
                {theme}
            </span>
        </div>
    </div>
    '''
    return html

@mcp.tool()
def save_card(username: str, html: str) -> str:
    """Saves the HTML to static/cards/{username}.html and returns the URL path."""
    cards_dir = os.path.join(os.path.dirname(__file__), "static", "cards")
    os.makedirs(cards_dir, exist_ok=True)
    
    file_path = os.path.join(cards_dir, f"{username}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return f"/card/{username}.html"

if __name__ == "__main__":
    mcp.run()
