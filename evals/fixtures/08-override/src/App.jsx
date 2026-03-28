import React, { useState } from "react";
import ErrorBanner from "./ErrorBanner";

export default function App() {
  const [showError, setShowError] = useState(false);

  const handleAction = () => {
    // Simulate an action that might fail
    setShowError(true);
  };

  const handleDismiss = () => {
    setShowError(false);
  };

  return (
    <div className="app">
      <h1>Notification App</h1>
      <button onClick={handleAction}>Perform Action</button>
      {showError && <ErrorBanner onDismiss={handleDismiss} />}
    </div>
  );
}
