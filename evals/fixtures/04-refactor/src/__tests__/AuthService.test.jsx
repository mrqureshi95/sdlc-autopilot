import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import AuthService from "../AuthService";

function TestConsumer() {
  return (
    <AuthService>
      {({ user, loading, error, login, logout }) => (
        <div>
          {loading && <p>Loading...</p>}
          {error && <p>Error: {error}</p>}
          {user ? (
            <>
              <p>User: {user.name}</p>
              <button onClick={logout}>Logout</button>
            </>
          ) : (
            <button onClick={() => login("test@example.com", "password")}>
              Login
            </button>
          )}
        </div>
      )}
    </AuthService>
  );
}

describe("AuthService", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders children with initial state", () => {
    render(<TestConsumer />);
    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  it("logs in successfully with correct credentials", async () => {
    render(<TestConsumer />);
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() => {
      expect(screen.getByText("User: Test User")).toBeInTheDocument();
    });
  });

  it("logs out and clears user", async () => {
    render(<TestConsumer />);
    fireEvent.click(screen.getByText("Login"));
    await waitFor(() => {
      expect(screen.getByText("User: Test User")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Logout"));
    expect(screen.getByText("Login")).toBeInTheDocument();
  });
});
