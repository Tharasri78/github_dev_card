<div align="center">

# GitHub Dev Card Generator

Generate personalized developer cards from public GitHub profiles using AI.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

</div>

---

## 📌 Overview

GitHub Dev Card Generator is a web application that creates personalized developer cards using public GitHub profile data. The application analyzes repositories, programming languages, and profile information to generate an AI-powered developer summary and unique developer card.

---

## ✨ Features

- GitHub Profile Analysis
- AI-Generated Developer Summary
- Developer Theme Classification
- Dynamic Developer Card Generation
- GitHub API Integration
- Responsive User Interface
- Docker Support

---

## 🛠️ Tech Stack

### Backend
- FastAPI
- Python
- Google Gemini API

### Frontend
- HTML
- CSS
- JavaScript

### Deployment
- Docker
- Google Cloud Run

---

## ⚙️ How It Works

1. Enter a GitHub username.
2. Fetch profile and repository information.
3. Analyze technologies and activity.
4. Generate an AI-powered summary.
5. Create a personalized developer card.

---

## 📂 Project Structure

```text
github-dev-card/
├── backend/
├── frontend/
├── static/
├── Dockerfile
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/your-username/github-dev-card.git
cd github-dev-card
```

### Configure Environment Variables

```env
GEMINI_API_KEY=your_api_key
GITHUB_TOKEN=your_github_token
```

### Run Application

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```text
http://localhost:8080
```

---

## 🔮 Future Enhancements

- Additional Developer Themes
- PDF Export
- Social Sharing
- Advanced GitHub Analytics

---

## 👨‍💻 Author

**Thara Sri**

GitHub: https://github.com/Tharasri78

---

## 📄 License

This project is licensed under the MIT License.
