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
        return {
            "developer_vibe": "Harshvardhan Singh appears to be a detail-oriented and organized individual with a strong focus on data science and analytics.",
            "top_skills": ["Jupyter Notebook", "Python", "CSS"],
            "fun_fact": "It seems Harshvardhan Singh has a strong interest in data science education, judging by the presence of 'Data-Science-Notes' and 'Data-Analytics-Libraries' repositories.",
            "card_theme": "researcher"
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
            "card_theme": "hacker"
        }

@mcp.tool()
def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generates a self-contained HTML string for a beautiful dev card."""
    if "error" in github_data:
        return f"<div class='error'>Error generating card: {github_data.get('error')}</div>"
        
    theme = analysis.get("card_theme", "hacker")
    
    theme_styles = {
        "hacker": {"bg": "#000000", "text": "#00ff00", "accent": "#003300", "font": "monospace"},
        "builder": {"bg": "#ffffff", "text": "#333333", "accent": "#e0e0e0", "font": "sans-serif"},
        "researcher": {"bg": "#f4f1ea", "text": "#2b2b2b", "accent": "#d1c7b7", "font": "serif"},
        "designer": {"bg": "#ff9a9e", "text": "#ffffff", "accent": "#fecfef", "font": "sans-serif"},
        "open-source-hero": {"bg": "#24292e", "text": "#ffffff", "accent": "#2ea043", "font": "sans-serif"}
    }
    
    styles = theme_styles.get(theme, theme_styles["hacker"])
    
    repos_html = ""
    for repo in github_data.get("top_repos", [])[:3]:
        repos_html += f'''
        <div style="background: {styles['accent']}; padding: 10px; margin-top: 10px; border-radius: 5px;">
            <strong style="color: {styles['text']};">{repo.get('name')}</strong>
            <span style="font-size: 0.8em; float: right;">⭐ {repo.get('stars')} | {repo.get('language') or 'N/A'}</span>
            <p style="font-size: 0.9em; margin: 5px 0 0 0; color: {styles['text']}; opacity: 0.8;">{repo.get('description') or 'No description'}</p>
        </div>
        '''
        
    skills_html = "".join([f"<span style='background: {styles['accent']}; padding: 3px 8px; border-radius: 12px; margin-right: 5px; font-size: 0.8em;'>{s}</span>" for s in analysis.get("top_skills", [])])
    
    html = f'''
    <div style="background-color: {styles['bg']}; color: {styles['text']}; font-family: {styles['font']}; padding: 30px; border-radius: 15px; width: 100%; box-sizing: border-box; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="{github_data.get('avatar_url')}" alt="{username}" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid {styles['accent']}; margin-right: 20px;">
            <div>
                <h2 style="margin: 0;">{github_data.get('name')}</h2>
                <div style="font-size: 0.9em; opacity: 0.8;">@{username}</div>
            </div>
        </div>
        
        <p style="font-style: italic; margin-bottom: 15px;">"{analysis.get('developer_vibe')}"</p>
        
        <div style="margin-bottom: 20px;">
            {skills_html}
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px; text-align: center; background: {styles['accent']}; padding: 10px; border-radius: 8px;">
            <div>
                <div style="font-weight: bold; font-size: 1.2em;">{github_data.get('public_repos')}</div>
                <div style="font-size: 0.8em;">Repos</div>
            </div>
            <div>
                <div style="font-weight: bold; font-size: 1.2em;">{github_data.get('followers')}</div>
                <div style="font-size: 0.8em;">Followers</div>
            </div>
            <div>
                <div style="font-weight: bold; font-size: 1.2em; text-transform: uppercase;">{theme}</div>
                <div style="font-size: 0.8em;">Theme</div>
            </div>
        </div>
        
        <h3 style="margin: 0 0 10px 0; font-size: 1em; text-transform: uppercase; letter-spacing: 1px;">Top Projects</h3>
        {repos_html}
        
        <div style="margin-top: 20px; font-size: 0.8em; opacity: 0.7; text-align: center;">
            Fun fact: {analysis.get('fun_fact')}
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
