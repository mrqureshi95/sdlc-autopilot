const request = require("supertest");
const app = require("../app");

describe("POST /api/transform", () => {
  it("should transform text to uppercase", async () => {
    const res = await request(app)
      .post("/api/transform")
      .send({ text: "hello" });
    expect(res.status).toBe(200);
    expect(res.body.result).toBe("HELLO");
  });

  // Missing: no test for empty body — this is the bug scenario
});

describe("GET /api/health", () => {
  it("should return ok", async () => {
    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});
