"use client";

import { useEffect, useRef, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { setUserScopes, fetchUsersWithScopes } from "@/lib/api";

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

interface UserScopeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId: string | null;
  userEmail: string;
  onSuccess: () => void;
}

export default function UserScopeDialog({
  open,
  onOpenChange,
  userId,
  userEmail,
  onSuccess,
}: UserScopeDialogProps) {
  const [scopes, setScopes] = useState<string[]>(() => {
    if (!open || !userId) return [];
    return [];
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isSuperuser, setIsSuperuser] = useState(() => {
    if (!open || !userId) return false;
    return false;
  });

  const openRef = useRef(open);
  const userIdRef = useRef(userId);
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    openRef.current = open;
    userIdRef.current = userId;
    if (!open || !userId) {
      setScopes([]);
      setIsSuperuser(false);
      return;
    }
    setLoading(true);
    fetchUsersWithScopes()
      .then((data) => {
        const user = data.data.find((u) => u.new_id === userId);
        if (user) {
          setScopes(user.assigned_scopes);
          setIsSuperuser(user.assigned_scopes.includes("superuser"));
        }
      })
      .catch(() => setScopes([]))
      .finally(() => setLoading(false));
  /* eslint-enable react-hooks/set-state-in-effect */
  }, [open, userId]);

  const toggleScope = (scope: string) => {
    setScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope],
    );
  };

  const handleSave = async () => {
    if (!userId) return;
    setSaving(true);
    try {
      await setUserScopes(userId, scopes);
      onSuccess();
    } catch {
      // Error handling at parent level
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {userId ? "Edit Scopes" : "New User Scopes"}
          </DialogTitle>
          <DialogDescription>
            {userId ? `Manage scopes for ${userEmail}` : "Set scopes for new user"}
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : isSuperuser ? (
          <div className="py-4">
            <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
              <Check className="w-4 h-4 text-amber-600" />
              <span className="text-sm text-amber-800 font-medium">
                This user is a superuser — has ALL scopes
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-4 max-h-80 overflow-y-auto">
            {ALL_SCOPES.map((category) => (
              <div key={category.category}>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">
                  {category.category}
                </h4>
                <div className="space-y-1">
                  {category.scopes.map((scope) => {
                    const checked = scopes.includes(scope.value);
                    return (
                      <label
                        key={scope.value}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent cursor-pointer transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleScope(scope.value)}
                          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm font-mono">{scope.value}</span>
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
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || isSuperuser}>
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
