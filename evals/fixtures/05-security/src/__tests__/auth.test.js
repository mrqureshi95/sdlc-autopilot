const request = require("supertest");
const app = require("../server");
const { closeDb } = require("../db");

afterAll(() => {
  closeDb();
});

describe("POST /auth/login", () => {
  it("returns 400 when username is missing", async () => {
    const res = await request(app)
      .post("/auth/login")
      .send({ password: "test" });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("Username and password required");
  });

  it("returns 401 for invalid credentials", async () => {
    const res = await request(app)
      .post("/auth/login")
      .send({ username: "nobody", password: "wrong" });
    expect(res.status).toBe(401);
  });
});

describe("POST /auth/register", () => {
  it("returns 400 when fields are missing", async () => {
    const res = await request(app)
      .post("/auth/register")
      .send({ username: "newuser" });
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("All fields are required");
  });
});

describe("GET /health", () => {
  it("returns ok status", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});
