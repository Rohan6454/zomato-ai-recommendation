## Component Diagram – High-Level View (Phase 1)

This document provides a textual description of the high-level component diagram for the AI-powered restaurant recommendation system.

### Components

- **Web UI (Frontend)**
  - React single-page application.
  - Collects user preferences and displays recommendations.
  - Communicates with the backend API over HTTP (JSON).

- **API Layer (Backend)**
  - FastAPI application (`backend/app/main.py`).
  - Exposes REST endpoints (e.g., `POST /recommendations`, `GET /health`).
  - Validates and normalizes incoming requests.
  - Orchestrates calls to the Data Service and Recommendation Service.

- **Data Service**
  - Responsible for loading and cleaning the Zomato dataset.
  - Provides structured access to restaurant data (later phases).
  - Interacts with:
    - In-memory data structures (initially), or
    - Database / search engine (in later phases).

- **Recommendation Service**
  - Uses the Data Service to fetch candidate restaurants based on user preferences.
  - Applies filtering and heuristic ranking.
  - Constructs prompts and calls the LLM.
  - Parses LLM responses to produce final, ranked recommendations with explanations.

- **LLM Provider**
  - External service (e.g., OpenAI/Azure/open-source LLM API).
  - Receives structured prompts and returns ranked/explained recommendations in natural language (structured as JSON).

- **Data Store**
  - Initial: in-memory representations loaded from the Zomato dataset at startup.
  - Later: SQLite/Postgres or a search engine for more robust querying.

### High-Level Interactions

1. Web UI → API Layer: send user preferences.
2. API Layer → Data Service: request candidate restaurants.
3. API Layer → Recommendation Service: request ranked recommendations with explanations.
4. Recommendation Service → LLM Provider: send prompt with candidates and preferences.
5. Recommendation Service → API Layer: return structured recommendations.
6. API Layer → Web UI: send final recommendations to display.

