"use client";

import { loadStripe } from "@stripe/stripe-js";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createPaymentIntent,
  createSubscription,
  fetchDonationConfigs,
  type DonationConfig,
  type DonationFormData,
  type PaymentIntentResult,
  type CheckoutSessionResult,
} from "@/lib/api";

const STRIPE_PUBLIC_KEY = process.env.NEXT_PUBLIC_STRIPE_PUBLIC_KEY || "";

const PRESET_AMOUNTS = [
  { label: "$10", value: 1000 },
  { label: "$25", value: 2500 },
  { label: "$50", value: 5000 },
  { label: "$100", value: 10000 },
  { label: "$250", value: 25000 },
];

interface DonationFormProps {
  onSuccess?: (paymentIntentId: string) => void;
  initialAmount?: number;
}

export default function DonationForm({ onSuccess, initialAmount }: DonationFormProps) {
  const [amount, setAmount] = useState(initialAmount || 2500);
  const [frequency, setFrequency] = useState<"one_time" | "recurring">("one_time");
  const [donorName, setDonorName] = useState("");
  const [donorEmail, setDonorEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check auth state on mount by looking for access_token cookie
  useEffect(() => {
    try {
      setIsAuthenticated(document.cookie.includes("access_token="));
    } catch {
      setIsAuthenticated(false);
    }
  }, []);

  const handleDonate = async () => {
    if (!STRIPE_PUBLIC_KEY) {
      setError("Stripe is not configured");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const payload: DonationFormData = {
        amount_cents: amount,
        currency: "usd",
        frequency,
        donor_email: donorEmail || undefined,
        donor_name: donorName || undefined,
      };

      const result =
        frequency === "one_time"
          ? await createPaymentIntent(payload)
          : await createSubscription(payload);

      if (frequency === "one_time" && "payment_intent_id" in result) {
        const paymentResult = result as PaymentIntentResult;
        const stripe = await loadStripe(STRIPE_PUBLIC_KEY);
        if (!stripe) throw new Error("Stripe failed to load");

        const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
          paymentResult.client_secret,
        );

        if (stripeError) {
          setError(stripeError.message || "Payment failed");
        } else if (paymentIntent?.status === "succeeded") {
          setSuccess(true);
          onSuccess?.(paymentIntent.id);
        }
      } else {
        const checkoutResult = result as CheckoutSessionResult;
        if (checkoutResult.checkout_url) {
          window.location.href = checkoutResult.checkout_url;
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Payment failed");
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-green-700">Thank You!</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-zinc-600">
            Your donation of ${(amount / 100).toFixed(2)} has been processed successfully.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Make a Donation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Preset amounts */}
        <div>
          <Label>Preset Amounts</Label>
          <div className="grid grid-cols-5 gap-2 mt-2">
            {PRESET_AMOUNTS.map((preset) => (
              <Button
                key={preset.value}
                type="button"
                variant={amount === preset.value ? "default" : "outline"}
                className="text-sm"
                onClick={() => setAmount(preset.value)}
              >
                {preset.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Custom amount */}
        <div>
          <Label htmlFor="custom-amount">Custom Amount</Label>
          <div className="relative mt-1">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500">$</span>
            <Input
              id="custom-amount"
              type="number"
              min="1"
              value={amount / 100}
              onChange={(e) => setAmount(Math.max(1, parseInt(e.target.value, 10) * 100))}
              className="pl-7"
            />
          </div>
        </div>

        {/* Frequency toggle */}
        <div>
          <Label>Frequency</Label>
          <div className="flex gap-4 mt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="frequency"
                checked={frequency === "one_time"}
                onChange={() => setFrequency("one_time")}
                className="accent-black"
              />
              <span>One-time</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="frequency"
                checked={frequency === "recurring"}
                onChange={() => setFrequency("recurring")}
                className="accent-black"
              />
              <span>Monthly</span>
            </label>
          </div>
        </div>

        {/* Guest fields */}
        {!isAuthenticated && (
          <div className="space-y-3">
            <div>
              <Label htmlFor="donor-name">Name</Label>
              <Input
                id="donor-name"
                value={donorName}
                onChange={(e) => setDonorName(e.target.value)}
                placeholder="Your name"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="donor-email">Email</Label>
              <Input
                id="donor-email"
                type="email"
                value={donorEmail}
                onChange={(e) => setDonorEmail(e.target.value)}
                placeholder="your@email.com"
                className="mt-1"
              />
            </div>
          </div>
        )}

        {/* Donate button */}
        <Button
          className="w-full text-base py-6"
          size="default"
          disabled={isLoading || amount < 100}
          onClick={handleDonate}
        >
          {isLoading
            ? frequency === "one_time"
              ? "Processing..."
              : "Redirecting to Stripe..."
            : `Donate $${(amount / 100).toFixed(2)}`}
        </Button>

        {/* Error message */}
        {error && <p className="text-red-600 text-sm text-center">{error}</p>}
      </CardContent>
    </Card>
  );
}
