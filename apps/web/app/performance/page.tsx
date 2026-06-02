import { CsvImportForm } from "@/components/Forms";

export const dynamic = "force-dynamic";

export default function PerformancePage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1>Performance</h1>
          <p>Import CSV performance metrics for future reporting and optimization workflows.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">CSV Import</h2>
          <CsvImportForm />
        </div>
        <div className="card">
          <h2 className="section-title">Performance Metrics</h2>
          <p className="muted">Metrics storage and charts will be added in a later phase.</p>
        </div>
      </section>
    </>
  );
}
