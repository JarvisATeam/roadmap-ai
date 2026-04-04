import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Roadmap Operator</h1>
        <p className="text-gray-600">
          Manage Echobot leads, review queue, and mission sync.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card title="Echobot">
            <p className="text-gray-600 mb-4">
              Review leads, approve sends, and sync to missions.
            </p>
            <Link href="/operator/echobot">
              <Button>Open Echobot</Button>
            </Link>
          </Card>
        </div>
      </div>
    </div>
  );
}
