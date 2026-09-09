import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function LeadManagementPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate fetching leads
    setTimeout(() => {
      setLeads([
        {
          id: '1',
          company: 'Acme Corp',
          contact: 'John Doe',
          source: 'web',
          status: 'lead',
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: '2',
          company: 'Beta Inc',
          contact: 'Sarah Smith',
          source: 'linkedin',
          status: 'lead',
          created_at: new Date(Date.now() - 172800000).toISOString(),
        },
        {
          id: '3',
          company: 'Gamma LLC',
          contact: 'Mike Johnson',
          source: 'referral',
          status: 'lead',
          created_at: new Date(Date.now() - 345600000).toISOString(),
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading leads...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Lead Management</h1>
      <p className="text-gray-600 mb-6">Manage your leads and opportunities</p>
      
      <div className="space-y-4">
        {leads.map(lead => (
          <div key={lead.id} className="border-b border-gray-200 pb-4">
            <div className="flex items-center gap-4">
              <span className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold">
                {lead.company}
              </span>
              <div>
                <h3 className="font-semibold">{lead.company}</h3>
                <p className="text-sm text-gray-600">{lead.contact}</p>
                <span className="text-xs text-gray-500">{lead.source}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
