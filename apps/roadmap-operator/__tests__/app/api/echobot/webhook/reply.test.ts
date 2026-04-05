import { POST } from "@/app/api/echobot/webhook/reply/route";

describe("/api/echobot/webhook/reply", () => {
  describe("POST", () => {
    it("should process positive reply", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/reply",
        {
          method: "POST",
          body: JSON.stringify({
            leadId: "lead-123",
            sentiment: "positive",
            replyText: "Yes, I'm interested!",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.processed).toBe(true);
    });

    it("should process negative reply", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/reply",
        {
          method: "POST",
          body: JSON.stringify({
            leadId: "lead-123",
            sentiment: "negative",
            replyText: "Not interested, please remove me",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it("should return error for missing leadId", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/reply",
        {
          method: "POST",
          body: JSON.stringify({
            sentiment: "positive",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toContain("Missing");
    });

    it("should return error for missing sentiment", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/reply",
        {
          method: "POST",
          body: JSON.stringify({
            leadId: "lead-123",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toContain("Missing");
    });
  });
});
