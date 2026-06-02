import { CsvImportForm } from "@/components/Forms";
import { api } from "@/app/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function PerformancePage() {
  const campaigns = await api.getCampaigns();
  const selectedCampaign = campaigns[0] ?? null;
  const analytics = selectedCampaign ? await api.getCampaignAnalytics(selectedCampaign.id) : [];

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Performance</h1>
          <p>Import CSV performance metrics for future reporting and optimization workflows.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">CSV Import</h2>
          <CsvImportForm />
        </div>
        <div className="card">
          <h2 className="section-title">Performance Metrics</h2>
          <p className="muted">
            {selectedCampaign ? `Showing ${selectedCampaign.name}` : "Import analytics after creating a campaign."}
          </p>
          <div style={{ marginTop: 12 }}>
            {selectedCampaign ? <StatusBadge status={selectedCampaign.status} /> : null}
          </div>
        </div>
      </section>

      <section className="table" style={{ marginTop: 16 }}>
        <div className="table-row cols-6 table-head">
          <span>Platform</span>
          <span>Views</span>
          <span>Engagement</span>
          <span>Orders</span>
          <span>Revenue / Spend</span>
          <span>ROAS</span>
        </div>
        {analytics.map((row) => (
          <div className="table-row cols-6" key={row.platform}>
            <span className="item-title">{row.platform}</span>
            <span>{row.views}</span>
            <span>{row.likes + row.comments + row.shares}</span>
            <span>{row.orders}</span>
            <span>
              {row.revenue.toFixed(2)} / {row.spend.toFixed(2)}
            </span>
            <span>{row.roas === null ? "N/A" : row.roas.toFixed(2)}</span>
          </div>
        ))}
        {analytics.length === 0 ? <div className="empty">No analytics imported yet.</div> : null}
      </section>
    </>
  );
}
