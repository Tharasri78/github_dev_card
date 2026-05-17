import sys
import os

# Imports based on the prompt's requested Google ADK components
try:
    from mock_google_adk.adk.agents import Agent
    from mock_google_adk.adk.tools import McpToolset
except ImportError:
    # Fallback to plausible genai imports if adk is integrated there
    from google.genai.agents import Agent, McpToolset

github_card_agent = Agent(
    model="gemini-2.5-flash",
    system_instruction=(
        "You are a GitHub profile analyst and dev card generator. When a user gives you a "
        "GitHub username, you ALWAYS follow this exact sequence: first call scrape_github, "
        "then analyze_profile with the result, then generate_card_html with all three inputs, "
        "then save_card. Never skip steps. Be enthusiastic about developers' work. "
        "If the profile is private or doesn't exist, say so clearly."
    ),
    toolsets=[
        McpToolset(
            command="python",
            args=["backend/mcp_server.py"],
            transport="stdio"
        )
    ]
)
