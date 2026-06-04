"use client";

import { AuthProvider } from "@/context/auth-context";
import { FeatureFlagProvider } from "@/context/feature-flag-context";
import NavbarClient from "@/components/navbar-client";
import Footer from "@/components/footer";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <FeatureFlagProvider>
        <>
          <NavbarClient />
          <main className="flex-1">{children}</main>
          <Footer />
        </>
      </FeatureFlagProvider>
    </AuthProvider>
  );
}
