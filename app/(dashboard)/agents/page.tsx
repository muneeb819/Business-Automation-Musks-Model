import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function AgentsPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simulate fetching agents
    setTimeout(() => {
      setAgents([
        {
          id: '1',
          name: 'Alex Morgan',
          role: 'Senior Outreach Specialist',
          status: 'active',
          last_run: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: '2',
          name: 'Taylor Kim',
          role: 'Content Creator',
          status: 'active',
          last_run: new Date(Date.now() - 43200000).toISOString(),
        },
        {
          id: '3',
          name: 'Jordan Lee',
          role: 'Paid Traffic Manager',
          status: 'active',
          last_run: new Date(Date.now() - 21600000).toISOString(),
        },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div className="text-center py-8">Loading agents...</div>;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Agents</h1>
      <p className="text-gray-600 mb-6">Manage your team of AI-powered agents</p>
      
      <div className="space-y-4">
        {agents.map(agent => (
          <div key={agent.id} className="border-b border-gray-200 pb-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                {agent.name.charAt(0)}
              </div>
              <div>
                <h3 className="font-semibold">{agent.name}</h3>
                <p className="text-sm text-gray-600">{agent.role}</p>
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {agent.status}
                </span>
              </div>
            </div>
            <div className="mt-2 text-sm text-gray-500">
              Last run: {formatDate(agent.last_run)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
