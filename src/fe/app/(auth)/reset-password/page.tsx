"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import AFCLogo from "@/components/afc-logo";
import { resetPassword } from "@/lib/api";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Read token directly from URL to avoid useSearchParams() during static export
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!token) {
      setError("Invalid reset link. Please request a new password reset.");
      return;
    }

    setIsLoading(true);

    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password");
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
          <h1 className="text-3xl font-medium mb-5">Reset Password</h1>
          <p className="text-zinc-600 mb-8">
            Enter your new password below.
          </p>
        </div>

        {success ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 text-center">
            <p className="text-green-700 font-medium mb-2">Password updated!</p>
            <p className="text-green-600 text-sm">
              Your password has been reset successfully. You can now log in with your new password.
            </p>
            <Link href="/login/" className="text-blue-600 hover:underline text-sm mt-3 inline-block">
              Go to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-5">
              <Label htmlFor="newPassword" className="text-base mb-2">
                New Password
              </Label>
              <Input
                id="newPassword"
                type="password"
                placeholder="Enter new password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
              />
              <p className="text-xs text-zinc-500 mt-1">
                Must be at least 8 characters with uppercase, lowercase, digit, and special character.
              </p>
            </div>

            <div className="mb-6">
              <Label htmlFor="confirmPassword" className="text-base mb-2">
                Confirm New Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && (
              <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
            )}

            <Button
              className="w-full text-base py-5"
              type="submit"
              disabled={isLoading || !token}
            >
              {isLoading ? "Updating..." : "Reset Password"}
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
