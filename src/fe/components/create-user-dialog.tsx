"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const ALL_SCOPES = [
  { category: "Core", scopes: [
    { value: "api:all", label: "Full API access" },
    { value: "spa:all", label: "Full SPA access" },
    { value: "mobile:all", label: "Full mobile access" },
    { value: "public:read", label: "Public read access" },
  ]},
  { category: "Payments", scopes: [
    { value: "payments:read", label: "Read payments" },
    { value: "payments:write", label: "Write payments" },
    { value: "payments:admin", label: "Admin payments" },
  ]},
  { category: "Integrations", scopes: [
    { value: "integrations:admin", label: "Admin integrations" },
  ]},
  { category: "Video Uploads", scopes: [
    { value: "video_uploads:read", label: "Read video uploads" },
    { value: "video_uploads:write", label: "Write video uploads" },
    { value: "video_uploads:delete", label: "Delete video uploads" },
    { value: "video_uploads:manage", label: "Manage video uploads" },
  ]},
  { category: "Users", scopes: [
    { value: "users:read", label: "Read users" },
    { value: "users:write", label: "Write users" },
    { value: "users:admin", label: "Admin users" },
  ]},
  { category: "Scheduler", scopes: [
    { value: "scheduler:admin", label: "Admin scheduler" },
    { value: "member:limited", label: "Limited member access" },
  ]},
  { category: "Superuser", scopes: [
    { value: "superuser", label: "Full superuser privileges" },
  ]},
];

interface CreateUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export default function CreateUserDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateUserDialogProps) {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [scopes, setScopes] = useState<string[]>([]);
  const isSuperuser = scopes.includes("superuser");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!email.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const { createUser } = await import("@/lib/api");
      await createUser({
        email: email.trim(),
        full_name: fullName.trim() || undefined,
        is_superuser: isSuperuser,
        scopes,
      });
      onSuccess();
      onOpenChange(false);
      setEmail("");
      setFullName("");
      setScopes([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create user");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Create User</DialogTitle>
          <DialogDescription>
            Add a new user to the application. The user will receive an email
            with a one-time link to set their own password.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoFocus
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              id="fullName"
              type="text"
              placeholder="Optional"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="superuser" className="text-sm font-medium">
              Superuser
            </Label>
            <Switch
              id="superuser"
              checked={isSuperuser}
              onCheckedChange={(val) => {
                if (val) setScopes(["superuser"]);
                else setScopes((prev) => prev.filter((s) => s !== "superuser"));
              }}
            />
          </div>

          <div className="space-y-3 max-h-60 overflow-y-auto">
            <h4 className="text-sm font-medium text-muted-foreground">
              Scopes
            </h4>
            {ALL_SCOPES.map((category) => (
              <div key={category.category}>
                <h5 className="text-xs font-medium text-muted-foreground mb-1">
                  {category.category}
                </h5>
                <div className="space-y-1">
                  {category.scopes.map((scope) => {
                    const checked = isSuperuser || scopes.includes(scope.value);
                    return (
                      <label
                        key={scope.value}
                        className={`flex items-center gap-3 px-3 py-1.5 rounded-lg transition-colors ${
                          isSuperuser ? "bg-amber-50 opacity-70 cursor-not-allowed" : "hover:bg-accent cursor-pointer"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={isSuperuser}
                          onChange={() => {
                            if (!isSuperuser) {
                              setScopes((prev) =>
                                prev.includes(scope.value)
                                  ? prev.filter((s) => s !== scope.value)
                                  : [...prev, scope.value],
                              );
                            }
                          }}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-xs font-mono">{scope.value}</span>
                        <span className="text-xs text-muted-foreground">
                          {scope.label}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <p className="text-sm text-red-600 px-1">{error}</p>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={creating}>
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={creating || !email.trim() || !email.includes("@")}
          >
            {creating ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : null}
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
