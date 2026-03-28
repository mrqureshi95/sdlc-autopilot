const { sortByRevenue, getLastSortOrder, calculateTotal } = require("./dataProcessor");

/**
 * Generates a formatted sales report.
 */

function generateReport(salesData) {
  sortByRevenue(salesData);

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

  return {
    best: salesData[0]?.name || "N/A",
    worst: salesData[salesData.length - 1]?.name || "N/A",
    total: calculateTotal(salesData),
  };
}

module.exports = { generateReport, generateQuickSummary };
