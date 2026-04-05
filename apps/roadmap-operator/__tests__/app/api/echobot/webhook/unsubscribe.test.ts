import { POST } from "@/app/api/echobot/webhook/unsubscribe/route";

describe("/api/echobot/webhook/unsubscribe", () => {
  describe("POST", () => {
    it("should process unsubscribe by email", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/unsubscribe",
        {
          method: "POST",
          body: JSON.stringify({
            email: "user@example.com",
            reason: "No longer interested",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.optedOut).toBe(true);
    });

    it("should process unsubscribe by leadId", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/unsubscribe",
        {
          method: "POST",
          body: JSON.stringify({
            leadId: "lead-123",
            reason: "Too many emails",
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it("should return error for missing email and leadId", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/unsubscribe",
        {
          method: "POST",
          body: JSON.stringify({
            reason: "No identifier provided",
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
