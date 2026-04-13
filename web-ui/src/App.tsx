import { HomePage } from "./pages/HomePage";

export default function App() {
  return (
    <>
      <header className="topbar">
        <h1>AI-Powered Restaurant Recommendations</h1>
        <p>Find places by location, budget, cuisine, and rating preferences.</p>
      </header>
      <HomePage />
    </>
  );
}

