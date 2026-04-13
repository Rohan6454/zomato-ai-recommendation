"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function Page() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [localities, setLocalities] = useState<string[]>([]);
  const [availableCuisines, setAvailableCuisines] = useState<string[]>([]);
  const [selectedLocality, setSelectedLocality] = useState("");
  const [maxBudget, setMaxBudget] = useState<string>("");
  const [budgetTouched, setBudgetTouched] = useState(false);
  const [budgetHint, setBudgetHint] = useState("");
  const [minRating, setMinRating] = useState<number>(4.0);
  const [cuisineInput, setCuisineInput] = useState("");
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    fetch(`${API_BASE}/localities`)
      .then((r) => r.json())
      .then((vals: string[]) => {
        setLocalities(vals);
      })
      .catch(() => setError("Failed to load localities. Please ensure backend is running."));
  }, [API_BASE]);

  useEffect(() => {
    const qs = selectedLocality ? `?location_city=${encodeURIComponent(selectedLocality)}` : "";
    fetch(`${API_BASE}/cuisines${qs}`)
      .then((r) => r.json())
      .then((vals: string[]) => {
        setAvailableCuisines(vals);
      })
      .catch(() => setError("Failed to load cuisines. Please ensure backend is running."));
  }, [API_BASE, selectedLocality]);

  useEffect(() => {
    const locationQ = (searchParams.get("location_city") || "").trim();
    const maxBudgetQ = (searchParams.get("max_budget") || "").trim();
    const minRatingQ = Number(searchParams.get("min_rating"));
    const cuisinesQ = (searchParams.get("cuisines") || "")
      .split(",")
      .map((x) => x.trim())
      .filter(Boolean);

    if (locationQ) setSelectedLocality(locationQ);
    if (maxBudgetQ) setMaxBudget(maxBudgetQ);
    if (!Number.isNaN(minRatingQ) && minRatingQ >= 0 && minRatingQ <= 5) setMinRating(minRatingQ);
    if (cuisinesQ.length > 0) {
      setSelectedCuisines(cuisinesQ);
      setCuisineInput(cuisinesQ[cuisinesQ.length - 1]);
    }
  }, [searchParams]);

  useEffect(() => {
    if (localities.length > 0 && selectedLocality && !localities.includes(selectedLocality)) {
      setSelectedLocality("");
    }
  }, [localities, selectedLocality]);

  useEffect(() => {
    if (availableCuisines.length > 0) {
      setSelectedCuisines((prev) => prev.filter((c) => availableCuisines.includes(c)));
    }
  }, [availableCuisines]);

  useEffect(() => {
    if (!selectedLocality) {
      setBudgetHint("");
      return;
    }
    const cuisinesParam = selectedCuisines.join(",");
    const qs = new URLSearchParams({ location_city: selectedLocality });
    if (cuisinesParam) qs.set("cuisines", cuisinesParam);
    qs.set("min_rating", String(minRating));
    if (maxBudget) qs.set("max_budget", maxBudget);
    fetch(`${API_BASE}/budget-suggestion?${qs.toString()}`)
      .then((r) => r.json())
      .then((data: { suggested_max_budget: number | null; sample_size: number; eligible_unique_count?: number }) => {
        if (data.suggested_max_budget) {
          const eligible = data.eligible_unique_count ?? 0;
          setBudgetHint(`Budget estimate uses ${data.sample_size} priced records; ${eligible} unique restaurants match your filters.`);
          if (!budgetTouched) setMaxBudget(String(data.suggested_max_budget));
        } else {
          setBudgetHint("No budget estimate available for current filters.");
          if (!budgetTouched) setMaxBudget("");
        }
      })
      .catch(() => {
        setBudgetHint("");
      });
  }, [API_BASE, selectedLocality, selectedCuisines, minRating, maxBudget, budgetTouched]);

  const canSubmit = useMemo(() => selectedLocality.length > 0 && !loading, [selectedLocality, loading]);
  const cuisineSuggestions = useMemo(() => {
    const q = cuisineInput.trim().toLowerCase();
    const base = q
      ? availableCuisines.filter((c) => c.toLowerCase().includes(q))
      : availableCuisines.slice(0, 12);
    return base.filter((c) => !selectedCuisines.includes(c)).slice(0, 8);
  }, [availableCuisines, cuisineInput, selectedCuisines]);

  const addCuisine = (value: string) => {
    if (!value.trim()) return;
    if (selectedCuisines.includes(value)) return;
    setSelectedCuisines((prev) => [...prev, value]);
    setCuisineInput("");
  };

  const removeCuisine = (value: string) => {
    setSelectedCuisines((prev) => prev.filter((c) => c !== value));
  };

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({
        location_city: selectedLocality,
        min_rating: String(minRating)
      });
      if (maxBudget) {
        params.set("max_budget", maxBudget);
      }
      if (selectedCuisines.length > 0) {
        params.set("cuisines", selectedCuisines.join(","));
      }
      router.push(`/results?${params.toString()}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="hero">
        <span className="badge">Welcome to Zomato&apos;s AI recommendation platform.</span>
        <h1>
          What are you <em>craving</em> today?
        </h1>
        <p>Curate your personal gastronomic feed to find your perfect table.</p>
      </section>

      <section className="builder">
        <div className="card location-card">
          <h3>Where do you wanna go today?</h3>
          <div className="field">
            <label>Locality</label>
            <select value={selectedLocality} onChange={(e) => setSelectedLocality(e.target.value)}>
              <option value="">Select a locality</option>
              {localities.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mini">
          <div className="card">
            <div className="section-title">Budget</div>
            <div className="field">
              <label>Max cost for two</label>
              <input
                value={maxBudget}
                onChange={(e) => {
                  setBudgetTouched(true);
                  setMaxBudget(e.target.value);
                }}
                type="number"
                min={0}
                step={50}
                placeholder="Enter max budget"
              />
              {budgetHint ? <small className="hint">{budgetHint}</small> : null}
            </div>
          </div>

          <div className="card">
            <div className="section-title">Minimum rating</div>
            <div className="field">
              <label>{minRating.toFixed(1)} stars</label>
              <input
                type="range"
                min={0}
                max={5}
                step={0.5}
                value={minRating}
                onChange={(e) => setMinRating(Number(e.target.value))}
              />
            </div>
          </div>
        </div>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <div className="section-title">Culinary focus</div>
        <div className="field">
          <label>Type cuisine name</label>
          <input
            type="text"
            value={cuisineInput}
            onChange={(e) => setCuisineInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key !== "Enter") return;
              e.preventDefault();
              const exact = availableCuisines.find((c) => c.toLowerCase() === cuisineInput.trim().toLowerCase());
              if (exact) {
                addCuisine(exact);
                return;
              }
              if (cuisineSuggestions.length > 0) addCuisine(cuisineSuggestions[0]);
            }}
            placeholder={selectedLocality ? "Type to see matching cuisines" : "Select locality first for targeted suggestions"}
            disabled={!selectedLocality}
          />
          <button
            type="button"
            className="secondary-btn inline"
            onClick={() => {
              const exact = availableCuisines.find((c) => c.toLowerCase() === cuisineInput.trim().toLowerCase());
              if (exact) addCuisine(exact);
              else if (cuisineSuggestions.length > 0) addCuisine(cuisineSuggestions[0]);
            }}
            disabled={!selectedLocality || (!cuisineInput.trim() && cuisineSuggestions.length === 0)}
          >
            Add cuisine
          </button>
          <div className="chips">
            {selectedCuisines.map((c) => (
              <button key={c} type="button" className="chip active" onClick={() => removeCuisine(c)}>
                {c} x
              </button>
            ))}
          </div>
          {selectedLocality && cuisineSuggestions.length > 0 ? (
            <div className="suggestions">
              {cuisineSuggestions.map((c) => (
                <button key={c} type="button" className="suggestion-item" onClick={() => addCuisine(c)}>
                  {c}
                </button>
              ))}
            </div>
          ) : null}
          <small className="hint">Suggestions are based on the selected locality. Click a selected cuisine chip to remove it.</small>
        </div>
      </section>

      <div className="actions">
        <button className="button" disabled={!canSubmit} onClick={submit}>
          {loading ? "Loading..." : "Start Exploring ->"}
        </button>
      </div>

      {error ? <div className="error">{error}</div> : null}
    </main>
  );
}

