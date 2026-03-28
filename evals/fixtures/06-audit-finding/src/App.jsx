import React, { useState } from "react";
import { fetchData } from "./DataFetcher";
import DataDisplay from "./DataDisplay";
import SearchResults from "./SearchResults";

export default function App() {
  const [data, setData] = useState(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState(null);

  const handleLoad = async () => {
    try {
      setError(null);
      const result = await fetchData("/api/records");
      setData(result);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <h1>Data Dashboard</h1>
      <button onClick={handleLoad}>Load Data</button>
      {error && <p className="error">{error}</p>}
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search records..."
      />
      {data && <DataDisplay data={data} />}
      {query && <SearchResults query={query} results={data?.items || []} />}
    </div>
  );
}
