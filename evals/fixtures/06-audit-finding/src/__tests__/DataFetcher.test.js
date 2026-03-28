import { fetchData } from "../DataFetcher";

global.fetch = jest.fn();

afterEach(() => {
  jest.resetAllMocks();
});

test("returns parsed JSON on success", async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ items: [{ id: 1, title: "Test" }] }),
  });

  const data = await fetchData("/api/records");
  expect(data.items).toHaveLength(1);
  expect(data.items[0].title).toBe("Test");
});

test("throws on non-OK response", async () => {
  fetch.mockResolvedValueOnce({ ok: false, status: 500 });

  await expect(fetchData("/api/records")).rejects.toThrow("Request failed: 500");
});
