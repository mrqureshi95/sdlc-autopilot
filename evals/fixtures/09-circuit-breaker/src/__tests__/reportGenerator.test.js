const { generateReport, generateQuickSummary } = require("../reportGenerator");

describe("generateReport", () => {
  test("returns a report with sorted top performers", () => {
    const data = [
      { id: 1, name: "Widget A", revenue: 500 },
      { id: 2, name: "Widget B", revenue: 1200 },
      { id: 3, name: "Widget C", revenue: 800 },
    ];

    const report = generateReport(data);

    expect(report.title).toBe("Sales Report");
    expect(report.totalRevenue).toBe(2500);
    expect(report.topPerformers[0].name).toBe("Widget B");
    expect(report.topPerformers[1].name).toBe("Widget C");

    // This test implicitly relies on the mutation side effect:
    // after generateReport, `data` itself is sorted descending.
    expect(data[0].name).toBe("Widget B");
    expect(data[2].name).toBe("Widget A");
  });

  test("includes sorted IDs", () => {
    const data = [
      { id: 10, name: "X", revenue: 50 },
      { id: 20, name: "Y", revenue: 150 },
    ];

    const report = generateReport(data);
    expect(report.sortedIds).toEqual([20, 10]);
  });
});

describe("generateQuickSummary", () => {
  test("identifies best and worst performers", () => {
    const data = [
      { id: 1, name: "Low", revenue: 10 },
      { id: 2, name: "High", revenue: 999 },
      { id: 3, name: "Mid", revenue: 500 },
    ];

    const summary = generateQuickSummary(data);
    expect(summary.best).toBe("High");
    expect(summary.worst).toBe("Low");
    expect(summary.total).toBe(1509);
  });
});
