## Sequence Diagram – Recommendation Request Flow (Phase 1)

This document provides a textual description of the high-level sequence of interactions for a single recommendation request.

### Actors / Participants

- `User`
- `Web UI (Frontend)`
- `API Layer (FastAPI Backend)`
- `Data Service`
- `Recommendation Service`
- `LLM Provider`

### Sequence (Happy Path)

1. **User → Web UI**
   - User opens the application and fills out the preference form:
     - Location (city, optional area).
     - Budget.
     - Cuisine(s).
     - Minimum rating.
     - Extra constraints.
     - Optional notes.
   - User clicks "Get Recommendations".

2. **Web UI → API Layer**
   - Web UI sends an HTTP `POST /recommendations` request with the structured preferences.

3. **API Layer – Validation & Normalization**
   - API validates the request payload:
     - Ensures required fields (e.g., `location_city`) are present.
     - Ensures values like `budget_bucket` and `min_rating` are within allowed ranges.
   - API normalizes values (e.g., trimming whitespace, standardizing case).

4. **API Layer → Data Service**
   - API converts the request into an internal `UserPreferences` object.
   - API calls the Data Service to retrieve a set of candidate restaurants that match:
     - Location.
     - Budget.
     - Cuisine.
     - Minimum rating.

5. **Data Service → API Layer**
   - Data Service returns a list of candidate restaurants (structured data) to the API Layer.

6. **API Layer → Recommendation Service**
   - API forwards the `UserPreferences` and candidate restaurants to the Recommendation Service.

7. **Recommendation Service – Filtering & Prompting**
   - Applies any additional filtering and heuristic ranking (pre-LLM).
   - Builds a compact prompt summarizing:
     - User preferences.
     - Candidate restaurants (with key attributes).

8. **Recommendation Service → LLM Provider**
   - Sends the constructed prompt to the external LLM Provider.

9. **LLM Provider → Recommendation Service**
   - LLM returns a ranked list of recommended restaurants with short explanations, in a structured (JSON-like) format.

10. **Recommendation Service – Parsing & Structuring**
    - Parses the LLM response.
    - Maps results back to full restaurant objects.
    - Produces a final list of recommendations with:
      - Restaurant details.
      - Rank.
      - Explanation.

11. **Recommendation Service → API Layer**
    - Returns the final `Recommendation` list to the API Layer.

12. **API Layer → Web UI**
    - Serializes recommendations into the response schema.
    - Sends HTTP response back to the Web UI.

13. **Web UI → User**
    - Renders the recommendations:
      - Restaurant name, cuisine, rating, estimated cost.
      - AI-generated explanation.
    - User reviews the recommendations and may adjust preferences and repeat the flow.

