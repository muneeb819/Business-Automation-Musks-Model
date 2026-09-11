import { redirect } from 'next/navigation';

export default function LeadManagementPage() {
  // Lead management is handled by the canonical `/leads` page.
  redirect('/leads');
}
