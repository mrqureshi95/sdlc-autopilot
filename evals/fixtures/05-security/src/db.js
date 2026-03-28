const Database = require("better-sqlite3");
const path = require("path");

let db;

function getDb() {
  if (!db) {
    db = new Database(path.join(__dirname, "..", "app.db"));
    db.pragma("journal_mode = WAL");
  }
  return db;
}

function initDb() {
  const conn = getDb();
  conn.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT DEFAULT 'user',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Seed a test user (password: "admin123")
  const existing = conn
    .prepare("SELECT id FROM users WHERE username = 'admin'")
    .get();
  if (!existing) {
    conn
      .prepare(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)"
      )
      .run("admin", "admin@example.com", "$2b$10$hashedpassword", "admin");
  }
}

function closeDb() {
  if (db) {
    db.close();
    db = undefined;
  }
}

module.exports = { getDb, initDb, closeDb };
