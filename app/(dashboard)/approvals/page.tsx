'use client';

import { useState } from 'react';
import { api } from '../../../lib/api';
import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState, formatDate } from '../../../components/ui';
import type { Approval, ApprovalListResponse } from '../../../lib/types';

export default function ApprovalsPage() {
  const [page, setPage] = useState(1);
  const { data, loading, error, refetch } = useApi<ApprovalListResponse>(
    `/approvals?page=${page}&page_size=${20}`
  );

  const [acting, setActing] = useState<string | null>(null);

  async function act(id: string, action: 'approve' | 'reject') {
    setActing(id);
    try {
      await api.post(`/approvals/${id}/action`, { action });
      refetch();
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Action failed');
    } finally {
      setActing(null);
    }
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div>
      <PageHeader
        title="Approvals"
        description="Every system change proposed by an agent requires a human decision."
      />

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !data || data.approvals.length === 0 ? (
        <EmptyState
          title="No approvals"
          description="When an agent proposes a configuration change, it will appear here for your review."
        />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {data.approvals.map((a: Approval) => (
                  <tr key={a.id} className="hover:bg-gray-50 align-top">
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900">{a.title}</p>
                      <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">{a.description}</p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{a.category.replace(/_/g, ' ')}</td>
                    <td className="px-6 py-4">
                      <Badge color={
                        a.risk_level === 'high' ? 'red' : a.risk_level === 'medium' ? 'yellow' : 'green'
                      }>
                        {a.risk_level}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <Badge color={statusColor(a.status)}>{a.status}</Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{formatDate(a.created_at)}</td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      {a.status === 'pending' ? (
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={() => act(a.id, 'approve')}
                            disabled={acting === a.id}
                            className="px-3 py-1 text-xs font-medium rounded-md bg-green-100 text-green-800 hover:bg-green-200 disabled:opacity-40"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => act(a.id, 'reject')}
                            disabled={acting === a.id}
                            className="px-3 py-1 text-xs font-medium rounded-md bg-red-100 text-red-800 hover:bg-red-200 disabled:opacity-40"
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Resolved</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">Total: {data.total}</p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-3 py-1.5 text-sm font-medium rounded-md border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-40"
              >
                Prev
              </button>
              <span className="px-3 py-1.5 text-sm text-gray-600">{page} / {totalPages}</span>
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
