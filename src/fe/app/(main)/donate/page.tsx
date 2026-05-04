"use client";

import DonationForm from "@/components/donation-form";
import DonationHistory from "@/components/donation-history";

function getCookie(name: string): string | null {
  const match = document.cookie.match("(^| )" + name + "=([^;]+)");
  return match ? decodeURIComponent(match[2]) : null;
}

export default function DonatePage() {
  const isAuthenticated = getCookie("access_token") !== null;

  return (
    <div className="container mx-auto py-12">
      <h1 className="text-4xl font-bold mb-8 text-center">
        Support Apostolic Faith Church
      </h1>
      <p className="text-center text-zinc-600 mb-12 max-w-2xl mx-auto">
        Your generous donations help us spread the Gospel and serve our community.
        Choose a one-time or monthly donation below.
      </p>
      <div className="grid md:grid-cols-2 gap-8">
        <DonationForm />
        {isAuthenticated && <DonationHistory />}
      </div>
    </div>
  );
}
