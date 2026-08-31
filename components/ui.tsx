'use client';

import clsx from 'clsx';

export function StatCard({
  label,
  value,
  hint,
  accent = 'text-gray-900',
}: {
  label: string;
  value: number | string;
  hint?: string;
  accent?: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className={clsx('text-3xl font-bold', accent)}>{value}</p>
      {hint && <p className="text-sm text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}

export function PageHeader({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="mb-8 flex items-start justify-between">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {description && <p className="text-gray-500">{description}</p>}
      </div>
      {children}
    </div>
  );
}

const badgeStyles: Record<string, string> = {
  green: 'bg-green-100 text-green-800',
  red: 'bg-red-100 text-red-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  blue: 'bg-blue-100 text-blue-800',
  gray: 'bg-gray-100 text-gray-700',
  purple: 'bg-purple-100 text-purple-800',
};

export function Badge({
  children,
  color = 'gray',
}: {
  children: React.ReactNode;
  color?: keyof typeof badgeStyles;
}) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        badgeStyles[color]
      )}
    >
      {children}
    </span>
  );
}

export function statusColor(status: string): keyof typeof badgeStyles {
  switch (status) {
    case 'active':
    case 'approved':
    case 'completed':
    case 'closed_won':
    case 'engaged':
    case 'ready_to_close':
      return 'green';
    case 'failed':
    case 'rejected':
    case 'closed_lost':
    case 'disqualified':
      return 'red';
    case 'pending':
    case 'executing':
    case 'new':
    case 'contacted':
      return 'yellow';
    case 'human_handoff':
    case 'maintenance':
      return 'purple';
    default:
      return 'gray';
  }
}

export function LoadingState({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="text-center py-16 text-gray-500">
      <p>{label}</p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="text-center py-16 text-gray-500">
      <p className="font-medium text-gray-600">{title}</p>
      {description && <p className="text-sm mt-1">{description}</p>}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
      {message}
    </div>
  );
}

export function formatDate(value?: string | null): string {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
