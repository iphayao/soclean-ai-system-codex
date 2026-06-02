import { getProducts } from "@/app/lib/api";

export const dynamic = "force-dynamic";

function formatCurrency(cents: number | null) {
  if (cents === null) {
    return "Not set";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(cents / 100);
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Products</h1>
          <p>Product facts and benefits that content workflows can reference without inventing details.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row table-head">
          <span>Product</span>
          <span>Category</span>
          <span>Price</span>
          <span>Status</span>
        </div>
        {products.map((product) => (
          <div className="table-row" key={product.id}>
            <span>
              <span className="item-title">{product.name}</span>
              <br />
              <span className="muted">{product.key_benefits.join(", ") || "No benefits saved"}</span>
            </span>
            <span>{product.category}</span>
            <span>{formatCurrency(product.price_cents)}</span>
            <span className={`pill ${product.active ? "active" : "draft"}`}>{product.active ? "active" : "inactive"}</span>
          </div>
        ))}
      </section>
    </>
  );
}
