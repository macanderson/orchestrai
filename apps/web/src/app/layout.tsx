import React from "react";
import { Metadata } from "next";
import { cookies } from "next/headers";
import "@/styles/globals.css";

// Placeholder Toaster
const Toaster = () => null;
// Placeholder TenantProvider
const TenantProvider = ({
  children,
}: {
  children: React.ReactNode;
  tenantId: string;
}) => <>{children}</>;
// Placeholder ThemeProvider
const ThemeProvider = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);

export const metadata: Metadata = {
  title: "DocuChat - Chat with Documentation",
  description: "A RAG-based documentation chat system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = cookies();
  const tenantId = cookieStore.get("X-Tenant-Id")?.value || "";

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
