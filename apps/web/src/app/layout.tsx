import { TenantProvider } from '@/providers/TenantProvider';
import { ThemeProvider } from '@/providers/ThemeProvider';
import { Metadata } from 'next';
import { cookies } from 'next/headers';
import React from 'react';
import { Toaster } from 'react-hot-toast';

import '@/styles/global.css';

export const metadata: Metadata = {
  title: 'OrchestrAI - AI-powered agents for your business',
  description: 'AI-powered agent generation for your business',
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const tenantId = cookieStore.get('X-Tenant-Id')?.value || '';

  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <TenantProvider tenantId={tenantId}>
            {children}
            <Toaster />
          </TenantProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
