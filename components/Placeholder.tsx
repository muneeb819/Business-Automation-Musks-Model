'use client';

import { PageHeader } from './ui';

export default function Placeholder({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div>
      <PageHeader title={title} description={description} />
      <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500 border-2 border-dashed border-gray-200">
        <p className="font-medium text-gray-600">Module under construction</p>
        <p className="text-sm mt-1">
          This view will be populated when the corresponding backend integration is
          wired to a live data source.
        </p>
      </div>
    </div>
  );
}
