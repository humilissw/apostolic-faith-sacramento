"use client";

import DonationForm from "@/components/donation-form";
import DonationHistory from "@/components/donation-history";
import { useAuth } from "@/context/auth-context";

export default function DonatePage() {
  const { isAuthenticated, isLoadingToken } = useAuth();

  return (
    <div className="container mx-auto py-12">
      <h1 className="text-4xl font-bold mb-8 text-center">
        Support Apostolic Faith Church
      </h1>
      <p className="text-center text-zinc-600 mb-12 max-w-2xl mx-auto">
        Your generous donations help us spread the Gospel and serve the community.
        Choose a one-time or monthly donation below.
      </p>
      <div className="grid md:grid-cols-2 gap-8">
        <DonationForm />
        {!isLoadingToken && isAuthenticated && <DonationHistory />}
      </div>
    </div>
  );
}
