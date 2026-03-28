// BUG: Import path is wrong — should be "@monorepo/shared" but uses a broken relative path
const { formatCurrency, formatDate } = require("../../shared/src/indx");

function renderSummary(data) {
  return {
    title: data.title,
    total: formatCurrency(data.total),
    date: formatDate(data.date),
    items: data.items.length,
  };
}

function renderDashboard(records) {
  return records.map((record) => renderSummary(record));
}

module.exports = { renderSummary, renderDashboard };
