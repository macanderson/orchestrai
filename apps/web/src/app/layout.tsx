import React from "react";
import { Metadata } from "next";
import { cookies } from "next/headers";
import { Toaster } from "react-hot-toast";
import { TenantProvider } from "@/providers/TenantProvider";
import { ThemeProvider } from "@/providers/ThemeProvider";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "DocuChat - Chat with Documentation",
  description: "A RAG-based documentation chat system",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore = await cookies();
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
