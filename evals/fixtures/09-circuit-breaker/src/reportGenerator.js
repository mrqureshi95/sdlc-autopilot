const { sortByRevenue, getLastSortOrder, calculateTotal } = require("./dataProcessor");

/**
 * Generates a formatted sales report.
 *
 * COUPLING: This module passes its own `salesData` array to sortByRevenue()
 * and then continues to use that SAME array reference, relying on the fact
 * that sortByRevenue mutates it in place. If sortByRevenue is refactored to
 * return a new sorted array without mutating the original, the report will
 * contain unsorted data while the returned value (which nobody captures
 * here differently) would be lost.
 */

function generateReport(salesData) {
  // Sort the data — relies on in-place mutation of salesData
  sortByRevenue(salesData);

  // salesData is now sorted because sortByRevenue mutated it
  const topItems = salesData.slice(0, 5);
  const total = calculateTotal(salesData);
  const sortOrder = getLastSortOrder();

  return {
    title: "Sales Report",
    generatedAt: new Date().toISOString(),
    totalRevenue: total,
    topPerformers: topItems.map((item) => ({
      name: item.name,
      revenue: item.revenue,
    })),
    sortedIds: sortOrder,
    itemCount: salesData.length,
  };
}

function generateQuickSummary(salesData) {
  sortByRevenue(salesData);

  // Again relies on salesData being mutated: first item is now highest revenue
  return {
    best: salesData[0]?.name || "N/A",
    worst: salesData[salesData.length - 1]?.name || "N/A",
    total: calculateTotal(salesData),
  };
}

module.exports = { generateReport, generateQuickSummary };
