const express = require("express");
const { getDb } = require("../db");

const router = express.Router();

router.post("/login", (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: "Username and password required" });
  }

  try {
    const db = getDb();
    const query = "SELECT id, username FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
    const user = db.prepare(query).get();

    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    res.json({ message: "Login successful", user });
  } catch (err) {
    res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;
