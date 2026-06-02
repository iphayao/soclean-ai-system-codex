import Link from "next/link";

import { api, formatDate } from "@/app/lib/api";
import { CampaignForm } from "@/components/Forms";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function CampaignsPage() {
  const [brands, campaigns] = await Promise.all([api.getBrands(), api.getCampaigns()]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Campaigns</h1>
          <p>Create campaigns, generate content, and track campaign status.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">Create Campaign</h2>
          <CampaignForm brands={brands} />
        </div>
        <div className="table">
          <div className="table-row table-head">
            <span>Campaign</span>
            <span>Objective</span>
            <span>Timing</span>
            <span>Status</span>
          </div>
          {campaigns.map((campaign) => (
            <div className="table-row" key={campaign.id}>
              <Link href={`/campaigns/${campaign.id}`} className="item-title">
                {campaign.name}
              </Link>
              <span>{campaign.objective}</span>
              <span>
                {formatDate(campaign.start_date)} to {formatDate(campaign.end_date)}
              </span>
              <StatusBadge status={campaign.status} />
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
