import type { Recommendation } from "../types";

interface RecommendationCardProps {
  item: Recommendation;
}

function renderStars(rating: number | null): string {
  if (rating === null) return "N/A";
  const rounded = Math.round(rating);
  return `${"★".repeat(rounded)}${"☆".repeat(5 - rounded)}`;
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  return (
    <article className="card">
      <div className="card-head">
        <h3>
          #{item.rank} {item.restaurant_name}
        </h3>
        <span className="rating-badge">{item.rating?.toFixed(1) ?? "N/A"}</span>
      </div>
      <p className="muted">{renderStars(item.rating)}</p>
      <p>
        <strong>Cuisines:</strong> {item.cuisines.join(", ") || "N/A"}
      </p>
      <p>
        <strong>Cost for two:</strong>{" "}
        {item.estimated_cost_for_two !== null ? `INR ${item.estimated_cost_for_two}` : "Not listed"}
      </p>
      <p>
        <strong>Location:</strong> {item.location_city}
        {item.location_area ? `, ${item.location_area}` : ""}
      </p>
      <p>
        <strong>Why this match:</strong> {item.explanation}
      </p>
    </article>
  );
}

