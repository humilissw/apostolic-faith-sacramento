"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import AFCLogo from "@/components/afc-logo";
import { requestPasswordReset } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess(false);

    try {
      await requestPasswordReset(email);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send reset email");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="font-noto-sans bg-zinc-300 flex justify-center items-center p-6 min-h-dvh">
      <div className="bg-white border border-zinc-200 rounded-xl p-10 w-full max-w-lg shadow-sm">
        <div className="flex justify-center mb-5">
          <AFCLogo width={120} height={145} />
        </div>

        <div className="text-center">
          <h1 className="text-3xl font-medium mb-5">Forgot Password</h1>
          <p className="text-zinc-600 mb-8">
            Enter your email address and we&apos;ll send you a link to reset your password.
          </p>
        </div>

        {success ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 text-center">
            <p className="text-green-700 font-medium mb-2">Email sent!</p>
            <p className="text-green-600 text-sm">
              Check your inbox for the password reset link. It will expire in 1 hour.
            </p>
            <Link href="/login/" className="text-blue-600 hover:underline text-sm mt-3 inline-block">
              Back to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-5">
              <Label htmlFor="email" className="text-base mb-2">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            {error && (
              <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
            )}

            <Button
              className="w-full text-base py-5"
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? "Sending..." : "Send Reset Link"}
            </Button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link href="/login/" className="text-sm text-blue-600 hover:underline">
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
