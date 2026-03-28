import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import SettingsPage from "../SettingsPage";

describe("SettingsPage", () => {
  it("renders the settings heading", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("renders notifications toggle", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Enable notifications")).toBeInTheDocument();
  });

  it("renders language selector with default English", () => {
    render(<SettingsPage />);
    const select = screen.getByDisplayValue("English");
    expect(select).toBeInTheDocument();
  });

  it("allows changing language", () => {
    render(<SettingsPage />);
    const select = screen.getByDisplayValue("English");
    fireEvent.change(select, { target: { value: "es" } });
    expect(screen.getByDisplayValue("Spanish")).toBeInTheDocument();
  });
});
