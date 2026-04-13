## Phase 1 – Requirements & High-Level Architecture

### 1. Goals
- **Clarify functional scope**
  - Collect user preferences: location, budget, cuisine, minimum rating, extra constraints (e.g., family-friendly, quick service).
  - Use the Zomato dataset to find relevant restaurants.
  - Use an LLM to refine, rank, and explain recommendations.
  - Present clear and useful recommendations in a UI.

- **Clarify non-functional needs**
  - **Latency**: Reasonable response time (e.g., < 3–5 seconds for typical queries).
  - **LLM cost control**: Minimize tokens by limiting candidate list size and using concise prompts.
  - **Scalability (later)**: Design with potential future scaling in mind but keep the initial implementation simple.
  - **Observability**: Basic logging of requests, LLM latency, and errors.

### 2. Tech Stack Decisions (Initial Proposal)
- **Backend**
  - Language: Python.
  - Framework: FastAPI (for quick, typed, documented APIs).
  - Reason: Good ecosystem for data processing and ML/LLM integration.

- **Frontend**
  - Framework: Next.js (React + TypeScript).
  - Reason: Better long-term frontend foundation with routing, SSR support, and production build tooling.

- **Data & Storage**
  - Initial prototype: In-memory structures loaded at startup from the Zomato dataset.
  - Next step: SQLite/Postgres for persistence and easier querying.

- **LLM**
  - Provider: OpenAI/Azure/Open-source via API (to be decided based on availability).
  - Integration: A thin client library that abstracts provider-specific details.

### 3. Core System Components
- **Data Service**
  - Responsible for loading, cleaning, and indexing the Zomato dataset.
  - Provides query APIs to fetch candidate restaurants based on structured filters.

- **Recommendation Service**
  - Coordinates filtering, scoring, and LLM-based ranking.
  - Handles prompt construction, LLM calls, and response parsing.

- **API Layer**
  - Exposes REST endpoints (e.g., `POST /recommendations`).
  - Validates user input and orchestrates calls to the recommendation service.

- **UI Layer**
  - Web-based interface for users to input preferences and view recommendations.
  - Calls the backend API and renders results in a user-friendly format.

### 4. High-Level Request Flow
1. **User** fills out preferences in the UI and submits the form.
2. **Frontend** sends a `POST /recommendations` request to the backend with the preferences.
3. **API Layer** validates and normalizes the preferences.
4. **Data Service** retrieves a set of candidate restaurants using structured filters (location, budget, cuisine, rating).
5. **Recommendation Service**:
   - Builds a prompt that includes user preferences and candidate summaries.
   - Calls the LLM to rank and explain top restaurants.
   - Parses the LLM response into a structured format.
6. **API Layer** returns the final ranked recommendations with explanations to the frontend.
7. **Frontend** displays the results to the user in a friendly layout.

### 5. Diagrams to Create (Optional but Recommended)
- **Component Diagram**
  - Shows `UI`, `API`, `Data Service`, `Recommendation Service`, `LLM Provider`, and `Data Store`.

- **Sequence Diagram**
  - Shows the lifecycle of a recommendation request:
    - User → UI → API → Data Service → Recommendation Service → LLM → Recommendation Service → API → UI.

