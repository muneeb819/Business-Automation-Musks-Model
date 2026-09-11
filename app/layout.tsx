import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Business Development Platform',
  description: 'AI-powered Business Development Operating System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
