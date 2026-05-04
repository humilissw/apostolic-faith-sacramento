"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import AFCLogo from "@/components/afc-logo";
import { generatePkceChallenge, googleLoginUrl } from "@/lib/api";
import { login as apiLogin } from "@/lib/api";
import { useAuth } from "@/context/auth-context";

export default function LoginForm() {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const res = await apiLogin(email, password, ["api:all"]);
      login(); // cookies are set by backend; client just triggers state update
      window.location.assign("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleGoogleLogin() {
    setIsGoogleLoading(true);
    setError("");

    try {
      const pkce = await generatePkceChallenge();
      // Store code_verifier in sessionStorage (cleared when tab closes)
      sessionStorage.setItem("google_code_verifier", pkce.code_verifier);

      const url = googleLoginUrl(pkce.code_challenge);
      window.location.assign(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google login failed");
      setIsGoogleLoading(false);
    }
  }

  return (
    <div className="font-noto-sans bg-zinc-300 flex justify-center items-center p-6 min-h-dvh">
      <div className="bg-white border border-zinc-200 rounded-xl p-10 w-full max-w-lg shadow-sm">
          <div className="flex justify-center mb-5">
              <AFCLogo width={120} height={145}/>
          </div>

          <div className="text-center">
            <h1 className="text-3xl font-medium mb-5">Login</h1>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-5">
              <Label htmlFor="username" className="text-base mb-2">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="mb-8">
              <div className="flex justify-between items-center mb-1.5">
                <Label htmlFor="password" className="text-base">Password</Label>
                <Link href="/forgot-password/" className="text-sm text-blue-600 hover:underline">Forgot password?</Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  className="pr-12"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-zinc-400 hover:text-zinc-600"
                >
                  {showPassword ? "hide" : "show"}
                </button>
              </div>
            </div>

            {error && (
              <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
            )}

            <Button className="w-full text-base py-5" type="submit" disabled={isLoading}>
              {isLoading ? "Logging in..." : "Login"}
            </Button>
          </form>

          <div className="flex items-center my-6">
            <div className="flex-1 border-t border-zinc-200" />
            <span className="px-3 text-sm text-zinc-400">or</span>
            <div className="flex-1 border-t border-zinc-200" />
          </div>

          <Button
            className="w-full text-base py-4 bg-white border border-zinc-300 text-zinc-700 hover:bg-zinc-50"
            type="button"
            disabled={isGoogleLoading}
            onClick={handleGoogleLogin}
          >
            {isGoogleLoading ? "Signing in..." : "Sign in with Google"}
          </Button>
      </div>
    </div>
  );
}
