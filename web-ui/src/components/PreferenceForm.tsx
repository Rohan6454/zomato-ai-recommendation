import { useState, type FormEvent } from "react";
import type { Preferences } from "../types";

interface PreferenceFormProps {
  isSubmitting: boolean;
  localities: string[];
  onSubmit: (prefs: Preferences) => void;
}

const CUISINE_OPTIONS = ["Indian", "Italian", "Chinese", "South Indian", "North Indian", "Continental"];

export function PreferenceForm({ isSubmitting, localities, onSubmit }: PreferenceFormProps) {
  const [locationCity, setLocationCity] = useState("Banashankari");
  const [maxBudget, setMaxBudget] = useState("");
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [minRating, setMinRating] = useState(3.5);
  const [notes, setNotes] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const toggleValue = (value: string, arr: string[], setArr: (next: string[]) => void) => {
    setArr(arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value]);
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!locationCity.trim()) {
      setValidationError("Location city is required.");
      return;
    }
    setValidationError(null);
    onSubmit({
      location_city: locationCity.trim(),
      max_budget: maxBudget.trim() ? Number(maxBudget) : undefined,
      cuisines,
      min_rating: minRating,
      notes: notes.trim() || undefined
    });
  };

  return (
    <form className="panel" onSubmit={submit}>
      <h2>Preferences</h2>

      <label>
        Locality
        <select value={locationCity} onChange={(e) => setLocationCity(e.target.value)}>
          <option value="">Select locality</option>
          {localities.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
      </label>

      <label>
        Max budget (cost for two)
        <input
          value={maxBudget}
          onChange={(e) => setMaxBudget(e.target.value)}
          type="number"
          min={0}
          step={50}
          placeholder="1200"
        />
      </label>

      <fieldset>
        <legend>Cuisines</legend>
        <div className="checkbox-grid">
          {CUISINE_OPTIONS.map((c) => (
            <label key={c}>
              <input
                type="checkbox"
                checked={cuisines.includes(c)}
                onChange={() => toggleValue(c, cuisines, setCuisines)}
              />
              {c}
            </label>
          ))}
        </div>
      </fieldset>

      <label>
        Minimum rating: {minRating.toFixed(1)}
        <input
          type="range"
          min={0}
          max={5}
          step={0.5}
          value={minRating}
          onChange={(e) => setMinRating(Number(e.target.value))}
        />
      </label>

      <label>
        Additional notes
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any special preference?"
          rows={3}
        />
      </label>

      {validationError ? <p className="validation-error">{validationError}</p> : null}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Getting recommendations..." : "Get recommendations"}
      </button>
    </form>
  );
}

