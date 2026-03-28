const express = require("express");
const { initDb } = require("./db");
const authRoutes = require("./routes/auth");
const usersRoutes = require("./routes/users");

const app = express();
app.use(express.json());

// Initialize database
initDb();

// Routes
app.use("/auth", authRoutes);
app.use("/users", usersRoutes);

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
}

module.exports = app;
