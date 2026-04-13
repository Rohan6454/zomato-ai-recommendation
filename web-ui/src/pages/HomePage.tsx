import { useEffect, useState } from "react";
import { ErrorBanner } from "../components/ErrorBanner";
import { LoadingState } from "../components/LoadingState";
import { PreferenceForm } from "../components/PreferenceForm";
import { RecommendationList } from "../components/RecommendationList";
import { getLocalities, getRecommendations } from "../services/api";
import type { Preferences, Recommendation } from "../types";

export function HomePage() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [localities, setLocalities] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getLocalities()
      .then((vals) => setLocalities(vals))
      .catch((e) => {
        const message = e instanceof Error ? e.message : "Failed to load localities.";
        setError(message);
      });
  }, []);

  const handleSubmit = async (prefs: Preferences) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getRecommendations(prefs);
      setItems(response);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Failed to fetch recommendations.";
      setError(message);
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="layout">
      <PreferenceForm isSubmitting={isLoading} localities={localities} onSubmit={handleSubmit} />
      <section className="panel">
        <h2>Recommendations</h2>
        {error ? <ErrorBanner message={error} /> : null}
        {isLoading ? <LoadingState /> : <RecommendationList items={items} />}
      </section>
    </main>
  );
}

