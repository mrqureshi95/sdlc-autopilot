function formatCurrency(value) {
  return "$" + Number(value).toFixed(2);
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("en-US");
}

function capitalize(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

module.exports = { formatCurrency, formatDate, capitalize };
