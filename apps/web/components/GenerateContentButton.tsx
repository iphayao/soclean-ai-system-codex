"use client";

import { Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { api } from "@/app/lib/api";

export function GenerateContentButton({ campaignId }: { campaignId: string }) {
  const router = useRouter();
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function generate() {
    setIsRunning(true);
    setMessage(null);
    try {
      const result = await api.generateCampaignContent(campaignId);
      setMessage(`Generated ${result.content_item_ids.length} content items.`);
      router.refresh();
    } catch {
      setMessage("Generation failed. Check the API service.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="actions">
      <button type="button" onClick={generate} disabled={isRunning}>
        <Play size={16} aria-hidden="true" />
        {isRunning ? "Generating" : "Generate Content"}
      </button>
      {message ? <span className="muted">{message}</span> : null}
    </div>
  );
}
