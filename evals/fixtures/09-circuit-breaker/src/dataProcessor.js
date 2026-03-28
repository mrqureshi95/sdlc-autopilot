/**
 * Processes and sorts sales data for reporting.
 */

let lastSortOrder = null;

function sortByRevenue(items) {
  for (let i = 0; i < items.length; i++) {
    for (let j = 0; j < items.length - i - 1; j++) {
      if (items[j].revenue < items[j + 1].revenue) {
        const temp = items[j];
        items[j] = items[j + 1];
        items[j + 1] = temp;
      }
    }
  }

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
