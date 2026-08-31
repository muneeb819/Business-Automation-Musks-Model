'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useApi } from '../../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState, formatDate, StatCard } from '../../../../components/ui';
import type { Agent, AgentHealthScore, AgentRun } from '../../../../lib/types';

export default function AgentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const { data: agent } = useApi<Agent>(`/agents/${id}`);
  const { data: health } = useApi<AgentHealthScore>(`/agents/${id}/health`);
  const { data: runsData } = useApi<AgentRun[]>(`/agents/${id}/runs`);
  const runs = runsData ?? [];

  if (!agent) {
    return <LoadingState />;
  }

  const metricItems = [
    { label: 'Availability', value: health?.availability },
    { label: 'Execution Success', value: health?.execution_success },
    { label: 'Task Completion', value: health?.task_completion },
    { label: 'Output Quality', value: health?.output_quality },
    { label: 'Cost Efficiency', value: health?.cost_efficiency },
    { label: 'Policy Compliance', value: health?.policy_compliance },
    { label: 'Error Rate', value: health?.error_rate },
    { label: 'Latency (ms)', value: health?.latency },
  ];

  return (
    <div>
      <div className="mb-4">
        <Link href="/agents" className="text-sm text-primary-600 hover:text-primary-700">
          &larr; Back to Agents
        </Link>
      </div>
      <PageHeader title={agent.name} description={`Agent Health · ${agent.agent_type}`}>
        <Badge color={statusColor(agent.status)}>{agent.status}</Badge>
      </PageHeader>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        <StatCard label="Overall Health" value={health ? `${health.overall_score}` : '—'} accent={health && health.overall_score >= 80 ? 'text-green-600' : 'text-yellow-600'} />
        <StatCard label="Total Runs" value={agent.total_runs} />
        <StatCard label="Successful" value={agent.successful_runs} />
        <StatCard label="Failed" value={agent.failed_runs} accent={agent.failed_runs > 0 ? 'text-red-600' : 'text-gray-900'} />
      </div>

      {health && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Health Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metricItems.map((m) => (
              <div key={m.label} className="bg-gray-50 rounded-md p-4">
                <p className="text-sm text-gray-500">{m.label}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {m.value !== undefined ? `${m.value}${m.label === 'Latency (ms)' ? '' : '%'}` : '—'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Runs</h3>
        {runs.length === 0 ? (
          <EmptyState title="No runs recorded" description="This agent has not run yet." />
        ) : (
          <div className="divide-y divide-gray-100">
            {runs.map((run) => (
              <div key={run.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{run.status}</p>
                  {run.error_message && (
                    <p className="text-sm text-red-600">{run.error_message}</p>
                  )}
                </div>
                <div className="text-right text-xs text-gray-400">
                  <p>{formatDate(run.started_at)}</p>
                  <p>{run.duration_ms != null ? `${run.duration_ms} ms` : '—'}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
