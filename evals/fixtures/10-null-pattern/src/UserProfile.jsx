import React from "react";

/**
 * Displays user profile information.
 *
 * BUG (REPORTED): Crashes with "Cannot read properties of null (reading 'city')"
 * when `user.address` is null. The API returns address: null for users who
 * haven't set their address yet.
 */
export default function UserProfile({ user }) {
  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <div className="address">
        <h3>Address</h3>
        <p>{user.address.street}</p>
        <p>{user.address.city}, {user.address.state} {user.address.zip}</p>
      </div>
      <p>Member since: {user.joinDate}</p>
    </div>
  );
}
