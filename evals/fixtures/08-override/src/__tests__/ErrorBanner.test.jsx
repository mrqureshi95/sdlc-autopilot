import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ErrorBanner from "../ErrorBanner";

test("renders the error message", () => {
  render(<ErrorBanner onDismiss={() => {}} />);
  expect(screen.getByRole("alert")).toBeTruthy();
  expect(screen.getByText(/something went wrong/i)).toBeTruthy();
});

test("calls onDismiss when dismiss button is clicked", () => {
  const mockDismiss = jest.fn();
  render(<ErrorBanner onDismiss={mockDismiss} />);
  fireEvent.click(screen.getByLabelText("Dismiss error"));
  expect(mockDismiss).toHaveBeenCalledTimes(1);
});
