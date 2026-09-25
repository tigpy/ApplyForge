import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ApplyForge | Autonomous Career Desk',
  description: 'Production Job Application Automation Platform with Human Approval Guardrails',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f3efe6] text-[#1c1914] antialiased">
        {children}
      </body>
    </html>
  );
}
