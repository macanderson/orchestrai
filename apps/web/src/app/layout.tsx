import { TenantProvider } from '@/providers/TenantProvider';
import '@/styles/globals.css';
import { Theme, ThemePanel } from '@radix-ui/themes';
import { Metadata } from 'next';
import { cookies } from 'next/headers';
import React from 'react';
import { Toaster } from 'react-hot-toast';

export const metadata: Metadata = {
  title: 'OrchestrAI - AI-powered agents for your business',
  description: 'AI-powered agent generation for your business',
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const tenantId = cookieStore.get('X-Tenant-Id')?.value || '';

  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <Theme appearance="light" accentColor="violet">
          <TenantProvider tenantId={tenantId}>
            {children}
            <ThemePanel />
            <Toaster />
          </TenantProvider>
        </Theme>
      </body>
    </html>
  );
}
