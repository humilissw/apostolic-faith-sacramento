"use client";

import { useState, useEffect } from "react";
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

export default function AssignmentDialog({
  open,
  onOpenChange,
  assignment,
  users = [],
  onSuccess,
}: AssignmentDialogProps) {
  const [user_id, setUserId] = useState(assignment?.user_id ?? "");
  const [event_date, setEventDate] = useState(
    assignment?.event_date
      ? new Date(assignment.event_date).toISOString().split("T")[0]
      : new Date().toISOString().split("T")[0]
  );
  const [type, setType] = useState<"music" | "service">(assignment?.type ?? "music");
  const [role, setRole] = useState(assignment?.role ?? "");
  const [instrument, setInstrument] = useState(assignment?.instrument ?? "");
  const [notes, setNotes] = useState(assignment?.notes ?? "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (assignment) {
      setUserId(assignment.user_id);
      setEventDate(new Date(assignment.event_date).toISOString().split("T")[0]);
      setType(assignment.type);
      setRole(assignment.role);
      setInstrument(assignment.instrument ?? "");
      setNotes(assignment.notes ?? "");
    }
  }, [assignment]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (assignment) {
        await updateAssignment(assignment.id, {
          user_id,
          event_date: new Date(event_date).toISOString(),
          type,
          role,
          instrument: instrument || null,
          notes: notes || null,
        });
        toast.success("Assignment updated");
      } else {
        await createAssignment({
          user_id,
          event_date: new Date(event_date).toISOString(),
          type,
          role,
          instrument: instrument || null,
          notes: notes || null,
        });
        toast.success("Assignment created");
      }
      onOpenChange(false);
      onSuccess();
    } catch {
      toast.error("Failed to save assignment");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{assignment ? "Edit Assignment" : "New Assignment"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="user_id">User</Label>
            <Select value={user_id} onValueChange={setUserId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a user" />
              </SelectTrigger>
              <SelectContent>
                {users.map((u) => (
                  <SelectItem key={u.id} value={u.id}>
                    {u.email}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="event_date">Event Date</Label>
            <Input
              id="event_date"
              type="date"
              value={event_date}
              onChange={(e) => setEventDate(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="type">Type</Label>
            <Select value={type} onValueChange={(v) => setType(v as "music" | "service")}>
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
            <Input id="role" value={role} onChange={(e) => setRole(e.target.value)} placeholder="e.g. Worship Leader" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="instrument">Instrument</Label>
            <Input id="instrument" value={instrument} onChange={(e) => setInstrument(e.target.value)} placeholder="e.g. Guitar" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Input id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes" />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
