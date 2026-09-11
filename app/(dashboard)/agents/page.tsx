'use client';

import Link from 'next/link';
import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  Badge,
  statusColor,
  LoadingState,
  EmptyState,
  ErrorState,
} from '../../../components/ui';
import type { Agent } from '../../../lib/types';

export default function AgentsPage() {
  const { data: agents, loading, error } = useApi<Agent[]>('/agents');

  return (
    <div>
      <PageHeader
        title="Agents"
        description="The autonomous workers that power the business development pipeline."
      />

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !agents || agents.length === 0 ? (
        <EmptyState
          title="No agents configured"
          description="Seed the platform to provision your default agent team."
        />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Health
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Runs
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  &nbsp;
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {agents.map((agent: Agent) => (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {agent.name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {agent.agent_type.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4">
                    <Badge color={statusColor(agent.status)}>{agent.status}</Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {agent.health_score.toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {agent.successful_runs}/{agent.total_runs} succeeded
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/agents/${agent.id}`}
                      className="text-sm font-medium text-primary-600 hover:text-primary-700"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
