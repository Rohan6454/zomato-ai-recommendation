## Phase 6 – Frontend / UI Layer

### 1. Goals
- Provide a user-friendly interface for entering preferences and viewing recommendations.
- Communicate clearly what filters are applied and why certain restaurants are recommended.
- Offer responsive design for desktop and basic mobile usage.

### 2. Technology & Structure
- **Framework**
  - Next.js (React + TypeScript) for a production-ready frontend foundation.
  - Initial visual direction follows `design/Picture1.png`.

- **Suggested folder layout**
  - `web-ui-next/`
    - `app/`
      - `layout.tsx`
      - `page.tsx`
      - `globals.css`
    - `.env.local.example`
    - `package.json`
    - `tsconfig.json`

### 3. Preference Form UX
- **Fields**
  - `Locality` – dropdown populated by backend `GET /localities`.
  - `Location area` – optional text.
  - `Max budget` – numeric input for max cost-for-two preference.
  - `Cuisine` – multi-select (chips or checkbox list).
  - `Minimum rating` – slider (e.g., 0–5 with 0.5 steps).
  - `Extras` – checkboxes (e.g., `Family friendly`, `Quick service`).
  - `Additional notes` – optional extension field for future iterations.

- **Interactions**
  - Validate required fields (e.g., `Location city`).
  - Disable submit button while request is in-flight.
  - Provide clear error messages on invalid input.

### 4. API Client
- Implement in Next.js page/components via `fetch` wrappers:

  - `getLocalities(): Promise<string[]>`
    - Makes `GET /localities` to populate dropdown options.
    - Ensures user selects from known localities instead of free text.

  - `getRecommendations(preferences: Preferences): Promise<Recommendation[]>`
    - Makes `POST /recommendations` to the backend.
    - Handles:
      - Success: returns parsed recommendations.
      - Errors: throws a structured error for the UI to handle.

- **Configuration**
  - Base URL from environment (e.g., `NEXT_PUBLIC_API_BASE_URL`).

### 5. Results Presentation
- **`RecommendationList`**
  - Accepts an array of `Recommendation` objects.
  - Renders one `RecommendationCard` per restaurant.
  - Handles empty results by showing `EmptyState`.

- **`RecommendationCard` content**
  - Restaurant name (prominent).
  - Cuisine(s).
  - Rating (numeric + stars visual).
  - Estimated cost for two (formatted with currency symbol).
  - Location (city + area).
  - AI-generated explanation:
    - Short paragraph.
    - Key words highlighted (e.g., “budget-friendly”, “family-friendly”).

- **States**
  - Loading state when waiting on backend.
  - Error banner for failed requests.
  - Empty state if no recommendations are returned.

### 6. Visual & UX Considerations
- **Layout**
  - Two-column layout on desktop:
    - Left: Preferences form.
    - Right: Recommendations list.
  - Single-column stacked layout on smaller screens.

- **Styling**
  - Use a modern, clean design (e.g., Tailwind CSS or a component library).
  - Consistent colors for primary actions and tags.

- **Accessibility**
  - Proper labels for all form fields.
  - Keyboard-navigable controls.
  - Sufficient color contrast.

### 7. Testing & Observability
- **Frontend tests (optional but recommended)**
  - Component tests for `PreferenceForm` and `RecommendationList` with mocked API.
  - Basic integration test for the full page flow (submit → loading → results).

- **Logging**
  - Minimal client-side logging (e.g., errors) for debugging during development.

### 8. Deliverables
- **Code**
  - Next.js app with:
    - Fully functional preference form.
    - Recommendations display wired to backend.

- **Artifacts**
  - Screenshots or short screencast of the user flow.
  - Instructions in a top-level README on how to run the frontend and connect it to the backend.

