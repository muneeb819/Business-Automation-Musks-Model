import { redirect } from 'next/navigation';

export default function OverviewPage() {
  // The dashboard home (`/`) is the canonical overview. Redirect any
  // legacy `/overview` links there instead of rendering duplicate/mock data.
  redirect('/');
}
