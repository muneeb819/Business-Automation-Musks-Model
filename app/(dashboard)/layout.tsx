'use client';

import Sidebar from '../../components/Sidebar';
import { usePathname } from 'next/navigation';
import { AlertTriangle, Database, Plug, RefreshCw } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const pageTitles: Record<string, string> = {
    '/': 'Dashboard Overview',
    '/leads': 'Leads',
    '/companies': 'Companies',
    '/pipeline': 'Pipeline',
    '/outreach': 'Outreach',
    '/conversations': 'Conversations',
    '/marketing': 'Marketing',
    '/agents': 'Agents',
    '/workflows': 'Workflows',
    '/analytics': 'Analytics',
    '/approvals': 'Approvals',
    '/knowledge': 'Knowledge',
    '/integrations': 'Integrations',
    '/notifications': 'Notifications',
    '/audit-logs': 'Audit Logs',
    '/organization': 'Organization',
    '/settings': 'Settings',
  };
  const title = pageTitles[pathname] || 'AI Business Development Platform';

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="flex">
        <Sidebar />
        <div className="flex-1 min-w-0">
          <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10">
            <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span className="hidden md:flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-yellow-400" />
                Demo mode
              </span>
            </div>
          </header>
          <div className="p-8">{children}</div>
        </div>
      </div>
    </main>
  );
}
