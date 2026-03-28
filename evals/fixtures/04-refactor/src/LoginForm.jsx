import React, { useState } from "react";
import AuthService from "./AuthService";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <AuthService>
      {({ user, loading, error, login, logout }) => {
        if (loading) return <p>Loading...</p>;

        if (user) {
          return (
            <div>
              <p>Welcome, {user.name}!</p>
              <button onClick={logout}>Logout</button>
            </div>
          );
        }

        const handleSubmit = async (e) => {
          e.preventDefault();
          try {
            await login(email, password);
          } catch {
            // error is displayed via AuthService state
          }
        };

        return (
          <form onSubmit={handleSubmit}>
            {error && <p className="error">{error}</p>}
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
          </form>
        );
      }}
    </AuthService>
  );
}

export default LoginForm;
