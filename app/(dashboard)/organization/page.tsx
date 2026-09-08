'use client';

import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  Badge,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../../components/ui';
import type { Organization } from '../../../lib/types';

export default function OrganizationPage() {
  const { data: org, loading, error } = useApi<Organization>('/organization');

  return (
    <div>
      <PageHeader
        title="Organization"
        description="Tenant, membership, and role administration."
      />

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !org ? (
        <EmptyState title="No organization" description="You are not part of an organization yet." />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{org.name}</h2>
                {org.slug && (
                  <p className="text-sm text-gray-500">@ {org.slug}</p>
                )}
              </div>
              <Badge color="green">{org.members.length} members</Badge>
            </div>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {org.description && (
                <div>
                  <dt className="text-gray-500">Description</dt>
                  <dd className="text-gray-900">{org.description}</dd>
                </div>
              )}
              {org.industry && (
                <div>
                  <dt className="text-gray-500">Industry</dt>
                  <dd className="text-gray-900">{org.industry}</dd>
                </div>
              )}
              {org.website && (
                <div>
                  <dt className="text-gray-500">Website</dt>
                  <dd className="text-gray-900">{org.website}</dd>
                </div>
              )}
              {org.created_at && (
                <div>
                  <dt className="text-gray-500">Created</dt>
                  <dd className="text-gray-900">{formatDate(org.created_at)}</dd>
                </div>
              )}
            </dl>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Members</h3>
            </div>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {org.members.map((m) => (
                  <tr key={m.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {m.full_name || '—'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{m.email}</td>
                    <td className="px-6 py-4">
                      <Badge color={m.role === 'owner' ? 'purple' : 'gray'}>{m.role}</Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {m.is_active ? 'Active' : 'Inactive'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}