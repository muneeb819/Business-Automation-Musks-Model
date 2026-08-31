'use client';

import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, LoadingState, EmptyState, ErrorState } from '../../../components/ui';
import type { LeadStatus } from '../../../lib/types';

const STAGES: { key: LeadStatus; label: string; color: string }[] = [
  { key: 'new', label: 'New', color: 'bg-gray-400' },
  { key: 'contacted', label: 'Contacted', color: 'bg-blue-400' },
  { key: 'engaged', label: 'Engaged', color: 'bg-yellow-400' },
  { key: 'ready_to_close', label: 'Ready to Close', color: 'bg-indigo-400' },
  { key: 'human_handoff', label: 'Human Handoff', color: 'bg-purple-400' },
  { key: 'closed_won', label: 'Closed Won', color: 'bg-green-400' },
  { key: 'closed_lost', label: 'Closed Lost', color: 'bg-red-400' },
];

export default function PipelinePage() {
  const { data: pipeline, loading, error } = useApi<Record<LeadStatus, number>>(
    '/dashboard/pipeline'
  );

  const total = pipeline
    ? Object.values(pipeline).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <div>
      <PageHeader
        title="Pipeline"
        description="Leads by stage across the unified outbound + inbound funnel."
      />

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !pipeline ? (
        <EmptyState title="No pipeline data" />
      ) : (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex items-end justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total: {total} leads</p>
          </div>
          <div className="flex h-6 w-full rounded-full overflow-hidden">
            {STAGES.filter((s) => (pipeline[s.key] ?? 0) > 0).map((s) => (
              <div
                key={s.key}
                className={s.color}
                style={{
                  width: `${total ? ((pipeline[s.key] ?? 0) / total) * 100 : 0}%`,
                  minWidth: '2px',
                }}
                title={`${s.label}: ${pipeline[s.key] ?? 0}`}
              />
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {STAGES.map((stage) => {
          const count = pipeline?.[stage.key] ?? 0;
          const pct = total ? ((count / total) * 100).toFixed(1) : '0';
          return (
            <div key={stage.key} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <span className={`w-2.5 h-2.5 rounded-full ${stage.color}`} />
                  {stage.label}
                </span>
                <Badge>{count}</Badge>
              </div>
              <p className="text-2xl font-bold text-gray-900">{pct}%</p>
              <div className="mt-2 h-2 rounded-full bg-gray-100 overflow-hidden">
                <div className={`h-full ${stage.color}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
