import React from "react";

/**
 * Displays a list of notifications.
 *
 * SAME PATTERN BUG: Crashes when `notification.sender` is null.
 * The API returns sender: null for system-generated notifications.
 */
export default function NotificationList({ notifications }) {
  return (
    <div className="notification-list">
      <h2>Notifications</h2>
      <ul>
        {notifications.map((notification) => (
          <li key={notification.id} className="notification-item">
            <strong>{notification.sender.name}</strong>
            <span className="avatar">{notification.sender.avatar}</span>
            <p>{notification.message}</p>
            <time>{notification.timestamp}</time>
          </li>
        ))}
      </ul>
    </div>
  );
}
