import Link from "next/link";

import { api, campaignName } from "@/app/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [brands, products, campaigns, contentItems, approvals, agentRuns] = await Promise.all([
    api.getBrands(),
    api.getProducts(),
    api.getCampaigns(),
    api.getContentItems(),
    api.getApprovals(),
    api.getAgentRuns(),
  ]);

  const inReview = contentItems.filter((item) => item.status === "in_review").length;
  const approved = contentItems.filter((item) => item.status === "approved").length;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>SoClean content operations at a glance.</p>
        </div>
      </header>

      <section className="grid cols-4">
        <div className="card metric">
          <span>Brands</span>
          <strong>{brands.length}</strong>
        </div>
        <div className="card metric">
          <span>Products</span>
          <strong>{products.length}</strong>
        </div>
        <div className="card metric">
          <span>Campaigns</span>
          <strong>{campaigns.length}</strong>
        </div>
        <div className="card metric">
          <span>Review Queue</span>
          <strong>{inReview}</strong>
        </div>
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2 className="section-title">Recent Content</h2>
          <div className="stack">
            {contentItems.slice(0, 5).map((item) => (
              <Link key={item.id} href={`/content/${item.id}`} className="memory-panel">
                <h2>{item.title}</h2>
                <p>
                  {campaignName(campaigns, item.campaign_id)} · {item.channel}
                </p>
              </Link>
            ))}
            {contentItems.length === 0 ? <p className="muted">No content yet.</p> : null}
          </div>
        </div>
        <div className="card">
          <h2 className="section-title">System Health</h2>
          <div className="grid cols-2">
            <div className="metric">
              <span>Approved</span>
              <strong>{approved}</strong>
            </div>
            <div className="metric">
              <span>Agent Runs</span>
              <strong>{agentRuns.length}</strong>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            {approvals[0] ? <StatusBadge status={approvals[0].status} /> : <span className="muted">No approvals yet</span>}
          </div>
        </div>
      </section>
    </>
  );
}
