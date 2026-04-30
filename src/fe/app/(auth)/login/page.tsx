"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import AFCLogo from "@/components/afc-logo"

export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className="font-noto-sans bg-zinc-300 flex justify-center items-center p-6 min-h-dvh">
      <div className="bg-white border border-zinc-200 rounded-xl p-10 w-full max-w-lg shadow-sm">
          <div className="flex justify-center mb-5">
              <AFCLogo width={120} height={145}/>
          </div>


          <div className="text-center">
            <h1 className="text-3xl font-medium mb-5">Login</h1>
          </div>


        <div className="mb-5">
          <Label htmlFor="username" className="text-base mb-2">Username</Label>
          <Input id="username" type="text" placeholder="Enter your username" />
        </div>

        <div className="mb-8">
          <div className="flex justify-between items-center mb-1.5">
            <Label htmlFor="password" className="text-base">Password</Label>
            <Link href="/forgot-password" className="text-sm text-blue-600 hover:underline">Forgot password?</Link>
          </div>
          <div className="relative">
            <Input id="password" type={showPassword ? "text" : "password"} placeholder="Enter your password" className="pr-12"/>
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-zinc-400 hover:text-zinc-600"
            >
              {showPassword ? "hide" : "show"}
            </button>
          </div>
        </div>

        <Button className="w-full text-base py-5">Login</Button>
      </div>
    </div>
  )
}
