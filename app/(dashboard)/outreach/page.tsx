import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function OutreachPage() {
  const [outreach, setOutreach] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate fetching outreach messages
    setTimeout(() => {
      setOutreach([
        {
          id: '1',
          subject: 'Welcome to our platform',
          recipient: 'acme@company.com',
          channel: 'email',
          status: 'sent',
          message: 'Thank you for joining our platform!',
          sent_at: new Date().toISOString(),
        },
        {
          id: '2',
          subject: 'Your proposal is ready',
          recipient: 'beta@startup.com',
          channel: 'email',
          status: 'sent',
          message: 'Here is your customized proposal.',
          sent_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading outreach...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Outreach</h1>
      <p className="text-gray-600 mb-6">Manage your outreach efforts and track messages</p>
      
      <div className="space-y-4">
        {outreach.map(outreachItem => (
          <div key={outreachItem.id} className="border-b border-gray-200 pb-4">
            <div className="flex items-center gap-4">
              <span className="w-12 h-12 rounded-full bg-cyan-100 text-cyan-700 flex items-center justify-center text-xs font-bold">
                {outreachItem.channel}
              </span>
              <div>
                <h3 className="font-semibold">{outreachItem.subject}</h3>
                <p className="text-sm text-gray-600">Sent to {outreachItem.recipient}</p>
                <span className="text-xs text-gray-500">{formatDate(outreachItem.sent_at)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
