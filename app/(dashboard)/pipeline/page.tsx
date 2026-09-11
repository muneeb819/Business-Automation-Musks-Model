'use client';

import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  Badge,
  LoadingState,
  ErrorState,
} from '../../../components/ui';

const STAGES: { key: string; label: string; color: 'blue' | 'yellow' | 'green' | 'red' | 'purple' | 'gray' }[] = [
  { key: 'new', label: 'New', color: 'blue' },
  { key: 'contacted', label: 'Contacted', color: 'yellow' },
  { key: 'engaged', label: 'Engaged', color: 'green' },
  { key: 'ready_to_close', label: 'Ready to Close', color: 'green' },
  { key: 'human_handoff', label: 'Human Handoff', color: 'purple' },
  { key: 'closed_won', label: 'Closed Won', color: 'green' },
  { key: 'closed_lost', label: 'Closed Lost', color: 'red' },
  { key: 'disqualified', label: 'Disqualified', color: 'gray' },
];

export default function PipelinePage() {
  const { data: pipeline, loading, error } = useApi<Record<string, number>>(
    '/dashboard/pipeline'
  );

  const total = pipeline
    ? Object.values(pipeline).reduce((sum, n) => sum + (n || 0), 0)
    : 0;

  return (
    <div>
      <PageHeader
        title="Pipeline"
        description="Lead volume across every stage of the outbound + inbound funnel."
      />

      {error && <ErrorState message={error} />}

      {loading ? (
        <LoadingState />
      ) : (
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-500">Total leads in pipeline</p>
            <p className="text-3xl font-bold text-gray-900">{total}</p>
          </div>

          <div className="bg-white rounded-lg shadow divide-y divide-gray-100">
            {STAGES.map((stage) => {
              const count = pipeline?.[stage.key] ?? 0;
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <div key={stage.key} className="px-6 py-4 flex items-center gap-4">
                  <Badge color={stage.color}>{stage.label}</Badge>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="w-40 text-right">
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                    <span className="text-sm text-gray-400 ml-2">({pct}%)</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
