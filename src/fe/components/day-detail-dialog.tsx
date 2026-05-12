"use client";

import { useState } from "react";
import {
  Music,
  Users,
  X,
  Clock,
  Trash2,
  Pencil,
  Crown,
  CalendarDays,
  CheckCircle2,
  XCircle,
  AlertCircle,
  UserPlus,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  updateAssignment,
  deleteAssignment,
  createTimeOffRequest,
  deleteTimeOffRequest,
  type Assignment,
  type TimeOffRequest,
} from "@/lib/api";
import { toast } from "sonner";

interface UserOption {
  id: string;
  email: string;
}

interface DayDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  date: string;
  assignments: Assignment[];
  myAssignments: Assignment[];
  timeOff: TimeOffRequest | undefined;
  users: UserOption[];
  isAdmin: boolean;
  onRefresh: () => void;
}

export default function DayDetailDialog({
  open,
  onOpenChange,
  date,
  assignments,
  myAssignments,
  timeOff,
  users,
  isAdmin,
  onRefresh,
}: DayDetailDialogProps) {
  // Edit assignment state
  const [editingAssignment, setEditingAssignment] = useState<Assignment | null>(null);
  const [editUserId, setEditUserId] = useState("");
  const [editRole, setEditRole] = useState("");
  const [editInstrument, setEditInstrument] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editSaving, setEditSaving] = useState(false);

  // Time-off state
  const [toNote, setToNote] = useState("");
  const [toSubmitting, setToSubmitting] = useState(false);

  // Delete confirmation
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const isMyAssignment = (a: Assignment) => myAssignments.some((m) => m.id === a.id);

  const handleEditAssignment = (a: Assignment) => {
    setEditingAssignment(a);
    setEditUserId(a.user_id);
    setEditRole(a.role);
    setEditInstrument(a.instrument ?? "");
    setEditNotes(a.notes ?? "");
  };

  const handleSaveEdit = async () => {
    if (!editingAssignment || !editUserId) return;
    setEditSaving(true);
    try {
      await updateAssignment(editingAssignment.id, {
        user_id: editUserId,
        event_date: new Date(date).toISOString(),
        type: editingAssignment.type,
        role: editRole,
        instrument: editInstrument || null,
        notes: editNotes || null,
      });
      toast.success("Assignment updated");
      setEditingAssignment(null);
      onRefresh();
    } catch {
      toast.error("Failed to update assignment");
    } finally {
      setEditSaving(false);
    }
  };

  const handleDeleteAssignment = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteAssignment(id);
      toast.success("Assignment deleted");
      onRefresh();
    } catch {
      toast.error("Failed to delete assignment");
    } finally {
      setDeletingId(null);
    }
  };

  const handleRequestTimeOff = async () => {
    setToSubmitting(true);
    try {
      await createTimeOffRequest({ date: date + "T00:00:00", notes: toNote || null });
      toast.success("Time-off request submitted");
      setToNote("");
      onRefresh();
    } catch {
      toast.error("Failed to submit time-off request");
    } finally {
      setToSubmitting(false);
    }
  };

  const handleDeleteTimeOff = async () => {
    if (!timeOff) return;
    try {
      await deleteTimeOffRequest(timeOff.id);
      toast.success("Time-off request removed");
      onRefresh();
    } catch {
      toast.error("Failed to remove time-off request");
    }
  };

  const formatDate = (d: string) => new Date(d + "T00:00:00").toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col">
        <DialogHeader className="flex row items-center justify-between gap-2 pb-2 border-b">
          <DialogTitle className="flex items-center gap-2">
            <CalendarDays className="w-5 h-5" />
            {formatDate(date)}
          </DialogTitle>
          <p className="text-sm text-muted-foreground">{assignments.length} assignment{assignments.length !== 1 ? "s" : ""}</p>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto py-4 space-y-6">
          {/* Assignments */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-muted-foreground">Assigned Users</h3>
            {assignments.length === 0 && (
              <p className="text-sm text-muted-foreground py-4 text-center">No assignments for this day</p>
            )}
            {assignments.map((a) => {
              const mine = isMyAssignment(a);
              const userOption = users.find((u) => u.id === a.user_id);
              return (
                <div key={a.id} className={`border rounded-lg p-4 space-y-2 ${mine ? "border-green-300 bg-green-50/50" : ""}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center gap-1 text-sm font-medium ${a.type === "music" ? "text-blue-700" : "text-green-700"}`}>
                        {a.type === "music" ? <Music className="w-3.5 h-3.5" /> : <Users className="w-3.5 h-3.5" />}
                        {a.type === "music" ? "Music" : "Service"}
                      </span>
                      {a.group_leader && (
                        <span className="flex items-center gap-0.5 text-amber-600 text-xs font-medium">
                          <Crown className="w-3.5 h-3.5" />
                          Group Leader
                        </span>
                      )}
                      {mine && (
                        <span className="text-xs font-medium text-green-700 bg-green-100 px-1.5 py-0.5 rounded">Your Assignment</span>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handleEditAssignment(a)} className="h-7 w-7 p-0">
                        <Pencil className="w-3.5 h-3.5" />
                      </Button>
                      {isAdmin && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteAssignment(a.id)}
                          disabled={deletingId === a.id}
                          className="h-7 w-7 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-[1fr_auto] gap-x-4 gap-y-1 text-sm">
                    <div className="font-medium">{userOption?.email || a.user_full_name || a.user_email || "Unknown"}</div>
                    <div className="text-right text-muted-foreground">User: {a.user_id}</div>
                    <div className="text-muted-foreground">Role</div>
                    <div className="text-right">{a.role || "—"}</div>
                    <div className="text-muted-foreground">Instrument</div>
                    <div className="text-right">{a.instrument || "—"}</div>
                    {a.notes && (
                      <>
                        <div className="text-muted-foreground">Notes</div>
                        <div className="text-right text-muted-foreground text-xs">{a.notes}</div>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Time-off section */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-muted-foreground flex items-center gap-1.5 mb-2">
              <Clock className="w-3.5 h-3.5" />
              Time Off
            </h3>
            {timeOff ? (
              <div className="flex items-center justify-between border rounded-lg p-3">
                <div className="flex items-center gap-2">
                  {timeOff.status === "approved" ? (
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ) : timeOff.status === "declined" ? (
                    <XCircle className="w-4 h-4 text-red-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                  )}
                  <span className="text-sm font-medium">
                    {timeOff.status === "approved"
                      ? "Approved"
                      : timeOff.status === "declined"
                      ? "Declined"
                      : "Pending"}
                  </span>
                  {timeOff.notes && <span className="text-sm text-muted-foreground">— {timeOff.notes}</span>}
                </div>
                <Button variant="outline" size="sm" onClick={handleDeleteTimeOff}>
                  Remove Request
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Input
                    placeholder="Reason (optional)"
                    value={toNote}
                    onChange={(e) => setToNote(e.target.value)}
                    className="h-9"
                  />
                  <Button onClick={handleRequestTimeOff} disabled={toSubmitting} className="h-9 shrink-0">
                    <UserPlus className="w-3.5 h-3.5 mr-1" />
                    {toSubmitting ? "Requesting..." : "Request Time Off"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Edit assignment sub-dialog */}
        {editingAssignment && (
          <div className="border-t pt-4 space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold">Edit Assignment</h4>
              <Button variant="ghost" size="sm" onClick={() => setEditingAssignment(null)} className="h-6 w-6 p-0">
                <X className="w-3.5 h-3.5" />
              </Button>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">User</Label>
              <Select value={editUserId} onValueChange={setEditUserId}>
                <SelectTrigger className="h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {users.map((u) => (
                    <SelectItem key={u.id} value={u.id}>{u.email}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Role</Label>
              <Input value={editRole} onChange={(e) => setEditRole(e.target.value)} className="h-9" placeholder="e.g. Worship Leader" />
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Instrument</Label>
              <Input value={editInstrument} onChange={(e) => setEditInstrument(e.target.value)} className="h-9" placeholder="e.g. Guitar" />
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Notes</Label>
              <Input value={editNotes} onChange={(e) => setEditNotes(e.target.value)} className="h-9" placeholder="Optional notes" />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setEditingAssignment(null)}>Cancel</Button>
              <Button size="sm" onClick={handleSaveEdit} disabled={editSaving || !editUserId}>
                {editSaving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
