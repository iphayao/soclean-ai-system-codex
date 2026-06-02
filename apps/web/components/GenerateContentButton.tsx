"use client";

import { Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { api } from "@/app/lib/api";

export function GenerateContentButton({ campaignId }: { campaignId: string }) {
  const router = useRouter();
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function pollJob(jobId: string) {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      const job = await api.getJob(jobId);
      setStatus(job.status);
      if (job.status === "completed") {
        const count = Array.isArray(job.result_metadata.content_item_ids)
          ? job.result_metadata.content_item_ids.length
          : 0;
        setMessage(`Generated ${count} content items.`);
        router.refresh();
        return;
      }
      if (job.status === "failed") {
        setMessage(job.error ?? "Generation failed.");
        router.refresh();
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
    setMessage("Generation is still running. Refresh for the latest status.");
  }

  async function generate() {
    setIsRunning(true);
    setMessage(null);
    setStatus("queued");
    try {
      const result = await api.generateCampaignContent(campaignId);
      setStatus(result.status);
      setMessage(`Job ${result.job_id.slice(0, 8)} queued.`);
      await pollJob(result.job_id);
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
      {status ? <span className={`pill ${status}`}>{status}</span> : null}
      {message ? <span className="muted">{message}</span> : null}
    </div>
  );
}
