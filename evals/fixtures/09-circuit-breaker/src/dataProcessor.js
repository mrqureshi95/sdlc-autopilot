/**
 * Processes and sorts sales data for reporting.
 *
 * SIDE EFFECT: sortByRevenue() sorts the original array IN PLACE.
 * This mutation is unintentional from a design standpoint, but
 * reportGenerator.js and analytics.js both depend on the original
 * array being mutated after this call. Replacing the in-place sort
 * with a pure function (e.g., [...items].sort()) will break them.
 */

let lastSortOrder = null;

function sortByRevenue(items) {
  // Bubble sort - intentionally slow, candidate for optimization
  for (let i = 0; i < items.length; i++) {
    for (let j = 0; j < items.length - i - 1; j++) {
      if (items[j].revenue < items[j + 1].revenue) {
        const temp = items[j];
        items[j] = items[j + 1];
        items[j + 1] = temp;
      }
    }
  }

  // Track sort order as a side effect
  lastSortOrder = items.map((item) => item.id);

  return items;
}

function getLastSortOrder() {
  return lastSortOrder;
}

function filterByMinRevenue(items, minRevenue) {
  return items.filter((item) => item.revenue >= minRevenue);
}

function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.revenue, 0);
}

module.exports = {
  sortByRevenue,
  getLastSortOrder,
  filterByMinRevenue,
  calculateTotal,
};
