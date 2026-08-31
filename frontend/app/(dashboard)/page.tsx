'use client';

import { useApi } from '../../lib/useApi';
import {
  StatCard,
  Badge,
  statusColor,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../components/ui';
import type {
  DashboardOverview,
  Activity,
  LeadStatus,
} from '../../lib/types';
import { useEffect, useState } from 'react';

const PIPELINE_LABELS: { key: string; label: string }[] = [
  { key: 'new', label: 'New' },
  { key: 'contacted', label: 'Contacted' },
  { key: 'engaged', label: 'Engaged' },
  { key: 'ready_to_close', label: 'Ready to Close' },
  { key: 'human_handoff', label: 'Human Handoffs' },
  { key: 'closed_won', label: 'Closed Won' },
  { key: 'closed_lost', label: 'Closed Lost' },
];

export default function OverviewPage() {
  const { data: overview, loading, error } = useApi<DashboardOverview>(
    '/dashboard/overview'
  );
  const { data: pipeline } = useApi<Record<LeadStatus, number>>(
    '/dashboard/pipeline'
  );
  const { data: activityData } = useApi<Activity[]>('/dashboard/recent-activity');
  const activity = activityData ?? [];
  const [supervisorAnswer, setSupervisorAnswer] = useState<string | null>(null);
  const [supervisorLoading, setSupervisorLoading] = useState(false);

  async function askSupervisor(query: string) {
    if (!query.trim()) return;
    setSupervisorLoading(true);
    setSupervisorAnswer(null);
    try {
      const { ApiError } = await import('../../lib/api');
      const api = (await import('../../lib/api')).default;
      const res = await api.post<{ response: string }>('/supervisor/command', {
        command: query,
      });
      setSupervisorAnswer(res.response || 'Supervisor acknowledged.');
    } catch (e) {
      setSupervisorAnswer(
        e instanceof Error ? e.message : 'Unable to reach Supervisor.'
      );
    } finally {
      setSupervisorLoading(false);
    }
  }

  return (
    <div>
      {error && <ErrorState message={error} />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          label="Total Leads"
          value={overview?.leads.total ?? (loading ? '—' : 0)}
          hint="Across both outbound and inbound funnels"
        />
        <StatCard
          label="Active Agents"
          value={overview?.agents.active ?? (loading ? '—' : 0)}
          hint={`${overview?.agents.failed ?? 0} failed`}
          accent={overview && overview.agents.failed > 0 ? 'text-red-600' : 'text-gray-900'}
        />
        <StatCard
          label="Pending Approvals"
          value={overview?.approvals.pending ?? (loading ? '—' : 0)}
          hint="Awaiting human decision"
        />
        <StatCard
          label="Deals Won"
          value={overview?.leads.won ?? (loading ? '—' : 0)}
          hint={`${overview?.leads.lost ?? 0} lost`}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
        <div className="xl:col-span-1 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Lead Pipeline
          </h3>
          {loading ? (
            <LoadingState />
          ) : (
            <div className="space-y-3">
              {PIPELINE_LABELS.map(({ key, label }) => {
                const value =
                  key === 'new' ||
                  key === 'contacted' ||
                  key === 'engaged' ||
                  key === 'ready_to_close'
                    ? (overview?.leads as Record<string, number> | undefined)?.[
                        key
                      ]
                    : pipeline?.[key as LeadStatus];
                return (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{label}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {value ?? 0}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="xl:col-span-2 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Activity
          </h3>
          {loading ? (
            <LoadingState />
          ) : activity.length === 0 ? (
            <EmptyState
              title="No recent activity"
              description="Activity will appear here as agents work through the pipeline."
            />
          ) : (
            <div className="divide-y divide-gray-100">
              {activity.map((a) => (
                <div key={a.id} className="py-3 flex items-start justify-between">
                  <div>
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">{a.agent_name}</span>{' '}
                      <span className="text-gray-500">{a.action_type}</span>
                    </p>
                    {a.summary && (
                      <p className="text-sm text-gray-500">{a.summary}</p>
                    )}
                  </div>
                  <div className="text-right text-xs text-gray-400">
                    {formatDate(a.created_at)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Supervisor Command Center
        </h3>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            const input = e.currentTarget.elements.namedItem(
              'query'
            ) as HTMLInputElement;
            askSupervisor(input.value);
            input.value = '';
          }}
        >
          <input
            name="query"
            type="text"
            placeholder="Ask Supervisor anything..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            type="submit"
            disabled={supervisorLoading}
            className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {supervisorLoading ? 'Working...' : 'Ask'}
          </button>
        </form>
        {supervisorAnswer && (
          <div className="mt-4 bg-gray-50 border border-gray-200 rounded-md p-4 text-sm text-gray-700">
            {supervisorAnswer}
          </div>
        )}
      </div>
    </div>
  );
}
