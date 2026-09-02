"use client";

import { useEffect, useState } from "react";
import { Check, X, PlugZap } from "lucide-react";
import {
  fetchFeatureFlags,
  updateFeatureFlag,
  preSeedFeatureFlags,
  type FeatureFlagEntry,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

const KNOWN_FLAGS: Record<string, { displayName: string; icon: string }> = {
  enable_home: { displayName: "Home", icon: "Home" },
  enable_doctrines: { displayName: "Doctrines", icon: "BookOpen" },
  enable_contact: { displayName: "Contact", icon: "Mail" },
  enable_media: { displayName: "Media", icon: "Film" },
  enable_donate: { displayName: "Donate", icon: "CreditCard" },
  enable_sermon: { displayName: "Sermons", icon: "Video" },
  enable_live_service: { displayName: "Live Service", icon: "Broadcast" },
  enable_video_uploads: { displayName: "Video Uploads", icon: "Video" },
  enable_scheduler_calendar: { displayName: "Scheduler Calendar", icon: "Calendar" },
  enable_scheduler_admin: { displayName: "Scheduler Admin", icon: "Calendar" },
  enable_my_scheduler: { displayName: "My Scheduler", icon: "Calendar" },
  enable_users_admin: { displayName: "Users Admin", icon: "Users" },
  enable_video_uploads_admin: { displayName: "Video Uploads Admin", icon: "Film" },
  enable_integrations: { displayName: "Integrations", icon: "Settings" },
  enable_events: { displayName: "Events", icon: "Calendar" },
  enable_events_admin: { displayName: "Events Admin", icon: "Calendar" },
};

interface KnownFlagMeta {
  display_name: string;
  description: string;
  icon: string;
  required_scopes: string[];
}

export default function FlagsAdminPage() {
  const [flags, setFlags] = useState<FeatureFlagEntry[]>([]);
  const [knownFlags, setKnownFlags] = useState<Record<string, KnownFlagMeta>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [flagsRes, knownRes] = await Promise.all([
          fetchFeatureFlags(),
          fetch(`${API_BASE}${API_V1}/feature-flags/known`).then((r) => r.json()),
        ]);
        if (!cancelled) {
          setFlags(flagsRes.data);
          setKnownFlags(knownRes);
        }
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
    const API_V1 = "api/v1";
    load();
    return () => { cancelled = true; };
  }, []);

  const handleToggle = async (name: string, enabled: boolean) => {
    setToggling(name);
    try {
      const updated = await updateFeatureFlag(name, enabled);
      setFlags((prev) => prev.map((f) => (f.name === name ? updated : f)));
    } catch {
      setError("Failed to update feature flag");
    } finally {
      setToggling(null);
    }
  };

  const handlePreSeed = async () => {
    try {
      await preSeedFeatureFlags();
      const data = await fetchFeatureFlags();
      setFlags(data.data);
    } catch {
      setError("Failed to pre-seed feature flags");
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-12">
        <div className="flex justify-center items-center min-h-dvh">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-12">
        <div className="flex justify-center items-center min-h-dvh">
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-dvh flex flex-col container mx-auto py-12 max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Feature Flags</h1>
          <p className="text-muted-foreground mt-1">
            Control which views are visible in the application
          </p>
        </div>
        <Button variant="outline" onClick={handlePreSeed}>
          <PlugZap className="w-4 h-4 mr-2" />
          Pre-seed
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Flag Name</TableHead>
              <TableHead>Display Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Required Scopes</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-20">Toggle</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {flags.map((flag) => {
              const scopes = knownFlags[flag.name]?.required_scopes ?? [];
              return (
                <TableRow key={flag.id}>
                  <TableCell className="font-mono text-sm">{flag.name}</TableCell>
                  <TableCell>{KNOWN_FLAGS[flag.name]?.displayName ?? flag.name}</TableCell>
                  <TableCell className="text-muted-foreground">{flag.description}</TableCell>
                  <TableCell>
                    {scopes.length === 0 ? (
                      <span className="text-muted-foreground">None (public)</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {scopes.map((scope) => (
                          <span
                            key={scope}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-blue-50 text-blue-700 border border-blue-200"
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <span
                      className={
                        flag.is_enabled
                          ? "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                          : "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
                      }
                    >
                      {flag.is_enabled ? (
                        <Check className="w-3 h-3" />
                      ) : (
                        <X className="w-3 h-3" />
                      )}
                      {flag.is_enabled ? "Enabled" : "Disabled"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={flag.is_enabled}
                        onCheckedChange={(enabled) => handleToggle(flag.name, enabled)}
                        disabled={toggling === flag.name}
                      />
                      <Label className="sr-only">{flag.name}</Label>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
