"use client";

import { useState } from "react";
import { Plus, Trash2, Loader2, Crown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { bulkAssignAssignments, type BulkAssignConflict } from "@/lib/api";
import { toast } from "sonner";

interface BulkAssignDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  users: Array<{ id: string; email: string }>;
  onSuccess: () => void;
}

interface Row {
  userId: string;
  role: string;
  instrument: string;
  notes: string;
  groupLeader: boolean;
}

export default function BulkAssignDialog({
  open,
  onOpenChange,
  users,
  onSuccess,
}: BulkAssignDialogProps) {
  const [eventDate, setEventDate] = useState(() => new Date().toISOString().split("T")[0]);
  const [type, setType] = useState<"music" | "service">("music");
  const [rows, setRows] = useState<Row[]>([{ userId: "", role: "", instrument: "", notes: "", groupLeader: false }]);
  const [saving, setSaving] = useState(false);
  const [conflicts, setConflicts] = useState<BulkAssignConflict[]>([]);

  const addRow = () => setRows((prev) => [...prev, { userId: "", role: "", instrument: "", notes: "", groupLeader: false }]);
  const removeRow = (index: number) => setRows((prev) => prev.filter((_, i) => i !== index));

  const updateRow = (index: number, field: keyof Row, value: string | boolean) => {
    setRows((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value } : row)),
    );
  };

  const handleConfirm = async () => {
    const validRows = rows.filter((r) => r.userId);
    if (validRows.length === 0) {
      toast.error("Select at least one user");
      return;
    }
    setSaving(true);
    setConflicts([]);
    try {
      const res = await bulkAssignAssignments({
        event_date: new Date(eventDate).toISOString(),
        type,
        entries: validRows.map((r) => ({
          user_id: r.userId,
          role: r.role,
          instrument: r.instrument || null,
          notes: r.notes || null,
          group_leader: r.groupLeader,
        })),
      });

      if (res.conflicts.length > 0) {
        setConflicts(res.conflicts);
        toast.error(`${res.conflicts.length} conflict(s) — ${res.created.length} created`);
      } else {
        toast.success(`${res.created.length} assignments created`);
      }

      onOpenChange(false);
      setRows([{ userId: "", role: "", instrument: "", notes: "", groupLeader: false }]);
      setConflicts([]);
      onSuccess();
    } catch {
      toast.error("Failed to bulk assign assignments");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Bulk Assign Performers</DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-6 py-6">
          {/* Shared fields */}
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="bulk-event-date" className="text-sm font-medium">Event Date</Label>
              <Input
                id="bulk-event-date"
                type="date"
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
                required
                className="h-10"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="bulk-type" className="text-sm font-medium">Type</Label>
              <Select value={type} onValueChange={(v) => setType(v as "music" | "service")}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="music">Music</SelectItem>
                  <SelectItem value="service">Service</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* User rows */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium">Performers</Label>
              <Button variant="outline" size="sm" type="button" onClick={addRow}>
                <Plus className="w-3 h-3 mr-1" />
                Add Performer
              </Button>
            </div>

            <div className="space-y-3">
              {rows.map((row, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-muted-foreground">Performer #{index + 1}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      type="button"
                      onClick={() => removeRow(index)}
                      disabled={rows.length === 1}
                      className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                  <div className="space-y-3">
                    <Select value={row.userId} onValueChange={(v) => updateRow(index, "userId", v)}>
                      <SelectTrigger className="h-10">
                        <SelectValue placeholder="Select user" />
                      </SelectTrigger>
                      <SelectContent>
                        {users.map((u) => (
                          <SelectItem key={u.id} value={u.id}>
                            {u.email}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        placeholder="Role"
                        value={row.role}
                        onChange={(e) => updateRow(index, "role", e.target.value)}
                        className="h-10"
                      />
                      <Input
                        placeholder="Instrument"
                        value={row.instrument}
                        onChange={(e) => updateRow(index, "instrument", e.target.value)}
                        className="h-10"
                      />
                    </div>
                    <div className="grid grid-cols-[1fr_auto] items-center gap-3">
                      <Input
                        placeholder="Notes (optional)"
                        value={row.notes}
                        onChange={(e) => updateRow(index, "notes", e.target.value)}
                        className="h-10"
                      />
                      <div className="flex items-center gap-2 shrink-0">
                        <Label htmlFor={`leader-${index}`} className="text-sm font-medium flex items-center gap-1.5 whitespace-nowrap">
                          <Crown className="w-3.5 h-3.5 text-amber-500" />
                          Group Leader
                        </Label>
                        <Switch
                          id={`leader-${index}`}
                          checked={row.groupLeader}
                          onCheckedChange={(v) => updateRow(index, "groupLeader", v)}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Conflicts */}
        {conflicts.length > 0 && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-3 space-y-1">
            <p className="text-sm font-medium text-red-800">Conflicts:</p>
            {conflicts.map((c, i) => (
              <p key={i} className="text-xs text-red-700 ml-4">
                {c.message}
              </p>
            ))}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={saving}>
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Assigning...
              </>
            ) : (
              "Assign"
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
