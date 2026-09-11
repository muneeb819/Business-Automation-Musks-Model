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
import type { Lead, LeadListResponse } from '../../../lib/types';

const OUTREACHABLE = new Set(['new', 'contacted', 'engaged', 'ready_to_close']);

export default function OutreachPage() {
  const { data, loading, error, refetch } = useApi<LeadListResponse>(
    '/leads?page=1&page_size=100'
  );
  const leads = (data?.leads ?? []).filter((l) => OUTREACHABLE.has(l.status));

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [channel, setChannel] = useState('email');
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const selected = leads.find((l) => l.id === selectedId) ?? null;

  const generateProposal = useCallback(async () => {
    if (!selected) return;
    setBusy('proposal');
    setNotice(null);
    try {
      const res = await api.post<{ proposal?: string; message?: string }>(
        '/outreach/generate-proposal',
        { lead_id: selected.id }
      );
      setMessage(res.proposal ?? res.message ?? '');
      setNotice('Proposal generated. Review before sending.');
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Failed to generate proposal');
    } finally {
      setBusy(null);
    }
  }, [selected]);

  const sendOutreach = useCallback(async () => {
    if (!selected || !message.trim()) {
      setNotice('Write a message before sending.');
      return;
    }
    setBusy('send');
    setNotice(null);
    try {
      await api.post('/outreach/send', {
        lead_id: selected.id,
        content: message.trim(),
        channel,
      });
      setMessage('');
      setNotice(`Outreach sent via ${channel}.`);
      refetch();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Failed to send outreach');
    } finally {
      setBusy(null);
    }
  }, [selected, message, channel, refetch]);

  const markReplied = useCallback(async () => {
    if (!selected) return;
    setBusy('reply');
    setNotice(null);
    try {
      await api.post('/outreach/check-reply', {
        lead_id: selected.id,
        has_reply: true,
        channel,
      });
      setSelectedId(null);
      setNotice('Reply recorded — automated outreach locked, human handoff created.');
      refetch();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Failed to record reply');
    } finally {
      setBusy(null);
    }
  }, [selected, channel, refetch]);

  return (
    <div>
      <PageHeader
        title="Outreach"
        description="Send personalized outreach. The moment a prospect replies, automation locks and a human takes over."
      />

      {notice && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-4 text-sm">
          {notice}
        </div>
      )}
      {error && <ErrorState message={error} />}

      {loading ? (
        <LoadingState />
      ) : leads.length === 0 ? (
        <EmptyState
          title="No leads ready for outreach"
          description="New and contacted leads appear here once hunting begins."
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900">
                Outreachable leads ({leads.length})
              </h3>
            </div>
            <div className="divide-y divide-gray-100 max-h-[32rem] overflow-y-auto">
              {leads.map((lead: Lead) => (
                <button
                  key={lead.id}
                  onClick={() => {
                    setSelectedId(lead.id);
                    setNotice(null);
                  }}
                  className={`w-full text-left px-6 py-4 hover:bg-gray-50 flex items-center justify-between ${
                    selectedId === lead.id ? 'bg-primary-50' : ''
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">
                        {lead.source.replace(/_/g, ' ')}
                      </span>
                      <Badge color={statusColor(lead.status)}>{lead.status}</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Score {lead.lead_score.toFixed(0)} · {lead.outreach_count} sent ·{' '}
                      {formatDate(lead.created_at)}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            {!selected ? (
              <p className="text-sm text-gray-500 py-16 text-center">
                Select a lead to compose outreach.
              </p>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900">
                    Lead · {selected.source.replace(/_/g, ' ')}
                  </h3>
                  <Badge color={statusColor(selected.status)}>{selected.status}</Badge>
                </div>

                <div className="flex gap-2">
                  <label className="text-sm text-gray-600 self-center">Channel</label>
                  <select
                    value={channel}
                    onChange={(e) => setChannel(e.target.value)}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="email">Email</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="phone">Phone</option>
                  </select>
                </div>

                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={8}
                  placeholder="Write a personalized message…"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />

                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={generateProposal}
                    disabled={busy === 'proposal'}
                    className="px-4 py-2 text-sm font-medium rounded-md border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    {busy === 'proposal' ? 'Generating…' : 'Generate proposal'}
                  </button>
                  <button
                    onClick={sendOutreach}
                    disabled={busy === 'send' || !message.trim()}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
                  >
                    {busy === 'send' ? 'Sending…' : 'Send outreach'}
                  </button>
                  <button
                    onClick={markReplied}
                    disabled={busy === 'reply'}
                    className="px-4 py-2 text-sm font-medium rounded-md border border-amber-300 text-amber-700 hover:bg-amber-50 disabled:opacity-50"
                  >
                    {busy === 'reply' ? 'Recording…' : 'Mark as replied (handoff)'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
