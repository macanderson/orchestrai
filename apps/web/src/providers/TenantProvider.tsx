'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';

interface TenantContextType {
  tenantId: string;
  setTenantId: (id: string) => void;
}

const TenantContext = createContext<TenantContextType>({
  tenantId: '',
  setTenantId: () => {},
});

export const useTenant = () => useContext(TenantContext);

export const TenantProvider = ({
  children,
  tenantId: initialTenantId,
}: {
  children: React.ReactNode;
  tenantId: string;
}) => {
  const [tenantId, setTenantIdState] = useState<string>(initialTenantId);

  useEffect(() => {
    if (initialTenantId && initialTenantId !== tenantId) {
      setTenantIdState(initialTenantId);
    }
  }, [initialTenantId, tenantId]); // Added tenantId to dependency array

  const setTenantId = (id: string) => {
    if (id === tenantId) return;
    document.cookie = `X-Tenant-Id=${id}; path=/; max-age=31536000; SameSite=Strict`;
    setTenantIdState(id);
    // Optionally, trigger a reload or callback here
  };

  return (
    <TenantContext.Provider value={{ tenantId, setTenantId }}>{children}</TenantContext.Provider>
  );
};
