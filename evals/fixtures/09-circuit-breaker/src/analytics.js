const { sortByRevenue, getLastSortOrder } = require("./dataProcessor");

/**
 * Analytics module that computes rank-based metrics.
 */

function computeRankings(salesData) {
  sortByRevenue(salesData);

  return salesData.map((item, index) => ({
    rank: index + 1,
    id: item.id,
    name: item.name,
    revenue: item.revenue,
  }));
}

function getTopPerformerIds(salesData, count) {
  sortByRevenue(salesData);

  const order = getLastSortOrder();
  return order ? order.slice(0, count) : [];
}

module.exports = { computeRankings, getTopPerformerIds };
