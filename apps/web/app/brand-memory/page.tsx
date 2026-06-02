import { getBrands } from "@/app/lib/api";

export const dynamic = "force-dynamic";

export default async function BrandMemoryPage() {
  const brands = await getBrands();
  const brand = brands[0];

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Brand Memory</h1>
          <p>Core SoClean positioning, voice, and compliance guardrails available to future agent workflows.</p>
        </div>
      </header>

      <section className="grid">
        <div className="memory-panel">
          <h2>Brand</h2>
          <p>{brand ? `${brand.name}: ${brand.description ?? "No description saved."}` : "No brand record found."}</p>
        </div>
        <div className="memory-panel">
          <h2>Voice</h2>
          <p>{brand?.voice ?? "No voice guidance saved."}</p>
        </div>
        <div className="memory-panel">
          <h2>Compliance</h2>
          <p>{brand?.compliance_notes ?? "No compliance notes saved."}</p>
        </div>
      </section>
    </>
  );
}
