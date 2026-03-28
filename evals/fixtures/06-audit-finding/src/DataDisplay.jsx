import React from "react";

/**
 * Renders a summary of fetched data records.
 *
 * VULNERABILITY: Uses dangerouslySetInnerHTML with unsanitized server data.
 * If the API returns HTML/script tags in `record.description`, they will be
 * executed in the browser — a stored XSS attack vector.
 */
export default function DataDisplay({ data }) {
  if (!data || !data.items) {
    return <p>No data available.</p>;
  }

  return (
    <div className="data-display">
      <h2>Records ({data.items.length})</h2>
      <ul>
        {data.items.map((record) => (
          <li key={record.id}>
            <strong>{record.title}</strong>
            <div
              dangerouslySetInnerHTML={{ __html: record.description }}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}
