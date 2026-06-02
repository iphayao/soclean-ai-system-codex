import { notFound } from "next/navigation";

import { api, campaignName, productName } from "@/app/lib/api";
import { ContentEditForm, ContentExportButton, ContentModerationActions } from "@/components/ContentActions";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function ContentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [content, campaigns, products, approvals] = await Promise.all([
    api.getContentItem(id),
    api.getCampaigns(),
    api.getProducts(),
    api.getApprovals(),
  ]);

  if (!content) {
    notFound();
  }

  const contentApprovals = approvals.filter((approval) => approval.content_item_id === content.id);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>{content.title}</h1>
          <p>
            {campaignName(campaigns, content.campaign_id)} · {productName(products, content.product_id)}
          </p>
        </div>
        <StatusBadge status={content.status} />
      </header>

      <section className="grid cols-2">
        <div className="card stack">
          <h2 className="section-title">Content</h2>
          <p className="detail-body">{content.body ?? "No body saved."}</p>
          <ContentModerationActions content={content} />
          <ContentExportButton content={content} />
        </div>
        <div className="card">
          <h2 className="section-title">Edit Content</h2>
          <ContentEditForm content={content} />
        </div>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <h2 className="section-title">Approvals</h2>
        <div className="stack">
          {contentApprovals.map((approval) => (
            <div key={approval.id} className="memory-panel">
              <h2>{approval.reviewer_name}</h2>
              <p>
                {approval.status} · {approval.feedback ?? "No feedback"}
              </p>
            </div>
          ))}
          {contentApprovals.length === 0 ? <p className="muted">No approval history yet.</p> : null}
        </div>
      </section>
    </>
  );
}
