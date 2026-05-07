"use client";

import { useEffect, useState } from "react";
import { Plus, Pencil, Trash2, Music, Users } from "lucide-react";
import { toast } from "sonner";
import {
  fetchAssignments,
  deleteAssignment,
  fetchUsersWithScopes,
  type Assignment,
} from "@/lib/api";
import type { UserWithScopes } from "@/lib/api";
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import AssignmentDialog from "@/components/assignment-dialog";

export default function SchedulerAdminPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [users, setUsers] = useState<UserWithScopes[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<Assignment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [assignmentsRes, usersRes] = await Promise.all([
          fetchAssignments(),
          fetchUsersWithScopes(),
        ]);
        if (!cancelled) {
          setAssignments(assignmentsRes.data);
          setUsers(usersRes.data);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const handleDeleteClick = (id: string) => {
    setPendingDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!pendingDeleteId) return;
    setDeleteConfirmOpen(false);
    setDeletingId(pendingDeleteId);
    try {
      await deleteAssignment(pendingDeleteId);
      setAssignments((prev) => prev.filter((a) => a.id !== pendingDeleteId));
      toast.success("Assignment deleted");
    } catch {
      toast.error("Failed to delete assignment");
    } finally {
      setDeletingId(null);
      setPendingDeleteId(null);
    }
  };

  const handleOpenDialog = (assignment: Assignment | null) => {
    setEditingAssignment(assignment);
    setDialogOpen(true);
  };

  const handleCreate = () => {
    setEditingAssignment(null);
    setDialogOpen(true);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const getUserEmail = (userId: string) => {
    return users.find((u) => u.new_id === userId)?.email ?? userId;
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
          <h1 className="text-4xl font-bold text-foreground">Scheduler Admin</h1>
          <p className="text-muted-foreground mt-1">
            Assign users to music or service roles
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" />
          New
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Instrument</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assignments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-16">
                  <Users className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">No assignments yet</p>
                </TableCell>
              </TableRow>
            ) : (
              assignments.map((assignment) => (
                <TableRow key={assignment.id}>
                  <TableCell className="font-medium">{getUserEmail(assignment.user_id)}</TableCell>
                  <TableCell>{formatDate(assignment.event_date)}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                      assignment.type === "music"
                        ? "bg-blue-100 text-blue-800"
                        : "bg-green-100 text-green-800"
                    }`}>
                      {assignment.type === "music" ? <Music className="w-3 h-3" /> : null}
                      {assignment.type}
                    </span>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">{assignment.role || "—"}</TableCell>
                  <TableCell>{assignment.instrument || "—"}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenDialog(assignment)}
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === assignment.id}
                        onClick={() => handleDeleteClick(assignment.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {dialogOpen && (
        <AssignmentDialog
          key={editingAssignment?.id ?? "create"}
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          assignment={editingAssignment}
          users={users.map((u) => ({ id: u.new_id, email: u.email }))}
          onSuccess={() => {
            fetchAssignments().then((data) => setAssignments(data.data));
          }}
        />
      )}

      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete assignment</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. The assignment will be permanently removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
