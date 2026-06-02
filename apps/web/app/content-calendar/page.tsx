import Link from "next/link";

import { api, campaignName, formatDate } from "@/app/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function ContentCalendarPage() {
  const [contentItems, campaigns] = await Promise.all([api.getContentItems(), api.getCampaigns()]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Content Calendar</h1>
          <p>Simple publishing list grouped by generated content and campaign timing.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row table-head">
          <span>Content</span>
          <span>Campaign</span>
          <span>Planned Date</span>
          <span>Status</span>
        </div>
        {contentItems.map((item) => {
          const campaign = campaigns.find((record) => record.id === item.campaign_id);
          return (
            <div className="table-row" key={item.id}>
              <Link href={`/content/${item.id}`} className="item-title">
                {item.title}
              </Link>
              <span>{campaignName(campaigns, item.campaign_id)}</span>
              <span>{formatDate(campaign?.start_date)}</span>
              <StatusBadge status={item.status} />
            </div>
          );
        })}
      </section>
    </>
  );
}
