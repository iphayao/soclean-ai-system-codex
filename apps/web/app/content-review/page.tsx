import Link from "next/link";

import { api, campaignName } from "@/app/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function ContentReviewPage() {
  const [contentItems, campaigns, approvals] = await Promise.all([
    api.getContentItems(),
    api.getCampaigns(),
    api.getApprovals(),
  ]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Content Review</h1>
          <p>Review generated drafts, approval status, and claim-safety feedback.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row cols-5 table-head">
          <span>Content</span>
          <span>Campaign</span>
          <span>Channel</span>
          <span>Latest Approval</span>
          <span>Status</span>
        </div>
        {contentItems.map((item) => {
          const approval = approvals.find((record) => record.content_item_id === item.id);
          return (
            <div className="table-row cols-5" key={item.id}>
              <Link href={`/content/${item.id}`} className="item-title">
                {item.title}
              </Link>
              <span>{campaignName(campaigns, item.campaign_id)}</span>
              <span>
                {item.channel} / {item.format}
              </span>
              <span>{approval?.feedback ?? "No approval record"}</span>
              <StatusBadge status={approval?.status ?? item.status} />
            </div>
          );
        })}
        {contentItems.length === 0 ? <div className="empty">No content items found.</div> : null}
      </section>
    </>
  );
}
