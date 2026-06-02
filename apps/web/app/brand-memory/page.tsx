import { api } from "@/app/lib/api";
import { BrandMemoryForm } from "@/components/Forms";

export const dynamic = "force-dynamic";

export default async function BrandMemoryPage() {
  const brands = await api.getBrands();
  const brand = brands[0] ?? null;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Brand Memory</h1>
          <p>Manage SoClean positioning, tone, and compliance guardrails for generation workflows.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">Memory Form</h2>
          <BrandMemoryForm brand={brand} />
        </div>
        <div className="card">
          <h2 className="section-title">Current Guidance</h2>
          <div className="stack">
            <div className="memory-panel">
              <h2>Voice</h2>
              <p>{brand?.voice ?? "No voice guidance saved."}</p>
            </div>
            <div className="memory-panel">
              <h2>Compliance</h2>
              <p>{brand?.compliance_notes ?? "No compliance notes saved."}</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
