import { GET } from "@/app/api/echobot/stats/route";

describe("/api/echobot/stats", () => {
  describe("GET", () => {
    it("should return stats with default values", async () => {
      const response = await GET();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data).toEqual({
        total: 0,
        leadsByStatus: {},
        leadsByTruth: {},
        sentiments: {},
        replyRate: 0,
        positiveRate: 0,
        queueSize: 0,
      });
    });

    it("should return proper content-type header", async () => {
      const response = await GET();
      expect(response.headers.get("content-type")).toContain("application/json");
    });
  });
});
