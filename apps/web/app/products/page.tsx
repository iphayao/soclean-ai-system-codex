import { api } from "@/app/lib/api";
import { ProductForm } from "@/components/Forms";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

function formatCurrency(cents: number | null) {
  if (!cents) {
    return "Not set";
  }
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(cents / 100);
}

export default async function ProductsPage() {
  const [brands, products] = await Promise.all([api.getBrands(), api.getProducts()]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Products</h1>
          <p>Product facts available to content agents and reviewers.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">Add Product</h2>
          <ProductForm brands={brands} />
        </div>
        <div className="table">
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
              <StatusBadge status={product.active ? "active" : "draft"} />
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
