"use client";

import { createContext, useContext, useMemo, useState } from "react";

interface DonationContextValue {
  lastPaymentIntent: string | null;
  setLastPaymentIntent: (id: string | null) => void;
}

const DonationContext = createContext<DonationContextValue | undefined>(undefined);

export function DonationProvider({ children }: { children: React.ReactNode }) {
  const [lastPaymentIntent, setLastPaymentIntent] = useState<string | null>(null);
  const value = useMemo(() => ({ lastPaymentIntent, setLastPaymentIntent }), [lastPaymentIntent]);
  return <DonationContext.Provider value={value}>{children}</DonationContext.Provider>;
}

export function useDonation() {
  const context = useContext(DonationContext);
  if (context === undefined) {
    throw new Error("useDonation must be used inside a DonationProvider");
  }
  return context;
}
