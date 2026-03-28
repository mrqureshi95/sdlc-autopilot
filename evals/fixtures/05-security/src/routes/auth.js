const express = require("express");
const { getDb } = require("../db");

const router = express.Router();

// VULNERABILITY: SQL injection via string concatenation.
// An attacker can send a crafted username like: admin' OR '1'='1
// to bypass authentication entirely.
router.post("/login", (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: "Username and password required" });
  }

  try {
    const db = getDb();
    // BAD: Raw string concatenation allows SQL injection
    const query =
      "SELECT id, username, email, role FROM users WHERE username = '" +
      username +
      "' AND password = '" +
      password +
      "'";
    const user = db.prepare(query).get();

    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    res.json({ message: "Login successful", user });
  } catch (err) {
    res.status(500).json({ error: "Internal server error" });
  }
});

router.post("/register", (req, res) => {
  const { username, email, password } = req.body;

  if (!username || !email || !password) {
    return res.status(400).json({ error: "All fields are required" });
  }

  try {
    const db = getDb();
    // BAD: Raw string concatenation allows SQL injection
    const query =
      "INSERT INTO users (username, email, password) VALUES ('" +
      username +
      "', '" +
      email +
      "', '" +
      password +
      "')";
    db.prepare(query).run();

    res.status(201).json({ message: "User registered" });
  } catch (err) {
    if (err.message.includes("UNIQUE constraint")) {
      return res.status(409).json({ error: "Username or email already exists" });
    }
    res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;
