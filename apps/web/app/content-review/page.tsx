import { getApprovals, getContentItems } from "@/app/lib/api";

export const dynamic = "force-dynamic";

export default async function ContentReviewPage() {
  const [contentItems, approvals] = await Promise.all([getContentItems(), getApprovals()]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Content Review</h1>
          <p>Draft content and approval records for human review before scheduling or publishing.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row table-head">
          <span>Content</span>
          <span>Channel</span>
          <span>Approval</span>
          <span>Status</span>
        </div>
        {contentItems.map((item) => {
          const approval = approvals.find((record) => record.content_item_id === item.id);
          return (
            <div className="table-row" key={item.id}>
              <span>
                <span className="item-title">{item.title}</span>
                <br />
                <span className="muted">{item.body ?? "No body saved"}</span>
              </span>
              <span>
                {item.channel} / {item.format}
              </span>
              <span>{approval?.feedback ?? "No approval record"}</span>
              <span className={`pill ${approval?.status ?? item.status}`}>{approval?.status ?? item.status}</span>
            </div>
          );
        })}
      </section>
    </>
  );
}
