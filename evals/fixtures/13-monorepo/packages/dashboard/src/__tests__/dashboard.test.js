const { renderSummary } = require("../src/dashboard");

jest.mock("../../shared/src/indx", () => ({
  formatCurrency: (v) => "$" + v.toFixed(2),
  formatDate: (d) => new Date(d).toLocaleDateString(),
}));

describe("dashboard", () => {
  test("renderSummary formats record", () => {
    const data = {
      title: "Q1 Report",
      total: 1500.5,
      date: "2026-01-15",
      items: [1, 2, 3],
    };
    const result = renderSummary(data);
    expect(result.title).toBe("Q1 Report");
    expect(result.items).toBe(3);
  });
});
