import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate fetching approvals
    setTimeout(() => {
      setApprovals([
        {
          id: '1',
          title: 'Lead 001 - Acme Corp',
          status: 'pending',
          description: 'Review lead quality and approval',
          risk_level: 'medium',
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: '2',
          title: 'Lead 002 - Beta Inc',
          status: 'approved',
          description: 'Ready for outreach',
          risk_level: 'low',
          created_at: new Date(Date.now() - 7200000).toISOString(),
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading approvals...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Approvals</h1>
      <p className="text-gray-600 mb-6">Manage lead approvals and workflow decisions</p>
      
      <div className="space-y-4">
        {approvals.map(approval => (
          <div key={approval.id} className="border-b border-gray-200 pb-4">
            <div className="flex items-center gap-4">
              <span className="w-12 h-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center text-xs font-bold">
                {approval.risk_level}
              </span>
              <div>
                <h3 className="font-semibold">{approval.title}</h3>
                <p className="text-sm text-gray-600">{approval.description}</p>
                <span className="text-xs text-gray-500">{approval.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
