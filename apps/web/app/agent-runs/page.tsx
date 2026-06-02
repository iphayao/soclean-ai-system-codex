import { api, campaignName, formatDate } from "@/app/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export const dynamic = "force-dynamic";

export default async function AgentRunsPage() {
  const [agentRuns, campaigns] = await Promise.all([api.getAgentRuns(), api.getCampaigns()]);

  return (
    <>
      <header className="page-header">
        <div>
          <h1>Agent Runs</h1>
          <p>Execution history for content generation workflows.</p>
        </div>
      </header>

      <section className="table">
        <div className="table-row cols-6 table-head">
          <span>Run</span>
          <span>Campaign</span>
          <span>Retries</span>
          <span>Steps</span>
          <span>Created</span>
          <span>Status</span>
        </div>
        {agentRuns.map((run) => (
          <div className="table-row cols-6" key={run.id}>
            <span className="item-title">{run.workflow_name}</span>
            <span>{campaignName(campaigns, run.campaign_id)}</span>
            <span>{run.retry_count}</span>
            <span>{run.steps.length}</span>
            <span>{formatDate(run.created_at)}</span>
            <StatusBadge status={run.status} />
          </div>
        ))}
        {agentRuns.length === 0 ? <div className="empty">No agent runs logged yet.</div> : null}
      </section>
    </>
  );
}
