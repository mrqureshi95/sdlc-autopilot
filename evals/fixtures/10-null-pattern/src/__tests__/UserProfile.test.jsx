import React from "react";
import { render, screen } from "@testing-library/react";
import UserProfile from "../UserProfile";

// NOTE: This test only covers the happy path where address is present.
// It does NOT test the case where address is null, which is the reported bug.

test("renders user profile with full data", () => {
  const user = {
    name: "Jane Doe",
    email: "jane@example.com",
    address: {
      street: "123 Main St",
      city: "Springfield",
      state: "IL",
      zip: "62701",
    },
    joinDate: "2023-01-15",
  };

  render(<UserProfile user={user} />);

  expect(screen.getByText("Jane Doe")).toBeTruthy();
  expect(screen.getByText("Email: jane@example.com")).toBeTruthy();
  expect(screen.getByText("123 Main St")).toBeTruthy();
  expect(screen.getByText(/Springfield/)).toBeTruthy();
});
