# ✨ AI-Powered GitHub Dev Card Generator ✨

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini%202.5%20Flash-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)

A state-of-the-art web application that generates premium, hyper-personalized developer cards based on public GitHub profiles. Leveraging **FastAPI**, **Gemini 2.5 Flash**, and **FastMCP**, the generator scrapes real-time user data and dynamically analyzes repository patterns, tech stacks, and bio sentiments to classify developers into distinct coder archetypes with stunning custom-themed developer badges.

---

## 🎨 Premium Theme Archetypes

The generator classifies developers dynamically into one of five custom, visually-stunning theme archetypes with tailormade styling:

| Archetype | Theme Persona | Visual Identity & Palette |
| :--- | :--- | :--- |
| **🔍 Researcher** | Machine Learning, Data Analytics, Jupyter Notebooks | Deep Space Blue (`#131927`) & Soft Indigo Accent |
| **🥷 Hacker** | Cybersecurity, Low-level Systems, C/C++, Rust | Matrix Black (`#050505`) & Neon Green Glow |
| **🛠️ Builder** | Web Development, Apps, JavaScript/TypeScript | Steel Charcoal (`#0c0a09`) & Electric Orange Accent |
| **🎨 Designer** | CSS Art, UI/UX Engineering, Frontend Aesthetics | Velvet Indigo (`#170f1d`) & Vibrant Pink Accent |
| **🌟 Open-Source Hero** | Massively Starred Repositories & OSS Contributors | Midnight Navy (`#0b0f19`) & Warm Amber Gold |

---

## 🚀 Key Features

* **🧠 Gemini-Powered Bio-Vibe Analysis**: Analyzes natural language bio sentiments, repository descriptions, and programming language statistics to generate custom vibe statements and witty coder fun-facts.
* **⚡ Smart Dynamic Fallback Scanner**: Runs fully operational out of the box! If no `GEMINI_API_KEY` is present, a smart heuristic engine analyses profile metadata dynamically to compile customized cards without hardcoded mocks.
* **🎨 Modern Responsive Interface**: Complete glassmorphic card design with dark-mode tailored palettes, elegant micro-animations, skeleton screen loaders, and graceful error alerts for invalid usernames.
* **📦 Consolidated Single-Service Deployment**: Configured as a unified full-stack architecture where FastAPI hosts both the static frontend and the card generation endpoints, ensuring zero CORS friction and minimal hosting costs.
* **🛡️ Character-Level Input Sanitization**: Form validation blocks invalid characters and extracts correct usernames even from copy-pasted full GitHub profile URLs.

---

## 🏗️ Repository Architecture

```directory
github-dev-card/
├── backend/
│   ├── frontend/             # Embedded copy of frontend for consolidated container
│   ├── google/               # Mock ADK / namespace package
│   │   └── adk/              
│   ├── mock_google_adk/      # Local mock package 
│   ├── static/               
│   │   └── cards/            # Cache for generated HTML dev cards
│   ├── Dockerfile            # Container deployment manifest
│   ├── main.py               # FastAPI router and full-stack mounting entrypoint
│   ├── mcp_server.py         # FastMCP tools & profile analysis engine
│   └── requirements.txt      # Production package dependencies
├── frontend/                 # Source code for local development
│   ├── index.html            # Premium Glassmorphic Web App UI
│   └── (static assets)
├── docker-compose.yml        # Orchestration manifest for local multi-service testing
└── README.md                 # Project Documentation
```

---

## 🛠️ FastMCP Toolset Definition

The backend implements four modular **FastMCP** tools under `backend/mcp_server.py` to coordinate card creation:

1. **`scrape_github(username: str) -> dict`**: Contacts GitHub REST API to fetch profile metadata, follower metrics, and repositories, parsing top languages.
2. **`analyze_profile(github_data: dict) -> dict`**: Evaluates scraped profile statistics and applies Gemini 2.5 Flash to generate top skills, developer vibe summaries, fun facts, and theme classification.
3. **`generate_card_html(username: str, github_data: dict, analysis: dict) -> str`**: Assembles a fully styled, self-contained HTML card element with CSS custom variables matching the chosen archetype.
4. **`save_card(username: str, html: str) -> str`**: Persists the resulting HTML card to `/static/cards/{username}.html`, caching it for web access and share links.

---

## 💻 Local Setup & Execution

### 1. Configure Environment Variables
Create a `.env` file inside the `backend/` directory or root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_optional_github_token_here
```
*(Configuring a `GITHUB_TOKEN` increases GitHub API rate limits from 60 to 5000 requests/hour).*

### 2. Standard Native Launch
Ensure Python 3.10+ is installed:
```powershell
# Navigate into backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run server in reload mode
uvicorn main:app --reload --port 8080
```
Open `http://localhost:8080` in your web browser to generate and view cards!

### 3. Docker Compose Orchestration
Run locally inside full isolation:
```bash
docker-compose up --build
```
Access the application on `http://localhost:3000`.

---

## 🌐 Cloud Run Deployment

To deploy your consolidated single-service application to Google Cloud Run:

### 1. Optimize IAM Permissions (First-Time Setup)
Ensure your default Compute engine service account has the necessary permissions to build, log, and write artifacts inside your project:
```bash
# Enable required Google Cloud APIs
gcloud services enable serviceusage.googleapis.com \
                       run.googleapis.com \
                       artifactregistry.googleapis.com \
                       cloudbuild.googleapis.com \
                       --project YOUR_PROJECT_ID

# Grant Storage Object Viewer to both Build & Compute service accounts
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/storage.objectViewer

# Grant Logs Writer and Artifact Registry Writer to the Compute service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/logging.logWriter

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/artifactregistry.writer
```

### 2. Deploy directly from Source
Run the deploy command from your workspace root. Google Cloud Build will automatically build, push, and deploy your containerized FastAPI service:
```bash
gcloud run deploy github-dev-card \
    --source backend \
    --project YOUR_PROJECT_ID \
    --region us-central1 \
    --allow-unauthenticated
```
Once deployed, Cloud Run will output your live, fully functional, full-stack application URL!

---

## 📜 License
This project is licensed under the MIT License. Feel free to clone, build, and share your developer identity cards!
