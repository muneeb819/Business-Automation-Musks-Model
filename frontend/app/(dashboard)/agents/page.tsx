'use client';

import Link from 'next/link';
import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState } from '../../../components/ui';
import type { Agent } from '../../../lib/types';

const TYPE_LABELS: Record<string, string> = {
  hunting: 'Hunting',
  enrichment: 'Enrichment',
  outreach: 'Outreach',
  content: 'Content',
  social_media: 'Social Media',
  seo: 'SEO',
  paid_traffic: 'Paid Traffic',
  engagement: 'Engagement',
  inbound_lead: 'Inbound Lead',
  supervisor: 'Supervisor',
  optimization: 'Optimization',
  marketplace: 'Marketplace',
};

export default function AgentsPage() {
  const { data: agentsData, loading, error } = useApi<Agent[]>('/agents');
  const agents = agentsData ?? [];

  const activeCount = agents.filter((a) => a.status === 'active').length;

  return (
    <div>
      <PageHeader
        title="Agents"
        description="Your autonomous business development workforce."
      >
        <div className="text-sm text-gray-500">
          <Badge color="green">{activeCount} active</Badge>
        </div>
      </PageHeader>

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : agents.length === 0 ? (
        <EmptyState
          title="No agents configured"
          description="Agents will be seeded once the system is provisioned."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent: Agent) => {
            const successRate =
              agent.total_runs > 0
                ? ((agent.successful_runs / agent.total_runs) * 100).toFixed(0)
                : '100';
            return (
              <Link
                key={agent.id}
                href={`/agents/${agent.id}`}
                className="bg-white rounded-lg shadow p-6 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                    <p className="text-sm text-gray-500">
                      {TYPE_LABELS[agent.agent_type] || agent.agent_type}
                    </p>
                  </div>
                  <Badge color={statusColor(agent.status)}>{agent.status}</Badge>
                </div>
                <div className="flex items-center gap-1 mb-4">
                  <div className="h-2 flex-1 rounded-full bg-gray-100 overflow-hidden">
                    <div
                      className={`h-full ${
                        agent.health_score >= 80
                          ? 'bg-green-500'
                          : agent.health_score >= 60
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${agent.health_score}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-700 w-10 text-right">
                    {agent.health_score}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-gray-50 rounded-md py-2">
                    <p className="text-lg font-bold text-gray-900">{agent.total_runs}</p>
                    <p className="text-xs text-gray-500">Runs</p>
                  </div>
                  <div className="bg-gray-50 rounded-md py-2">
                    <p className="text-lg font-bold text-gray-900">{successRate}%</p>
                    <p className="text-xs text-gray-500">Success</p>
                  </div>
                  <div className="bg-gray-50 rounded-md py-2">
                    <p className="text-lg font-bold text-gray-900">
                      {agent.failed_runs}
                    </p>
                    <p className="text-xs text-gray-500">Failed</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
