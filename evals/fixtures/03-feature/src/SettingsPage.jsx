import React, { useState } from "react";
import "./SettingsPage.css";

function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [language, setLanguage] = useState("en");

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <div className="settings-section">
        <h2>Notifications</h2>
        <label className="setting-row">
          <span>Enable notifications</span>
          <input
            type="checkbox"
            checked={notifications}
            onChange={(e) => setNotifications(e.target.checked)}
          />
        </label>
      </div>

      <div className="settings-section">
        <h2>Language</h2>
        <label className="setting-row">
          <span>Display language</span>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
          </select>
        </label>
      </div>

      {/* Dark mode toggle is not yet implemented */}
    </div>
  );
}

export default SettingsPage;
