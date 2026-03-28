const { sortByRevenue, filterByMinRevenue, calculateTotal } = require("../dataProcessor");

describe("sortByRevenue", () => {
  test("sorts items by revenue in descending order", () => {
    const items = [
      { id: 1, name: "A", revenue: 100 },
      { id: 2, name: "B", revenue: 300 },
      { id: 3, name: "C", revenue: 200 },
    ];

    const result = sortByRevenue(items);

    expect(result[0].revenue).toBe(300);
    expect(result[1].revenue).toBe(200);
    expect(result[2].revenue).toBe(100);
  });

  test("handles empty array", () => {
    expect(sortByRevenue([])).toEqual([]);
  });

  test("handles single item", () => {
    const items = [{ id: 1, name: "A", revenue: 50 }];
    expect(sortByRevenue(items)).toEqual([{ id: 1, name: "A", revenue: 50 }]);
  });
});

describe("filterByMinRevenue", () => {
  test("filters items below threshold", () => {
    const items = [
      { id: 1, revenue: 100 },
      { id: 2, revenue: 50 },
      { id: 3, revenue: 200 },
    ];
    const result = filterByMinRevenue(items, 100);
    expect(result).toHaveLength(2);
  });
});

describe("calculateTotal", () => {
  test("sums all revenues", () => {
    const items = [{ revenue: 100 }, { revenue: 200 }, { revenue: 300 }];
    expect(calculateTotal(items)).toBe(600);
  });
});
