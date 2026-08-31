'use client';

import { Suspense, useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '../../../lib/api';
import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState, formatDate } from '../../../components/ui';
import type { Lead, LeadListResponse, LeadStatus } from '../../../lib/types';

const STATUS_FILTERS: { value: LeadStatus | ''; label: string }[] = [
  { value: '', label: 'All' },
  { value: 'new', label: 'New' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'engaged', label: 'Engaged' },
  { value: 'ready_to_close', label: 'Ready to Close' },
  { value: 'human_handoff', label: 'Human Handoff' },
  { value: 'closed_won', label: 'Won' },
  { value: 'closed_lost', label: 'Lost' },
  { value: 'disqualified', label: 'Disqualified' },
];

export default function LeadsPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <LeadsInner />
    </Suspense>
  );
}

function LeadsInner() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<LeadStatus | ''>(
    (searchParams.get('status') as LeadStatus) || ''
  );
  const [page, setPage] = useState(1);

  const query = new URLSearchParams({ page: String(page), page_size: '20' });
  if (status) query.set('status', status);

  const { data, loading, error, refetch } = useApi<LeadListResponse>(
    `/leads?${query.toString()}`,
    [page, status]
  );

  useEffect(() => {
    setPage(1);
  }, [status]);

  const handleHandoff = useCallback(
    async (id: string) => {
      try {
        await api.post(`/leads/${id}/handoff`);
        refetch();
      } catch (e) {
        alert(e instanceof Error ? e.message : 'Handoff failed');
      }
    },
    [refetch]
  );

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div>
      <PageHeader
        title="Leads"
        description="All prospects in the unified outbound + inbound pipeline."
      />

      <div className="flex gap-2 mb-6 flex-wrap">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value || 'all'}
            onClick={() => setStatus(f.value)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md ${
              status === f.value
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !data || data.leads.length === 0 ? (
        <EmptyState
          title="No leads found"
          description={status ? 'Try a different status filter.' : 'Leads will appear here once hunting begins.'}
        />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fit</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Outreach</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3" />
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {data.leads.map((lead: Lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <Badge color={statusColor(lead.status)}>{lead.status.replace(/_/g, ' ')}</Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{lead.source.replace(/_/g, ' ')}</td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{lead.fit_score.toFixed(1)}</td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{lead.lead_score.toFixed(1)}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{lead.outreach_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{formatDate(lead.created_at)}</td>
                    <td className="px-6 py-4 text-right">
                      {lead.status !== 'human_handoff' && (
                        <button
                          onClick={() => handleHandoff(lead.id)}
                          className="text-xs font-medium text-primary-600 hover:text-primary-700"
                        >
                          Hand off
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing {data.leads.length} of {data.total}
            </p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40"
              >
                Prev
              </button>
              <span className="px-3 py-1.5 text-sm text-gray-600">
                {page} / {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
