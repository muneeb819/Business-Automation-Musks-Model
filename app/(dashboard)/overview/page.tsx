import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function OverviewPage() {
  const [notifications, setNotifications] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);

  // Simulate fetching notifications
  useEffect(() => {
    // In a real app, this would call the API
    setTimeout(() => {
      setNotifications([
        {
          id: '1',
          type: 'ready_to_close',
          reference_type: 'lead_123',
          title: 'New Lead - Acme Corp',
          message: 'Contacted for consulting services',
          channel: 'email',
          is_read: false,
          sent_at: new Date(Date.now() - 3600 * 1000).toISOString(),
        },
        {
          id: '2',
          type: 'human_handoff',
          reference_type: 'lead_456',
          title: 'Follow-up with TechCo',
          message: 'Technical consultation scheduled',
          channel: 'phone',
          is_read: true,
          sent_at: new Date().toISOString(),
        },
      ]);
      setUnread(notifications.filter(n => !n.is_read).length);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading overview...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Overview</h1>
      <p className="text-gray-600 mb-6">
        This is the BDOS dashboard overview. You can manage your organisation, monitor notifications,
        and oversee all business development activities.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Organisation</h3>
          <p className="text-gray-600">Default Organization</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Notifications</h3>
          <p className="text-gray-600">3 total (1 unread)</p>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Active Members</h3>
          <p className="text-gray-600">11 members</p>
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Recent Notifications</h2>
        {notifications.map(n => (
          <div key={n.id} className="border-b border-gray-200 pt-4 mb-3">
            <div className="flex items-center gap-3">
              <span className={`px-2 py-1 rounded text-xs font-medium ${n.is_read ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                {n.is_read ? 'Read' : 'Unread'}
              </span>
              <span className="text-sm">{n.title}</span>
              {n.channel && <span className="text-xs text-gray-500 ml-2">{n.channel}</span>}
            </div>
            <p className="text-sm text-gray-600">{n.message}</p>
            {n.type && <span className="text-xs text-gray-400 ml-2">{n.type}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
