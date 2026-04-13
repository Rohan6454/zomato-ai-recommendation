## AI-Powered Restaurant Recommendation System (Zomato Use Case)

This project is an AI-powered restaurant recommendation service inspired by Zomato. It combines **structured restaurant data** with a **Large Language Model (LLM)** to provide personalized, human-like recommendations.

This repository is organized and implemented phase-wise. Phase 1 covers **requirements and high-level architecture** and sets the foundation for later phases.

---

### Phase 1 – Requirements & High-Level Architecture

**Functional scope**
- Collect user preferences:
  - Location (city, optionally area).
  - Budget (low / medium / high / any).
  - Cuisine(s).
  - Minimum rating.
  - Extra constraints (e.g., family-friendly, quick service).
- Use the Zomato dataset to find matching restaurants.
- Use an LLM to refine, rank, and explain recommendations.
- Present clear, helpful recommendations in a web UI.

**Non-functional needs**
- Reasonable latency (target \< 3–5 seconds for typical queries).
- Control LLM cost by:
  - Limiting candidate list size before calling the LLM.
  - Keeping prompts concise and structured.
- Design for future scalability but keep initial implementation simple.
- Basic observability: logging of requests, LLM latency, and errors.

**Tech stack (initial decisions)**
- Backend: **Python + FastAPI**.
- Frontend: **React** (single-page app).
- Data: In-memory structures from the Zomato dataset (later phases may add SQLite/Postgres).
- LLM: Provider-agnostic client (e.g., OpenAI/Azure or open-source LLM via API).

For more details, see `architecture/phase-1-high-level-architecture.md`.

---

### Repository Structure (Initial)

- `architecture/`
  - Phase-wise architecture documents, including Phase 1 high-level design.
- `phases/`
  - Phase-by-phase folder index and deliverables pointers.
- `backend/`
  - FastAPI application (skeleton created in Phase 1, to be expanded in later phases).
- `web-ui/`
  - Frontend React application (to be implemented in later phases).

---

### Getting Started (Phase 1)

At the end of Phase 1, only the **structure and core decisions** are in place. Implementation of data ingestion, recommendation logic, API endpoints, and UI will be done in subsequent phases.

To work on the backend locally (once later phases are implemented):
1. Create a virtual environment.
2. Install requirements from `backend/requirements.txt`.
3. Run the FastAPI app (e.g., with `uvicorn`).

Concrete implementation steps for later phases are documented under `architecture/`.

---

### Environment Variables (Gemini)

Create a `.env` file at the **repo root** (same level as this `README.md`) by copying:
- `.env.example` → `.env`

Then set:
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional)

The `.env` file is **ignored by git** via `.gitignore`.

