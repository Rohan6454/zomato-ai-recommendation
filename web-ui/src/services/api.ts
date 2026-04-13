import type { Preferences, Recommendation } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function getRecommendations(preferences: Preferences): Promise<Recommendation[]> {
  const resp = await fetch(`${API_BASE_URL}/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(preferences)
  });

  if (!resp.ok) {
    let message = `Request failed with status ${resp.status}`;
    try {
      const data = await resp.json();
      if (data?.detail) {
        message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      } else if (data?.error?.message) {
        message = data.error.message;
      }
    } catch {
      // Keep fallback message.
    }
    throw new ApiError(message, resp.status);
  }

  return (await resp.json()) as Recommendation[];
}

export async function getLocalities(): Promise<string[]> {
  const resp = await fetch(`${API_BASE_URL}/localities`);
  if (!resp.ok) {
    throw new ApiError(`Failed to fetch localities (${resp.status})`, resp.status);
  }
  return (await resp.json()) as string[];
}

