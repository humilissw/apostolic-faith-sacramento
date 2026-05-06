"use client";

import { useEffect, useState } from "react";
import { Check, X, Pencil, Trash2, WifiOff, PlugZap } from "lucide-react";
import {
  fetchIntegrations,
  deleteIntegration,
  preSeedIntegrations,
  type IntegrationConfig,
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
import { cn } from "@/lib/utils";
import IntegrationDialog from "@/components/integration-dialog";

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<IntegrationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await fetchIntegrations();
        if (!cancelled) setIntegrations(data.data);
      } catch (err) {
        console.debug("🚀 ~ load ~ err:", err)
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this integration?")) return;
    setDeletingId(id);
    try {
      await deleteIntegration(id);
      setIntegrations((prev) => prev.filter((i) => i.id !== id));
    } catch {
      setError("Failed to delete integration");
    } finally {
      setDeletingId(null);
    }
  };

  const handleOpenDialog = (id: string | null) => {
    setEditingId(id);
    setDialogOpen(true);
  };

  const handlePreSeed = async () => {
    try {
      await preSeedIntegrations();
      const data = await fetchIntegrations();
      setIntegrations(data.data);
    } catch {
      setError("Failed to pre-seed integrations");
    }
  };

  const statusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "bg-green-100 text-green-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-600";
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
    <div className="container mx-auto py-12 max-w-6xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Integrations</h1>
          <p className="text-muted-foreground mt-1">
            Manage third-party service connections
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handlePreSeed}>
            <PlugZap className="w-4 h-4 mr-2" />
            Pre-seed
          </Button>
          <Button onClick={() => handleOpenDialog(null)}>
            <PlusIcon className="w-4 h-4 mr-2" />
            New Integration
          </Button>
        </div>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">Icon</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Enabled</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {integrations.map((integration) => (
              <TableRow key={integration.id}>
                <TableCell className="font-medium">
                  <span className="text-lg">{integration.icon}</span>
                </TableCell>
                <TableCell className="font-mono text-sm">
                  {integration.type}
                </TableCell>
                <TableCell>{integration.display_name}</TableCell>
                <TableCell>
                  <span
                    className={cn(
                      "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                      statusColor(integration.status),
                    )}
                  >
                    {integration.status === "connected" ? (
                      <Check className="w-3 h-3" />
                    ) : integration.status === "error" ? (
                      <X className="w-3 h-3" />
                    ) : (
                      <WifiOff className="w-3 h-3" />
                    )}
                    {integration.status}
                  </span>
                </TableCell>
                <TableCell>
                  {integration.enabled ? (
                    <span className="text-green-600 text-sm">Yes</span>
                  ) : (
                    <span className="text-gray-400 text-sm">No</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenDialog(integration.id)}
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={deletingId === integration.id}
                      onClick={() => handleDelete(integration.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <IntegrationDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        integrationId={editingId}
        onSuccess={() => {
          setDialogOpen(false);
          fetchIntegrations().then((data) => setIntegrations(data.data));
        }}
      />
    </div>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  );
}
