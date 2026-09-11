'use client';

import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  StatCard,
  Badge,
  statusColor,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../../components/ui';
import type {
  MarketingListResponse,
  MarketingPerformance,
} from '../../../lib/types';

export default function MarketingPage() {
  const { data, loading, error } = useApi<MarketingListResponse>(
    '/marketing?page=1&page_size=50'
  );
  const { data: perf } = useApi<MarketingPerformance>('/marketing/performance');

  const activities = data?.activities ?? [];

  return (
    <div>
      <PageHeader
        title="Marketing"
        description="Content, paid traffic, social, and SEO activity across the organization."
      />

      {error && <ErrorState message={error} />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard label="Total Views" value={perf?.total_views ?? 0} />
        <StatCard label="Total Clicks" value={perf?.total_clicks ?? 0} />
        <StatCard label="Leads Attributed" value={perf?.total_leads_attributed ?? 0} />
        <StatCard
          label="Total Spend"
          value={`$${(perf?.total_spend ?? 0).toLocaleString()}`}
        />
        <StatCard label="Click Rate" value={`${perf?.click_rate ?? 0}%`} />
        <StatCard label="Cost per Lead" value={`$${perf?.cost_per_lead ?? 0}`} />
        <StatCard label="Activities" value={perf?.activity_count ?? 0} />
      </div>

      {loading ? (
        <LoadingState />
      ) : activities.length === 0 ? (
        <EmptyState
          title="No marketing activity yet"
          description="Approved marketing output will appear here."
        />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Views
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Clicks
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Leads
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {activities.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {a.title || '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {a.agent_type.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{a.platform || '—'}</td>
                  <td className="px-6 py-4">
                    <Badge color={statusColor(a.status || '')}>
                      {(a.status || 'draft').replace(/_/g, ' ')}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-right text-sm text-gray-600">{a.views}</td>
                  <td className="px-6 py-4 text-right text-sm text-gray-600">{a.clicks}</td>
                  <td className="px-6 py-4 text-right text-sm text-gray-600">
                    {a.leads_attributed}
                  </td>
                  <td className="px-6 py-4 text-right text-sm text-gray-500">
                    {formatDate(a.created_at)}
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
