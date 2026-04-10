"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className="flex justify-center items-start pt-40 min-h-screen">
      <div className="bg-white border border-zinc-200 rounded-xl p-8 w-full max-w-sm shadow-sm">
        <h1 className="text-2xl font-medium mb-1">Login</h1>
        <p className="text-sm text-zinc-500 mb-6">Enter your credentials to continue</p>

        <div className="mb-4">
          <Label htmlFor="username" className="text-sm mb-1.5">Username</Label>
          <Input id="username" type="text" placeholder="Enter your username" />
        </div>

        <div className="mb-6">
          <div className="flex justify-between items-center mb-1.5">
            <Label htmlFor="password" className="text-sm">Password</Label>
            <Link href="/forgot-password" className="text-xs text-blue-600 hover:underline">Forgot password?</Link>
          </div>
          <div className="relative">
            <Input id="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" className="pr-12" />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-zinc-400 hover:text-zinc-600"
            >
              {showPassword ? "hide" : "show"}
            </button>
          </div>
        </div>

        <Button className="w-full">Login</Button>
      </div>
    </div>
  )
}