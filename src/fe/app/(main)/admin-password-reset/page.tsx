"use client";

import { useState } from "react";
import { Key, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { adminPasswordReset } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AdminPasswordResetPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setLoading(true);
    setSuccess(null);
    setError(null);

    try {
      await adminPasswordReset(email.trim());
      setSuccess("Password recovery email sent successfully");
      setEmail("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to send password reset";
      // If the feature flag is disabled, show a clear message
      if (message.includes("disabled")) {
        setError("Admin password reset is currently disabled. Please contact your system administrator.");
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-12 max-w-lg">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Key className="w-7 h-7 text-muted-foreground" />
          <h1 className="text-4xl font-bold text-foreground">Admin Password Reset</h1>
        </div>
        <p className="text-muted-foreground">
          Send a password reset email to any user in the application. The user will receive a link to set a new password.
        </p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1.5">
              User Email Address
            </label>
            <Input
              id="email"
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <Button type="submit" disabled={loading || !email.trim()} className="w-full">
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Key className="w-4 h-4 mr-2" />
                Send Reset Email
              </>
            )}
          </Button>
        </form>

        {success && (
          <div className="mt-4 flex items-start gap-2 p-3 rounded-lg bg-green-50 border border-green-200 text-green-800">
            <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm">{success}</p>
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-800">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}
      </Card>
    </div>
  );
}
