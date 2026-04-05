import { POST } from "@/app/api/echobot/webhook/stripe/route";

describe("/api/echobot/webhook/stripe", () => {
  describe("POST", () => {
    const validStripeEvent = {
      id: "evt_123",
      type: "invoice.paid",
      data: {
        object: {
          customer_email: "customer@example.com",
          hosted_invoice_url: "https://invoice.stripe.com/i/123",
        },
      },
    };

    it("should process invoice.paid event", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/stripe",
        {
          method: "POST",
          body: JSON.stringify(validStripeEvent),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.processed).toBe(true);
    });

    it("should deduplicate duplicate events", async () => {
      const request1 = new Request(
        "http://localhost/api/echobot/webhook/stripe",
        {
          method: "POST",
          body: JSON.stringify(validStripeEvent),
        }
      );
      await POST(request1);

      const request2 = new Request(
        "http://localhost/api/echobot/webhook/stripe",
        {
          method: "POST",
          body: JSON.stringify(validStripeEvent),
        }
      );
      const response2 = await POST(request2);
      const data2 = await response2.json();

      expect(response2.status).toBe(200);
      expect(data2.duplicate).toBe(true);
    });

    it("should ignore non-invoice.paid events", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/stripe",
        {
          method: "POST",
          body: JSON.stringify({
            id: "evt_456",
            type: "customer.created",
            data: {},
          }),
        }
      );

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.ignored).toBe(true);
    });

    it("should return error for missing eventId", async () => {
      const request = new Request(
        "http://localhost/api/echobot/webhook/stripe",
        {
          method: "POST",
          body: JSON.stringify({
            type: "invoice.paid",
            data: {},
          }),
        }
      );

      const response = await POST(request);
      expect(response.status).toBe(400);
    });
  });
});
