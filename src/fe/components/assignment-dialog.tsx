"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import type { Assignment } from "@/lib/api";
import { createAssignment, updateAssignment } from "@/lib/api";

interface AssignmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  assignment: Assignment | null;
  users?: Array<{ id: string; email: string }>;
  onSuccess: () => void;
}

interface Conflict {
  id: string;
  type: string;
  role: string;
  event_date: string;
}

export default function AssignmentDialog({
  open,
  onOpenChange,
  assignment,
  users = [],
  onSuccess,
}: AssignmentDialogProps) {
  const [saving, setSaving] = useState(false);
  const [conflictError, setConflictError] = useState<string | null>(null);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [formUserId, setFormUserId] = useState(assignment?.user_id ?? "");
  const [formEventDate, setFormEventDate] = useState(
    assignment?.event_date
      ? new Date(assignment.event_date).toISOString().split("T")[0]
      : new Date().toISOString().split("T")[0]
  );
  const [formType, setFormType] = useState<"music" | "service">(assignment?.type ?? "music");
  const [formRole, setFormRole] = useState(assignment?.role ?? "");
  const [formInstrument, setFormInstrument] = useState(assignment?.instrument ?? "");
  const [formNotes, setFormNotes] = useState(assignment?.notes ?? "");

  // Sync form when a new assignment is selected
  if (assignment) {
    setFormUserId(assignment.user_id);
    setFormEventDate(new Date(assignment.event_date).toISOString().split("T")[0]);
    setFormType(assignment.type);
    setFormRole(assignment.role);
    setFormInstrument(assignment.instrument ?? "");
    setFormNotes(assignment.notes ?? "");
  }

  const handleSubmit = async () => {
    setSaving(true);
    setConflictError(null);
    setConflicts([]);
    try {
      if (assignment) {
        await updateAssignment(assignment.id, {
          user_id: formUserId,
          event_date: new Date(formEventDate).toISOString(),
          type: formType,
          role: formRole,
          instrument: formInstrument || null,
          notes: formNotes || null,
        });
        toast.success("Assignment updated");
      } else {
        await createAssignment({
          user_id: formUserId,
          event_date: new Date(formEventDate).toISOString(),
          type: formType,
          role: formRole,
          instrument: formInstrument || null,
          notes: formNotes || null,
        });
        toast.success("Assignment created");
      }
      onOpenChange(false);
      onSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save assignment";
      if (msg.includes("Conflict")) {
        setConflictError("Double-booking detected");
        setConflicts([]);
        toast.error(msg);
      } else {
        toast.error(msg);
      }
    } finally {
      setSaving(false);
    }
  };

  const selectedUser = users.find((u) => u.id === formUserId);

  return (
    <Dialog open={open} onOpenChange={(val) => {
      if (!val) {
        // Reset form fields when closing
        if (assignment) {
          setFormUserId(assignment.user_id);
          setFormEventDate(new Date(assignment.event_date).toISOString().split("T")[0]);
          setFormType(assignment.type);
          setFormRole(assignment.role);
          setFormInstrument(assignment.instrument ?? "");
          setFormNotes(assignment.notes ?? "");
        } else {
          setFormUserId("");
          setFormEventDate(new Date().toISOString().split("T")[0]);
          setFormType("music");
          setFormRole("");
          setFormInstrument("");
          setFormNotes("");
        }
      }
      onOpenChange(val);
    }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{assignment ? "Edit Assignment" : "New Assignment"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user_id">User</Label>
            <Select value={formUserId} onValueChange={setFormUserId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a user" />
              </SelectTrigger>
              <SelectContent>
                {users.length === 0 && (
                  <SelectItem value="__none" disabled>
                    No users available
                  </SelectItem>
                )}
                {users.map((u) => (
                  <SelectItem key={u.id} value={u.id}>
                    {u.email}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedUser && (
              <p className="text-xs text-muted-foreground">{selectedUser.email}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="event_date">Event Date</Label>
            <Input
              id="event_date"
              type="date"
              value={formEventDate}
              onChange={(e) => setFormEventDate(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="type">Type</Label>
            <Select value={formType} onValueChange={(v) => setFormType(v as "music" | "service")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="music">Music</SelectItem>
                <SelectItem value="service">Service</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Input id="role" value={formRole} onChange={(e) => setFormRole(e.target.value)} placeholder="e.g. Worship Leader" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="instrument">Instrument</Label>
            <Input id="instrument" value={formInstrument} onChange={(e) => setFormInstrument(e.target.value)} placeholder="e.g. Guitar" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Input id="notes" value={formNotes} onChange={(e) => setFormNotes(e.target.value)} placeholder="Optional notes" />
          </div>
          {conflictError && (
            <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
              <div className="flex items-center gap-2 text-amber-800 font-medium text-sm">
                <svg className="w-4 h-4 shrink-0" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
                {conflictError}
              </div>
              {conflicts.length > 0 && (
                <ul className="mt-2 ml-6 text-sm text-amber-700 space-y-1">
                  {conflicts.map((c) => (
                    <li key={c.id}>
                      {c.type}: {c.role}
                      <span className="text-xs text-amber-600 block">
                        {new Date(c.event_date).toLocaleDateString()}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={saving || !formUserId}>
              {saving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
