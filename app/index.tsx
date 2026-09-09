import { Navigate, Link } from 'react-router-dom';
import { OrganizationPage } from '../organization/page';
import { NotificationsPage } from '../notifications/page';
import { OverviewPage } from '../overview/page';
import { AgentsPage } from '../agents/page';
import { PipelinePage } from '../pipeline/page';
import { MarketingPage } from '../marketing/page';
import { ApprovalsPage } from '../approvals/page';
import { OutreachPage } from '../outreach/page';
import { LeadManagementPage } from '../lead-management/page';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-indigo-600">BDOS</Link>
          <div className="space-x-6">
            <Link to="/organization" className="text-gray-600 hover:text-indigo-600">Organization</Link>
            <Link to="/notifications" className="text-gray-600 hover:text-indigo-600">Notifications</Link>
            <Link to="/overview" className="text-gray-600 hover:text-indigo-600">Overview</Link>
            <Link to="/agents" className="text-gray-600 hover:text-indigo-600">Agents</Link>
            <Link to="/pipeline" className="text-gray-600 hover:text-indigo-600">Pipeline</Link>
            <Link to="/marketing" className="text-gray-600 hover:text-indigo-600">Marketing</Link>
            <Link to="/approvals" className="text-gray-600 hover:text-indigo-600">Approvals</Link>
            <Link to="/outreach" className="text-gray-600 hover:text-indigo-600">Outreach</Link>
            <Link to="/lead-management" className="text-gray-600 hover:text-indigo-600">Lead Mgmt</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Dashboard */}
        <section id="dashboard" className="mb-8">
          <h1 className="text-2xl font-bold mb-4">BDOS Dashboard</h1>
          <p className="text-gray-600">Organization overview and notification feed</p>
        </section>
        
        {/* Page components */}
        <OrganizationPage />
        <NotificationsPage />
        <OverviewPage />
        <AgentsPage />
        <PipelinePage />
        <MarketingPage />
        <ApprovalsPage />
        <OutreachPage />
        <LeadManagementPage />
      </main>
    </div>
  );
}
