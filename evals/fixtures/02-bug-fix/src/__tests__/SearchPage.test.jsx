import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import SearchPage from "../SearchPage";

describe("SearchPage", () => {
  it("renders the search input and button", () => {
    render(<SearchPage />);
    expect(screen.getByPlaceholderText("Search...")).toBeInTheDocument();
    expect(screen.getByText("Go")).toBeInTheDocument();
  });

  it("displays results after submitting a search", () => {
    render(<SearchPage />);
    const input = screen.getByPlaceholderText("Search...");
    fireEvent.change(input, { target: { value: "hello" } });
    fireEvent.click(screen.getByText("Go"));
    expect(screen.getByText(/Result for "hello" - Item 1/)).toBeInTheDocument();
  });
});
