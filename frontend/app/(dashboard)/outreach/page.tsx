'use client';

import { useState } from 'react';
import { api } from '../../../lib/api';
import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState, StatCard, formatDate } from '../../../components/ui';
import type { LeadListResponse, Lead } from '../../../lib/types';

export default function OutreachPage() {
  const { data, loading, error, refetch } = useApi<LeadListResponse>(
    '/leads?page=1&page_size=50'
  );
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Leads that have not yet been handed off and have had at least one outreach
  const candidates: Lead[] =
    data?.leads.filter(
      (l) =>
        l.status !== 'human_handoff' &&
        l.status !== 'closed_won' &&
        l.status !== 'closed_lost' &&
        l.status !== 'disqualified'
    ) ?? [];

  const handoffs: Lead[] =
    data?.leads.filter((l) => l.status === 'human_handoff') ?? [];

  async function run(action: 'check_reply', lead: Lead, hasReply = false) {
    setBusy(lead.id);
    setNotice(null);
    try {
      const res = await api.post<unknown>(`/outreach/${action}`, {
        lead_id: lead.id,
        has_reply: hasReply,
      });
      if (hasReply) {
        setNotice(`Reply detected on ${lead.id.slice(0, 8)}. Human handoff created and automated outreach LOCKED.`);
      } else {
        setNotice('Reply check complete. No reply detected — automation continues.');
      }
      refetch();
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Operation failed';
      try {
        const parsed = JSON.parse(msg);
        setNotice(parsed.message || msg);
      } catch {
        setNotice(msg);
      }
      refetch();
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Outreach"
        description="Automated first-touch sequences. The moment a prospect replies, the system locks automation and hands off to you."
      />

      {notice && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-4 text-sm">
          {notice}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard label="Active Outreach" value={candidates.length} />
        <StatCard label="Human Handoffs" value={handoffs.length} accent="text-purple-600" />
        <StatCard label="Total Leads" value={data?.total ?? 0} />
      </div>

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : candidates.length === 0 ? (
        <EmptyState title="No leads in active outreach" description="Generate and send outreach from the pipeline, or wait for the hunting agent to source leads." />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lead</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Outreach</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Check Reply</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {candidates.map((lead: Lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{lead.id.slice(0, 8)}</td>
                  <td className="px-6 py-4">
                    <Badge color={statusColor(lead.status)}>{lead.status.replace(/_/g, ' ')}</Badge>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{lead.outreach_count}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{lead.lead_score.toFixed(1)}</td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => run('check_reply', lead, true)}
                      disabled={busy === lead.id}
                      className="px-3 py-1 text-xs font-medium rounded-md bg-purple-100 text-purple-800 hover:bg-purple-200 disabled:opacity-40"
                    >
                      {busy === lead.id ? 'Checking...' : 'Simulate reply → handoff'}
                    </button>
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
