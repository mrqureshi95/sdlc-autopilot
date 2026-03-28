const express = require("express");
const { getDb } = require("../db");

const router = express.Router();

// VULNERABILITY: SQL injection via string concatenation in search query.
router.get("/search", (req, res) => {
  const { q } = req.query;

  if (!q) {
    return res.status(400).json({ error: "Search query required" });
  }

  try {
    const db = getDb();
    // BAD: Raw string concatenation allows SQL injection
    const query =
      "SELECT id, username, email, role FROM users WHERE username LIKE '%" +
      q +
      "%' OR email LIKE '%" +
      q +
      "%'";
    const users = db.prepare(query).all();

    res.json({ users });
  } catch (err) {
    res.status(500).json({ error: "Internal server error" });
  }
});

router.get("/:id", (req, res) => {
  const { id } = req.params;

  try {
    const db = getDb();
    // BAD: Raw string concatenation allows SQL injection
    const query =
      "SELECT id, username, email, role FROM users WHERE id = " + id;
    const user = db.prepare(query).get();

    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json({ user });
  } catch (err) {
    res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;
