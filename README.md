# CareerCompass AI

An AI-powered career mentor for engineering students — built as the final assessment
for the IBM Generative AI Internship.

> Status: **Phases 4–6 — Backend endpoints, LLM integration, and SQLite persistence.**
> Frontend pages exist as static UI (Phase 3) but are not yet wired to the API.
> See the PRD for full scope.

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** FastAPI (Python)
- **LLM:** Google Gemini API
- **Database:** SQLite
- **Deployment:** Docker + AWS EC2

## Project Structure
```
career-compass-ai/
├── frontend/           # Static HTML/CSS/JS UI
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/            # FastAPI application
│   ├── main.py         # App entrypoint + routes
│   ├── ai.py           # Gemini integration + prompt engineering
│   ├── database.py     # SQLAlchemy engine/session setup
│   ├── models.py       # ORM models + Pydantic schemas
│   └── requirements.txt
├── database/           # SQLite file lives here at runtime (gitignored)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Running Locally (Docker)
1. Copy `.env.example` to `.env` and add your real `GEMINI_API_KEY`.
2. From the project root:
   ```bash
   docker compose up --build
   ```
3. Backend health check: http://localhost:8000/health
4. Interactive API docs (Swagger): http://localhost:8000/docs
5. Frontend: http://localhost:3000

## API Endpoints
The app is currently single-profile (no login flow yet) — there's one profile
record that every endpoint reads from / writes to.

| Method | Path              | Purpose                                            |
|--------|-------------------|-----------------------------------------------------|
| GET    | `/health`         | Liveness check                                      |
| GET    | `/profile`        | Fetch the current student profile                   |
| POST   | `/profile`        | Create/update branch, semester, skills, interests, goal |
| POST   | `/career-guidance`| Ask a free-form career question (saved to history)  |
| GET    | `/history`        | List past questions & answers                       |
| POST   | `/roadmap`        | Generate a phased learning roadmap for a domain      |
| POST   | `/resume-review`  | Get strengths/improvements for pasted resume text    |
| POST   | `/skill-gap`      | Compare current skills against a target role         |

All AI-backed endpoints (`/career-guidance`, `/roadmap`, `/resume-review`,
`/skill-gap`) call Gemini via `ai.py` and will return a `503` until a real
`GEMINI_API_KEY` is set in `.env`.

## Development Roadmap
This project is being built in phases (see PRD Section 19):
1. ✅ Finalize PRD & project scaffolding
2. ✅ UI design
3. ✅ Frontend build (static pages)
4. ✅ FastAPI backend (real endpoints)
5. ✅ LLM integration (Google Gemini)
6. ✅ SQLite database
7. Wire frontend JS to the API (forms/chat currently static)
8. Testing
9. Dockerization refinement
10. AWS deployment
11. Documentation & final submission

## Author
Built as part of the IBM Generative AI Masterclass internship assessment.
