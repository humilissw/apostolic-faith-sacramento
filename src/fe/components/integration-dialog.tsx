"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  createIntegration,
  fetchIntegration,
  testIntegrationConnection,
  updateIntegration,
  type IntegrationWithCreds,
  type TestConnectionResult,
} from "@/lib/api";

const KNOWN_TYPES = [
  { value: "stripe", label: "Stripe", requiredFields: ["secret_key", "public_key", "webhook_secret"] },
  { value: "twilio", label: "Twilio", requiredFields: ["account_sid", "auth_token"] },
  { value: "sendgrid", label: "SendGrid", requiredFields: ["api_key"] },
  { value: "youtube", label: "YouTube", requiredFields: ["api_key"] },
  { value: "facebook", label: "Facebook", requiredFields: ["app_id", "app_secret"] },
  { value: "spotify", label: "Spotify", requiredFields: ["client_id", "client_secret"] },
];

const SECRET_FIELDS = new Set(["secret_key", "auth_token", "app_secret", "client_secret", "webhook_secret"]);

interface IntegrationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  integrationId: string | null;
  onSuccess: () => void;
}

export default function IntegrationDialog({
  open,
  onOpenChange,
  integrationId,
  onSuccess,
}: IntegrationDialogProps) {
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<TestConnectionResult | null>(null);
  const [type, setType] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [icon, setIcon] = useState("Plug");
  const [enabled, setEnabled] = useState(false);
  const [credentials, setCredentials] = useState<Record<string, string>>({});

  const currentType = KNOWN_TYPES.find((t) => t.value === type);

  // Load or reset form data when dialog opens
  useEffect(() => {
    if (!open) return;
    setError(null);
    setTestResult(null);
    if (integrationId) {
      fetchIntegration(integrationId)
        .then((data) => {
          setType(data.type);
          setDisplayName(data.display_name);
          setIcon(data.icon);
          setEnabled(data.enabled);
        })
        .catch((err) => setError(err.message));
    } else {
      setType("");
      setDisplayName("");
      setIcon("Plug");
      setEnabled(false);
      setCredentials({});
    }
    // eslint-disable-next-line react-hooks/set-state-in-effect
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, integrationId]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setTestResult(null);
    try {
      const payload = {
        type,
        display_name: displayName,
        icon,
        enabled,
        credentials,
        config_json: null,
      };
      let result: IntegrationWithCreds;
      if (integrationId) {
        result = await updateIntegration(integrationId, payload);
      } else {
        result = await createIntegration(payload);
      }
      onSuccess();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function handleTest() {
    if (!type) return;
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testIntegrationConnection({
        type,
        credentials,
        config_json: null,
      });
      setTestResult(result);
    } catch {
      setTestResult({ success: false, status: "error", message: "Connection test failed" });
    } finally {
      setTesting(false);
    }
  }

  const updateCredential = (field: string, value: string) => {
    setCredentials((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{integrationId ? "Edit Integration" : "New Integration"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <Label>Type</Label>
            <Select value={type} onValueChange={(v) => { setType(v); setCredentials({}); setTestResult(null); }}>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {KNOWN_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Display Name</Label>
            <Input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Stripe Payments"
            />
          </div>

          <div>
            <Label>Icon (Lucide name)</Label>
            <Input
              value={icon}
              onChange={(e) => setIcon(e.target.value)}
              placeholder="Plug"
            />
          </div>

          {currentType && currentType.requiredFields.map((field) => (
            <div key={field}>
              <Label>{field.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</Label>
              <Input
                type={SECRET_FIELDS.has(field) ? "password" : "text"}
                value={credentials[field] || ""}
                onChange={(e) => updateCredential(field, e.target.value)}
                placeholder={`Enter ${field}`}
              />
            </div>
          ))}

          <div className="flex items-center gap-2 pt-2">
            <Switch checked={enabled} onCheckedChange={setEnabled} id="enabled" />
            <Label htmlFor="enabled">Enabled</Label>
          </div>

          {currentType && (
            <Button
              type="button"
              variant="outline"
              disabled={testing || !type || Object.keys(credentials).length === 0}
              onClick={handleTest}
            >
              {testing ? "Testing..." : "Test Connection"}
            </Button>
          )}

          {testResult && (
            <p className={`text-sm ${testResult.success ? "text-green-600" : "text-red-600"}`}>
              {testResult.success ? "Connected" : "Failed"}: {testResult.message}
            </p>
          )}

          {error && <p className="text-red-600 text-sm">{error}</p>}

          <DialogFooter>
            <Button type="submit" disabled={saving || !type}>
              {saving ? "Saving..." : integrationId ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
