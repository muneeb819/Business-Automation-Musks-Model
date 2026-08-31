'use client';

import { useApi } from '../../../lib/useApi';
import { PageHeader, Badge, statusColor, LoadingState, EmptyState, ErrorState, StatCard, formatDate } from '../../../components/ui';

interface MarketingPerf {
  total_views: number;
  total_clicks: number;
  total_leads_attributed: number;
  total_spend: number;
  click_rate: number;
  cost_per_lead: number;
  activity_count: number;
}

interface MarketingActivity {
  id: string;
  agent_type: string;
  platform: string;
  content_type: string;
  title: string;
  views: number;
  engagement_rate: number;
  clicks: number;
  leads_attributed: number;
  spend: number;
  status: string;
  created_at: string;
}

interface MarketingList {
  activities: MarketingActivity[];
  total: number;
  page: number;
  page_size: number;
}

export default function MarketingPage() {
  const { data: perf } = useApi<MarketingPerf>('/marketing/performance');
  const { data: list } = useApi<MarketingList>('/marketing');

  return (
    <div>
      <PageHeader
        title="Marketing"
        description="Inbound funnel performance across content, social, SEO, and paid campaigns."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard label="Total Views" value={perf?.total_views ?? 0} />
        <StatCard label="Total Clicks" value={perf?.total_clicks ?? 0} />
        <StatCard label="Leads Attributed" value={perf?.total_leads_attributed ?? 0} />
        <StatCard label="Total Spend" value={perf ? `$${perf.total_spend}` : 0} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-500">Click Rate</p>
          <p className="text-3xl font-bold text-gray-900">{perf?.click_rate ?? 0}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-500">Cost per Lead</p>
          <p className="text-3xl font-bold text-gray-900">
            {perf ? `$${perf.cost_per_lead}` : 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-500">Activities</p>
          <p className="text-3xl font-bold text-gray-900">{perf?.activity_count ?? 0}</p>
        </div>
      </div>

      {!list || (list && list.activities.length === 0) ? (
        <EmptyState title="No marketing activity" description="Marketing agents will publish content and campaigns here." />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Platform</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Views</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Leads</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {list.activities.map((a: MarketingActivity) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{a.title}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{a.platform}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{a.views ?? 0}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{a.leads_attributed ?? 0}</td>
                  <td className="px-6 py-4"><Badge color={statusColor(a.status)}>{a.status}</Badge></td>
                  <td className="px-6 py-4 text-sm text-gray-500">{formatDate(a.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
