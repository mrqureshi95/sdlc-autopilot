const express = require("express");

const app = express();
app.use(express.json());

app.get("/api/data", (req, res) => {
  res.json({ items: [{ id: 1, name: "Item A" }, { id: 2, name: "Item B" }] });
});

// BUG: Health check returns 201 instead of 200, which causes monitoring
// systems to report the service as unhealthy.
app.get("/health", (req, res) => {
  res.status(201).json({ status: "ok", uptime: process.uptime() });
});

const PORT = process.env.PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;
