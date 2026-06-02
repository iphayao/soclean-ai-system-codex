import { getApprovals, getBrands, getCampaigns, getContentItems, getProducts } from "@/app/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [brands, products, campaigns, contentItems, approvals] = await Promise.all([
    getBrands(),
    getProducts(),
    getCampaigns(),
    getContentItems(),
    getApprovals(),
  ]);

  const pendingApprovals = approvals.filter((approval) => approval.status === "pending").length;
  const inReview = contentItems.filter((item) => item.status === "in_review").length;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Operational overview for SoClean brand memory, product context, campaign work, and review queues.</p>
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
          <span>Pending Reviews</span>
          <strong>{pendingApprovals + inReview}</strong>
        </div>
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="memory-panel">
          <h2>Active Campaign Focus</h2>
          <p>
            {campaigns.find((campaign) => campaign.status === "active")?.objective ??
              "No active campaign loaded yet. Start the API and seed database to populate this view."}
          </p>
        </div>
        <div className="memory-panel">
          <h2>Review Queue</h2>
          <p>
            {pendingApprovals > 0
              ? `${pendingApprovals} approval item${pendingApprovals === 1 ? "" : "s"} awaiting review.`
              : "No pending approval records found."}
          </p>
        </div>
      </section>
    </>
  );
}
