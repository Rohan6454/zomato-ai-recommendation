"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

type Recommendation = {
  restaurant_name: string;
  cuisines: string[];
  rating: number | null;
  estimated_cost_for_two: number | null;
  location_city: string;
  explanation: string;
  rank: number;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function ResultsPage() {
  const PAGE_SIZE = 20;
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [results, setResults] = useState<Recommendation[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  const payload = useMemo(() => {
    const location_city = searchParams.get("location_city") || "Banashankari";
    const max_budget = searchParams.get("max_budget");
    const min_rating = searchParams.get("min_rating");
    const cuisinesParam = searchParams.get("cuisines");
    const cuisines = cuisinesParam
      ? cuisinesParam
          .split(",")
          .map((x) => x.trim())
          .filter(Boolean)
      : [];

    return {
      location_city,
      max_budget: max_budget ? Number(max_budget) : undefined,
      min_rating: min_rating ? Number(min_rating) : 4,
      cuisines
    };
  }, [searchParams]);

  useEffect(() => {
    setCurrentPage(1);
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const resp = await fetch(`${API_BASE}/recommendations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!resp.ok) {
          throw new Error(`Backend returned ${resp.status}`);
        }

        const data = (await resp.json()) as Recommendation[];
        setResults(data);
      } catch (e) {
        setResults([]);
        setError(e instanceof Error ? e.message : "Failed to fetch recommendations");
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [payload]);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(results.length / PAGE_SIZE)), [results.length, PAGE_SIZE]);
  const clampedPage = Math.min(currentPage, totalPages);
  const pageStart = (clampedPage - 1) * PAGE_SIZE;
  const pageEnd = pageStart + PAGE_SIZE;
  const pageResults = useMemo(() => results.slice(pageStart, pageEnd), [results, pageStart, pageEnd]);

  return (
    <main className="page">
      <section className="hero">
        <span className="badge">Your Curated Feed</span>
        <h1>
          Recommended <em>restaurants</em>
        </h1>
        <p>
          Showing picks for <strong>{payload.location_city}</strong>
          {payload.max_budget ? ` under ${payload.max_budget} for two` : ""}.
        </p>
      </section>

      <section className="results-shell">
        <div className="results-topbar">
          <Link href={`/?${searchParams.toString()}`} className="secondary-btn">
            ← Update preferences
          </Link>
          <span className="result-count">
            {loading ? "Loading..." : `Showing ${results.length === 0 ? 0 : pageStart + 1}-${Math.min(pageEnd, results.length)} of ${results.length}`}
          </span>
        </div>

        {error ? <div className="error">{error}</div> : null}

        {!loading && !error && results.length === 0 ? (
          <div className="empty-state">
            <h3>No restaurants found</h3>
            <p>Try reducing minimum rating, increasing budget, or selecting fewer cuisines.</p>
          </div>
        ) : null}

        <div className="results-grid">
          {pageResults.map((r) => (
            <article key={`${r.restaurant_name}-${r.rank}`} className="result-card rich">
              <div className="rank-pill">#{r.rank}</div>
              <h3>{r.restaurant_name}</h3>
              <div className="meta">
                <span>Rating: {r.rating ?? "N/A"}</span>
                <span>Cost for two: {r.estimated_cost_for_two ?? "Not listed"}</span>
              </div>
              <div className="chips">
                {r.cuisines.slice(0, 4).map((c) => (
                  <span key={c} className="chip">
                    {c}
                  </span>
                ))}
              </div>
              <p className="why">{r.explanation}</p>
            </article>
          ))}
        </div>

        {!loading && !error && results.length > PAGE_SIZE ? (
          <div className="pagination">
            <button
              type="button"
              className="secondary-btn"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={clampedPage <= 1}
            >
              Previous
            </button>
            <span className="pagination-info">
              Page {clampedPage} of {totalPages}
            </span>
            <button
              type="button"
              className="secondary-btn"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={clampedPage >= totalPages}
            >
              Next
            </button>
          </div>
        ) : null}
      </section>
    </main>
  );
}

