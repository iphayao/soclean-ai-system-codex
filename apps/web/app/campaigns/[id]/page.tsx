import Link from "next/link";
import { notFound } from "next/navigation";

import { api, formatDate } from "@/app/lib/api";
import { GenerateContentButton } from "@/components/GenerateContentButton";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function CampaignDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [campaign, contentItems, agentRuns] = await Promise.all([
    api.getCampaign(id),
    api.getContentItems(),
    api.getAgentRuns(),
  ]);

  if (!campaign) {
    notFound();
  }

  const campaignContent = contentItems.filter((item) => item.campaign_id === id);
  const campaignRuns = agentRuns.filter((run) => run.campaign_id === id);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>{campaign.name}</h1>
          <p>{campaign.objective}</p>
        </div>
        <GenerateContentButton campaignId={campaign.id} />
      </header>

      <section className="grid cols-3">
        <div className="card metric">
          <span>Status</span>
          <StatusBadge status={campaign.status} />
        </div>
        <div className="card metric">
          <span>Timeline</span>
          <strong style={{ fontSize: 18 }}>
            {formatDate(campaign.start_date)} to {formatDate(campaign.end_date)}
          </strong>
        </div>
        <div className="card metric">
          <span>Generated Items</span>
          <strong>{campaignContent.length}</strong>
        </div>
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2 className="section-title">Content</h2>
          <div className="stack">
            {campaignContent.map((item) => (
              <Link key={item.id} href={`/content/${item.id}`} className="memory-panel">
                <h2>{item.title}</h2>
                <p>
                  {item.channel} · {item.format} · {item.status}
                </p>
              </Link>
            ))}
            {campaignContent.length === 0 ? <p className="muted">No content generated yet.</p> : null}
          </div>
        </div>
        <div className="card">
          <h2 className="section-title">Agent Runs</h2>
          <div className="stack">
            {campaignRuns.slice(0, 5).map((run) => (
              <div key={run.id} className="memory-panel">
                <h2>{run.workflow_name}</h2>
                <p>
                  {run.status} · retries {run.retry_count} · {run.steps.length} steps
                </p>
              </div>
            ))}
            {campaignRuns.length === 0 ? <p className="muted">No agent runs yet.</p> : null}
          </div>
        </div>
      </section>
    </>
  );
}
