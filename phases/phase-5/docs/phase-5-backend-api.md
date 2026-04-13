## Phase 5 – Backend API Layer

### 1. Goals
- Expose a clean, documented API for requesting restaurant recommendations.
- Handle validation, normalization, error handling, and orchestration.
- Serve as the contract between the frontend (or other clients) and the recommendation engine.

### 2. Framework & Structure
- **Framework**
  - Use FastAPI (Python) for rapid development and built-in OpenAPI documentation.

- **Suggested layout**
  - `api/main.py` – FastAPI app setup and route registration.
  - `api/routes/recommendations.py` – endpoints related to recommendations.
  - `api/models.py` – request/response Pydantic models.
  - `api/dependencies.py` – shared dependencies (e.g., data store, recommendation engine).

### 3. API Models
Define Pydantic models (or equivalent) to enforce input/output structure.

- **Request model** – `RecommendationRequest`
  - `location_city: str`
  - `location_area: Optional[str]`
  - `max_budget: Optional[float]` (maximum cost-for-two budget)
  - `cuisines: Optional[List[str]]`
  - `min_rating: Optional[float]`
  - `extras: Optional[List[str]]` (e.g., `["family_friendly", "quick_service"]`)
  - `notes: Optional[str]` (free-form preferences passed to the LLM as context)

- **Response model** – `RecommendationResponse`
  - `restaurant_name: str`
  - `cuisines: List[str]`
  - `rating: Optional[float]`
  - `estimated_cost_for_two: Optional[float]`
  - `location_city: str`
  - `location_area: Optional[str]`
  - `explanation: str`
  - (Optional) `rank: int`

### 4. Endpoints
- **`POST /recommendations`**
  - **Request body**: `RecommendationRequest`.
  - **Flow**:
    1. Validate and normalize the request payload.
    2. Map the request into the internal `UserPreferences` object.
    3. Call `recommendation_engine.recommend(preferences)`.
    4. Map internal `Recommendation` objects to `RecommendationResponse` models.
    5. Return the list of recommendations (e.g., top 5–10).

- **`GET /health`**
  - Returns basic health information:
    - Status: `ok`.
    - Optional: version, environment.

- **`GET /localities`**
  - Returns a sorted list of unique localities.
  - Used by the frontend locality dropdown to avoid free-text duplicates.

### 5. Validation & Normalization
- **Validation**
  - Ensure required fields like `location_city` are present.
  - Enforce non-negative values for `max_budget` (when provided).
  - Constrain `min_rating` between 0 and 5.

- **Normalization**
  - Trim whitespace, standardize case for locality and cuisine names.
  - Convert single cuisine string inputs (if allowed) into a list.

### 6. Error Handling
- **Types of errors**
  - Invalid request payload (400).
  - No candidates found for given preferences (200 with empty list or 404 with message).
  - LLM/service timeout or error (500).

- **Error response structure**
  - Consistent error schema, e.g.:
    - `{"error": {"code": "NO_RESULTS", "message": "No restaurants found for the given preferences"}}`

### 7. Cross-Cutting Concerns
- **Logging**
  - Log:
    - Request metadata (without sensitive free-form notes, or anonymized).
    - Number of candidates before/after filtering.
    - LLM call duration and status.
  - Avoid logging personally identifiable information.

- **Rate Limiting (Optional)**
  - Basic per-IP or per-API-key rate limiting for public endpoints.

- **CORS**
  - Configure CORS to allow requests from the frontend origin.

### 8. Documentation & Testing
- **Documentation**
  - Rely on FastAPI’s automatic docs (Swagger UI/OpenAPI).
  - Add endpoint descriptions and example payloads.

- **Testing**
  - Use test client (e.g., `TestClient` in FastAPI) to:
    - Test `POST /recommendations` with typical and edge-case inputs.
    - Mock the recommendation engine to isolate API testing.

### 9. Deliverables
- **Code**
  - Fully implemented API with `POST /recommendations` and `GET /health`.

- **Artifacts**
  - OpenAPI/Swagger documentation available at `/docs`.
  - Example request/response pairs for manual testing (e.g., in a `.http` file or Postman collection).

