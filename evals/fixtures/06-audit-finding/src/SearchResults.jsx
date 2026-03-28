import React, { useRef, useEffect } from "react";

/**
 * Displays search results by highlighting matching text.
 *
 * VULNERABILITY: Uses innerHTML to inject highlighted markup built from
 * user-controlled `query` — a reflected XSS attack vector.
 */
export default function SearchResults({ query, results }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const html = results
      .filter((r) => r.title.toLowerCase().includes(query.toLowerCase()))
      .map((r) => {
        const highlighted = r.title.replace(
          new RegExp(`(${query})`, "gi"),
          "<mark>$1</mark>"
        );
        return `<div class="result-item"><h3>${highlighted}</h3><p>${r.description}</p></div>`;
      })
      .join("");

    containerRef.current.innerHTML = html;
  }, [query, results]);

  return (
    <div className="search-results">
      <h2>Search Results</h2>
      <div ref={containerRef} />
    </div>
  );
}
