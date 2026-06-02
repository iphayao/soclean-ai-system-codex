import { API_BASE_URL } from "@/app/lib/api";

export default function SettingsPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Runtime configuration for the SoClean dashboard.</p>
        </div>
      </header>

      <section className="grid cols-2">
        <div className="card">
          <h2 className="section-title">API</h2>
          <p className="muted">Configured API base URL</p>
          <p className="item-title">{API_BASE_URL}</p>
        </div>
        <div className="card">
          <h2 className="section-title">Environment</h2>
          <p className="muted">Set `NEXT_PUBLIC_API_BASE_URL` to point the browser client at another API host.</p>
        </div>
      </section>
    </>
  );
}
