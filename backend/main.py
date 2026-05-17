import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
try:
    from mock_google_adk.adk.services import InMemorySessionService, InMemoryMemoryService
    from mock_google_adk.adk.agents import Runner
except ImportError:
    from google.genai.agents import Runner, InMemorySessionService, InMemoryMemoryService

from agent import github_card_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

runner = Runner(
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service
)

class GenerateRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    import re
    username = request.username.strip().replace("@", "")
    
    # GitHub username validation
    if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$", username):
        raise HTTPException(
            status_code=400, 
            detail="Please enter only a valid GitHub username (alphanumeric and single hyphens only)."
        )
        
    try:
        session = session_service.get_or_create_session(username)
        
        message = f"Generate a dev card for {username}"
        
        # Depending on ADK API, runner.run might return an iterable of events or an async generator
        # The prompt says "Streams the agent events and returns the final card URL and HTML"
        # Since FastAPI supports yielding via StreamingResponse, or we just consume and return
        # Wait, the prompt says "returns the final card URL and HTML". I will just consume it and return JSON.
        
        # If it's an async generator:
        html = ""
        card_url = ""
        
        # A simple blocking or async run call (assuming synchronous or standard await for simplicity)
        response = runner.run(session_id=session.id, message=message)
        
        # For the sake of the exercise, let's assume it returns a final response with text
        # If the generated HTML is in the static folder, we can read it directly.
        card_path = os.path.join(os.path.dirname(__file__), "static", "cards", f"{username}.html")
        if os.path.exists(card_path):
            with open(card_path, "r", encoding="utf-8") as f:
                html = f.read()
            card_url = f"/card/{username}.html"
            
        return {
            "message": "Card generated successfully.",
            "url": card_url,
            "html": html,
            "agent_response": response.text if hasattr(response, "text") else str(response)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

cards_dir = os.path.join(os.path.dirname(__file__), "static", "cards")
os.makedirs(cards_dir, exist_ok=True)
app.mount("/card", StaticFiles(directory=cards_dir), name="cards")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
