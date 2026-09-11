'use client';

import { useCallback, useState } from 'react';
import { api } from '../../../lib/api';
import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  Badge,
  statusColor,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../../components/ui';
import type { Approval, ApprovalListResponse } from '../../../lib/types';

export default function ApprovalsPage() {
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const { data, loading, error, refetch } = useApi<ApprovalListResponse>(
    `/approvals?page=${page}&page_size=20`,
    [page]
  );
  const approvals = data?.approvals ?? [];
  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  const takeAction = useCallback(
    async (approval: Approval, action: 'approve' | 'reject') => {
      setBusy(approval.id);
      setNotice(null);
      try {
        await api.post(`/approvals/${approval.id}/action`, { action });
        setNotice(
          action === 'approve'
            ? `"${approval.title}" approved.`
            : `"${approval.title}" rejected.`
        );
        refetch();
      } catch (e) {
        setNotice(e instanceof Error ? e.message : 'Action failed');
      } finally {
        setBusy(null);
      }
    },
    [refetch]
  );

  return (
    <div>
      <PageHeader
        title="Approvals"
        description="Changes proposed by AI agents that require human sign-off."
      />

      {notice && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-4 text-sm">
          {notice}
        </div>
      )}
      {error && <ErrorState message={error} />}

      {loading ? (
        <LoadingState />
      ) : approvals.length === 0 ? (
        <EmptyState
          title="No approvals pending"
          description="Agent-proposed changes will appear here for review."
        />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow divide-y divide-gray-100">
            {approvals.map((approval) => (
              <div key={approval.id} className="p-5 flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-semibold text-gray-900">{approval.title}</h3>
                    <Badge color={statusColor(approval.status)}>{approval.status}</Badge>
                    <Badge color="gray">{approval.category.replace(/_/g, ' ')}</Badge>
                    {approval.risk_level && (
                      <Badge color={approval.risk_level === 'high' ? 'red' : 'yellow'}>
                        {approval.risk_level} risk
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{approval.description}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    Proposed: {approval.proposed_fix}
                  </p>
                  <p className="text-xs text-gray-400 mt-2">{formatDate(approval.created_at)}</p>
                </div>
                {approval.status === 'pending' && (
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => takeAction(approval, 'approve')}
                      disabled={busy === approval.id}
                      className="px-3 py-1.5 text-xs font-medium rounded-md bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => takeAction(approval, 'reject')}
                      disabled={busy === approval.id}
                      className="px-3 py-1.5 text-xs font-medium rounded-md border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing {approvals.length} of {data?.total ?? 0}
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
