## Web UI – AI-Powered Restaurant Recommendation System

Phase 6 frontend implementation is built with **React + TypeScript + Vite**.

### Implemented features
- Preference form with:
  - Location city, optional area
  - Budget bucket
  - Cuisines (multi-select)
  - Minimum rating slider
  - Extras checkboxes
  - Optional notes
- API integration with backend `POST /recommendations`
- Recommendation cards list showing:
  - Name, cuisines, rating, cost, location, explanation
- UX states:
  - Loading
  - Error banner
  - Empty state

### Folder structure
- `src/components/`
  - `PreferenceForm.tsx`
  - `RecommendationList.tsx`
  - `RecommendationCard.tsx`
  - `LoadingState.tsx`
  - `EmptyState.tsx`
  - `ErrorBanner.tsx`
- `src/services/api.ts`
- `src/pages/HomePage.tsx`
- `src/App.tsx`
- `src/main.tsx`
- `src/styles.css`

### Run locally
From `web-ui/`:

1. Install dependencies:
   - `npm install`
2. Configure API URL:
   - copy `.env.example` to `.env`
   - update `VITE_API_URL` if needed (default is `http://127.0.0.1:8000`)
3. Start dev server:
   - `npm run dev`

### Backend dependency
Ensure backend is running before using the UI:
- from `backend/`: `uvicorn app.main:app --reload`

See `architecture/phase-6-frontend-ui.md` for phase-level design details.

