'use client';

import { useApi } from '../../../lib/useApi';
import {
  PageHeader,
  LoadingState,
  EmptyState,
  ErrorState,
  formatDate,
} from '../../../components/ui';
import type { Company } from '../../../lib/types';

export default function CompaniesPage() {
  const { data: companies, loading, error } = useApi<Company[]>('/companies');

  return (
    <div>
      <PageHeader
        title="Companies"
        description="Accounts targeted by the outbound hunting funnel."
      />

      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : !companies || companies.length === 0 ? (
        <EmptyState
          title="No companies yet"
          description="Companies appear here as leads are discovered and enriched."
        />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Domain
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Industry
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Added
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {companies.map((c: Company) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{c.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {c.website ? (
                      <a
                        href={c.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700"
                      >
                        {c.domain || c.website}
                      </a>
                    ) : (
                      c.domain || '—'
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{c.industry || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{c.location || '—'}</td>
                  <td className="px-6 py-4 text-right text-sm text-gray-500">
                    {formatDate(c.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
