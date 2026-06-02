import { getCampaigns } from "@/app/lib/api";

export const dynamic = "force-dynamic";

export default async function CampaignsPage() {
  const campaigns = await getCampaigns();

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Campaigns</h1>
          <p>Campaign objectives, audiences, and status tracking for SoClean content planning.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row table-head">
          <span>Campaign</span>
          <span>Objective</span>
          <span>Timing</span>
          <span>Status</span>
        </div>
        {campaigns.map((campaign) => (
          <div className="table-row" key={campaign.id}>
            <span className="item-title">{campaign.name}</span>
            <span>{campaign.objective}</span>
            <span>
              {campaign.start_date ?? "TBD"} to {campaign.end_date ?? "TBD"}
            </span>
            <span className={`pill ${campaign.status}`}>{campaign.status}</span>
          </div>
        ))}
      </section>
    </>
  );
}
