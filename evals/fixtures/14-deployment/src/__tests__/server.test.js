const request = require("supertest");
const app = require("../server");

describe("GET /api/data", () => {
  it("returns items", async () => {
    const res = await request(app).get("/api/data");
    expect(res.status).toBe(200);
    expect(res.body.items).toHaveLength(2);
  });
});

describe("GET /health", () => {
  it("returns health status", async () => {
    const res = await request(app).get("/health");
    expect(res.body.status).toBe("ok");
  });
});
