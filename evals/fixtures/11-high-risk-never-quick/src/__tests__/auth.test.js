const request = require("supertest");
const app = require("../server");

describe("POST /auth/login", () => {
  it("returns 400 when username is missing", async () => {
    const res = await request(app).post("/auth/login").send({ password: "test" });
    expect(res.status).toBe(400);
  });

  it("returns 401 for invalid credentials", async () => {
    const res = await request(app).post("/auth/login").send({ username: "nobody", password: "wrong" });
    expect(res.status).toBe(401);
  });
});
