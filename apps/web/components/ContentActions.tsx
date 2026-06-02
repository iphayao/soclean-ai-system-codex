"use client";

import { Check, Save, X } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { api, ContentItem } from "@/app/lib/api";

export function ContentEditForm({ content }: { content: ContentItem }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.updateContentItem(content.id, {
      title: String(form.get("title") || ""),
      body: String(form.get("body") || ""),
      status: String(form.get("status") || content.status),
    });
    setMessage("Content saved.");
    router.refresh();
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field">
          <label htmlFor="title">Title</label>
          <input id="title" name="title" defaultValue={content.title} required />
        </div>
        <div className="field">
          <label htmlFor="status">Status</label>
          <select id="status" name="status" defaultValue={content.status}>
            <option value="draft">Draft</option>
            <option value="in_review">In review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>
      <div className="field">
        <label htmlFor="body">Body</label>
        <textarea id="body" name="body" defaultValue={content.body ?? ""} />
      </div>
      <div className="actions">
        <button type="submit">
          <Save size={16} aria-hidden="true" />
          Save Edits
        </button>
        {message ? <span className="muted">{message}</span> : null}
      </div>
    </form>
  );
}

export function ContentModerationActions({ content }: { content: ContentItem }) {
  const router = useRouter();
  const [isSaving, setIsSaving] = useState(false);

  async function decide(status: "approved" | "rejected") {
    setIsSaving(true);
    try {
      await api.updateContentItem(content.id, { status });
      await api.createApproval({
        content_item_id: content.id,
        reviewer_name: "Dashboard Review",
        status,
        feedback: status === "approved" ? "Approved from dashboard." : "Rejected from dashboard.",
        decided_at: new Date().toISOString(),
      });
      router.refresh();
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="actions">
      <button type="button" onClick={() => decide("approved")} disabled={isSaving}>
        <Check size={16} aria-hidden="true" />
        Approve
      </button>
      <button type="button" className="danger" onClick={() => decide("rejected")} disabled={isSaving}>
        <X size={16} aria-hidden="true" />
        Reject
      </button>
    </div>
  );
}
