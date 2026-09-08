'use client';

import { useState } from 'react';
import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  Badge,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../../components/ui';
import { api } from '../../../lib/api';
import type { Notification, NotificationListResponse } from '../../../lib/types';

const TYPE_LABELS: Record<string, string> = {
  ready_to_close: 'Ready to Close',
  approval_needed: 'Approval Needed',
  system_issue: 'System Issue',
  human_handoff: 'Human Handoff',
  new_reply: 'New Reply',
  agent_failure: 'Agent Failure',
  strategy_recommendation: 'Strategy Recommendation',
};

export default function NotificationsPage() {
  const { data, loading, error, refetch } = useApi<NotificationListResponse>('/notifications?page=1&page_size=50');
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const notifications = data?.notifications ?? [];

  async function markRead(n: Notification) {
    setBusy(n.id);
    try {
      await api.post(`/notifications/${n.id}/read`);
      refetch();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Failed to mark as read');
    } finally {
      setBusy(null);
    }
  }

  async function markAllRead() {
    setBusy('all');
    try {
      await api.post('/notifications/read-all');
      setNotice('All notifications marked as read.');
      refetch();
    } catch (e) {
      setNotice(e instanceof Error ? e.message : 'Failed to mark notifications');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Notifications"
        description="Alerts from agents and the platform."
      >
        {notifications.length > 0 && (
          <button
            onClick={markAllRead}
            disabled={busy === 'all'}
            className="px-4 py-2 text-sm font-medium rounded-md bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {busy === 'all' ? 'Marking...' : 'Mark all read'}
          </button>
        )}
      </PageHeader>

      {notice && (
        <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-4 text-sm">
          {notice}
        </div>
      )}

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : notifications.length === 0 ? (
        <EmptyState
          title={data && data.unread > 0 ? 'No matching notifications' : 'No notifications'}
          description="Agent and platform alerts will appear here."
        />
      ) : (
        <div className="bg-white rounded-lg shadow divide-y divide-gray-100">
          {notifications.map((n) => (
            <div key={n.id} className="p-5 flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div
                  className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${
                    n.is_read ? 'bg-gray-200' : 'bg-primary-500'
                  }`}
                />
                <div>
                  <div className="flex items-center gap-2">
                    <p className={`text-sm font-medium ${n.is_read ? 'text-gray-600' : 'text-gray-900'}`}>
                      {n.title}
                    </p>
                    <Badge color="gray">
                      {TYPE_LABELS[n.type] || n.type.replace(/_/g, ' ')}
                    </Badge>
                    {n.channel && n.channel !== 'dashboard' && (
                      <Badge color="blue">{n.channel}</Badge>
                    )}
                  </div>
                  {n.message && (
                    <p className="text-sm text-gray-500 mt-1">{n.message}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDate(n.sent_at)}
                  </p>
                </div>
              </div>
              {!n.is_read && (
                <button
                  onClick={() => markRead(n)}
                  disabled={busy === n.id}
                  className="shrink-0 px-3 py-1 text-xs font-medium rounded-md bg-primary-50 text-primary-700 hover:bg-primary-100 disabled:opacity-40"
                >
                  {busy === n.id ? '...' : 'Mark read'}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}