import type { Recommendation } from "../types";
import { EmptyState } from "./EmptyState";
import { RecommendationCard } from "./RecommendationCard";

interface RecommendationListProps {
  items: Recommendation[];
}

export function RecommendationList({ items }: RecommendationListProps) {
  if (!items.length) {
    return <EmptyState />;
  }

  return (
    <section className="list">
      {items.map((item) => (
        <RecommendationCard key={`${item.restaurant_name}-${item.rank}`} item={item} />
      ))}
    </section>
  );
}

