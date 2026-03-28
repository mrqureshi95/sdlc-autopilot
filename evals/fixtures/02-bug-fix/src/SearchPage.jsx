import React, { useState } from "react";
import "./SearchPage.css";

function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = (e) => {
    e.preventDefault();
    // Simulate search results
    setResults([
      { id: 1, title: `Result for "${query}" - Item 1` },
      { id: 2, title: `Result for "${query}" - Item 2` },
      { id: 3, title: `Result for "${query}" - Item 3` },
    ]);
  };

  return (
    <div className="search-page">
      <h1 className="search-title">Search</h1>
      <div className="search-results">
        {results.map((item) => (
          <div key={item.id} className="result-item">
            {item.title}
          </div>
        ))}
      </div>
      {/* BUG: Search bar is positioned absolute at the bottom of the viewport.
           On mobile, when the virtual keyboard opens it covers this input
           because bottom:0 refers to the full viewport, not the visible area. */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          className="search-input"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Go</button>
      </form>
    </div>
  );
}

export default SearchPage;
