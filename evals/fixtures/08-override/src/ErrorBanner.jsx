import React from "react";
import "./ErrorBanner.css";

/**
 * Displays an error banner with a dismiss button.
 * The error message text below needs to be updated per product request.
 */
export default function ErrorBanner({ onDismiss }) {
  return (
    <div className="error-banner" role="alert">
      <span className="error-banner__icon" aria-hidden="true">!</span>
      <p className="error-banner__message">
        Something went wrong. Please try again later.
      </p>
      <button className="error-banner__dismiss" onClick={onDismiss} aria-label="Dismiss error">
        &times;
      </button>
    </div>
  );
}
