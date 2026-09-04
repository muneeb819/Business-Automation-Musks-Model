'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { clearTokens } from '../lib/api';
import {
  LayoutDashboard,
  Users,
  Building2,
  CreditCard,
  PhoneCall,
  MessagesSquare,
  Megaphone,
  Bot,
  Activity,
  Workflow,
  BarChart3,
  CheckSquare,
  Database,
  Plug,
  Bell,
  ScrollText,
  Building,
  Settings,
  LogOut,
  type LucideIcon,
} from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  section?: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Overview', href: '/', icon: LayoutDashboard },
  { label: 'Leads', href: '/leads', icon: Users },
  { label: 'Companies', href: '/companies', icon: Building2 },
  { label: 'Pipeline', href: '/pipeline', icon: CreditCard },
  {
    label: 'Outreach',
    href: '/outreach',
    icon: PhoneCall,
    section: 'Operations',
  },
  { label: 'Conversations', href: '/conversations', icon: MessagesSquare },
  { label: 'Marketing', href: '/marketing', icon: Megaphone },
  {
    label: 'Agents',
    href: '/agents',
    icon: Bot,
    section: 'AI',
  },
  { label: 'Agent Health', href: '/agents', icon: Activity },
  { label: 'Workflows', href: '/workflows', icon: Workflow },
  { label: 'Analytics', href: '/analytics', icon: BarChart3 },
  {
    label: 'Approvals',
    href: '/approvals',
    icon: CheckSquare,
    section: 'Management',
  },
  { label: 'Knowledge', href: '/knowledge', icon: Database },
  { label: 'Integrations', href: '/integrations', icon: Plug },
  { label: 'Notifications', href: '/notifications', icon: Bell },
  { label: 'Audit Logs', href: '/audit-logs', icon: ScrollText },
  {
    label: 'Organization',
    href: '/organization',
    icon: Building,
    section: 'System',
  },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearTokens();
    router.push('/login');
  }

  const sections: { title: string | null; items: NavItem[] }[] = [];
  let current: NavItem[] = [];
  for (const item of NAV_ITEMS) {
    if (item.section) {
      if (current.length) {
        sections.push({ title: null, items: current });
        current = [];
      }
      sections.push({ title: item.section, items: [] });
      current.push(item);
    } else {
      current.push(item);
    }
  }
  if (current.length) {
    sections.push({ title: null, items: current });
  }

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-4 flex flex-col">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-gray-900">AI BD Platform</h1>
        <p className="text-sm text-gray-500">Business Development OS</p>
      </div>
      <nav className="space-y-1 flex-1 overflow-y-auto">
        {sections.map((section, i) => (
          <div key={i}>
            {section.title && (
              <p className="px-3 pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                {section.title}
              </p>
            )}
            {section.items.map((item) => {
              const active =
                item.href === '/'
                  ? pathname === '/'
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md ${
                    active
                      ? 'text-gray-900 bg-gray-100'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="pt-4 border-t border-gray-100">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-50"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
