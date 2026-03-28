const express = require("express");
const app = express();

app.use(express.json());

// POST /api/transform — transforms input text to uppercase
// BUG: crashes with 500 when body is empty or missing 'text' field
app.post("/api/transform", (req, res) => {
  const result = req.body.text.toUpperCase();
  res.json({ result });
});

// GET /api/health
app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});

module.exports = app;
