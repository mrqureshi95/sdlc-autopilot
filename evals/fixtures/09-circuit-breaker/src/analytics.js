const { sortByRevenue, getLastSortOrder } = require("./dataProcessor");

/**
 * Analytics module that computes rank-based metrics.
 *
 * COUPLING: Like reportGenerator, this module relies on sortByRevenue()
 * mutating the passed-in array. It reads from the original array after
 * sorting, expecting it to be in sorted order.
 */

function computeRankings(salesData) {
  sortByRevenue(salesData);

  // Relies on salesData being mutated in place by sortByRevenue
  return salesData.map((item, index) => ({
    rank: index + 1,
    id: item.id,
    name: item.name,
    revenue: item.revenue,
  }));
}

function getTopPerformerIds(salesData, count) {
  sortByRevenue(salesData);

  // Reads the sort order side effect
  const order = getLastSortOrder();
  return order ? order.slice(0, count) : [];
}

module.exports = { computeRankings, getTopPerformerIds };
