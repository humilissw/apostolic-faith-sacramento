const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- Payment / Donation types ---

export interface DonationFormData {
  amount_cents: number;
  currency: string;
  frequency: "one_time" | "recurring";
  donor_email?: string;
  donor_name?: string;
}

export interface PaymentIntentResult {
  client_secret: string;
  payment_intent_id: string;
}

export interface CheckoutSessionResult {
  client_secret: string;
  type: "checkout";
  checkout_url: string;
}

export interface DonationConfig {
  id: string;
  label: string;
  amount_cents: number;
  is_default: boolean;
  frequency: "one_time" | "recurring";
  created_on: string;
}

export interface PaymentRecord {
  id: string;
  amount_cents: number;
  currency: string;
  status: string;
  stripe_payment_intent_id: string;
  stripe_subscription_id: string | null;
  donor_email: string | null;
  donor_name: string | null;
  receipt_url: string | null;
  created_on: string;
  updated_on: string | null;
}

// --- Payment / Donation API functions ---

export async function createPaymentIntent(data: DonationFormData): Promise<PaymentIntentResult> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/create-intent`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create payment intent");
  }

  return res.json();
}

export async function createSubscription(data: DonationFormData): Promise<CheckoutSessionResult> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/create-subscription`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create subscription");
  }

  return res.json();
}

export async function fetchDonationConfigs(): Promise<DonationConfig[]> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/config`);
  if (!res.ok) {
    throw new Error("Failed to fetch donation configs");
  }
  const body = await res.json();
  return body.data;
}

export async function fetchUserPayments(): Promise<{ data: PaymentRecord[]; count: number }> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/payments/`);
  if (!res.ok) {
    throw new Error("Failed to fetch payments");
  }
  return res.json();
}
