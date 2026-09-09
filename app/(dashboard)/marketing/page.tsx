import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function MarketingPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate fetching campaigns
    setTimeout(() => {
      setCampaigns([
        {
          id: '1',
          name: 'Summer Campaign',
          channel: 'email',
          status: 'running',
          budget: 5000,
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: '2',
          name: 'Q4 Lead Gen',
          channel: 'linkedin',
          status: 'planned',
          budget: 3000,
          created_at: new Date(Date.now() - 172800000).toISOString(),
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading marketing...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Marketing</h1>
      <p className="text-gray-600 mb-6">Manage your marketing initiatives and campaigns</p>
      
      <div className="space-y-4">
        {campaigns.map(campaign => (
          <div key={campaign.id} className="border-b border-gray-200 pb-4">
            <div className="flex items-center gap-4">
              <span className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
                {campaign.name.charAt(0)}
              </span>
              <div>
                <h3 className="font-semibold">{campaign.name}</h3>
                <p className="text-sm text-gray-600">{campaign.channel}</p>
                <span className="text-xs text-gray-500">{campaign.status}</span>
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Budget: ${campaign.budget}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
