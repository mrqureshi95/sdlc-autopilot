const Database = require("better-sqlite3");

let db;

function getDb() {
  if (!db) {
    db = new Database(":memory:");
    db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      )
    `);
    db.prepare("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)").run("admin", "hashed_pw");
  }
  return db;
}

module.exports = { getDb };
