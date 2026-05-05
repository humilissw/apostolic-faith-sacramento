"use client";

import { useEffect, useState } from "react";
import { Pencil, Trash2, ShieldCheck } from "lucide-react";
import {
  fetchUsersWithScopes,
  removeUserScopes,
  type UserWithScopes,
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
import UserScopeDialog from "@/components/user-scope-dialog";

export default function UsersAdminPage() {
  const [users, setUsers] = useState<UserWithScopes[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<{ id: string; email: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [removingUserId, setRemovingUserId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await fetchUsersWithScopes();
        if (!cancelled) setUsers(data.data);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const handleRemoveScopes = async (id: string) => {
    if (!confirm("Remove all scopes from this user?")) return;
    setRemovingUserId(id);
    try {
      await removeUserScopes(id);
      setUsers((prev) =>
        prev.map((u) => (u.new_id === id ? { ...u, assigned_scopes: [] } : u)),
      );
    } catch {
      setError("Failed to remove scopes");
    } finally {
      setRemovingUserId(null);
    }
  };

  const handleOpenDialog = (user: UserWithScopes) => {
    setEditingUser({ id: user.new_id, email: user.email });
    setDialogOpen(true);
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
          <h1 className="text-4xl font-bold text-foreground">User Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage user permissions and scopes
          </p>
        </div>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Superuser</TableHead>
              <TableHead>Scopes</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.new_id}>
                <TableCell className="font-medium">{user.email}</TableCell>
                <TableCell>
                  <span
                    className={
                      user.is_active
                        ? "text-green-600 text-sm font-medium"
                        : "text-gray-400 text-sm"
                    }
                  >
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                </TableCell>
                <TableCell>
                  {user.is_superuser ? (
                    <span className="flex items-center gap-1 text-amber-600 text-sm">
                      <ShieldCheck className="w-4 h-4" /> Yes
                    </span>
                  ) : (
                    <span className="text-gray-400 text-sm">No</span>
                  )}
                </TableCell>
                <TableCell>
                  {user.is_superuser ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                      <ShieldCheck className="w-3 h-3" /> ALL SCOPES
                    </span>
                  ) : user.assigned_scopes.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {user.assigned_scopes.map((scope) => (
                        <span
                          key={scope}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {scope}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-gray-400 text-sm">Default (api:all)</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleOpenDialog(user)}
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={removingUserId === user.new_id}
                      onClick={() => handleRemoveScopes(user.new_id)}
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

      <UserScopeDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        userId={editingUser?.id ?? null}
        userEmail={editingUser?.email ?? ""}
        onSuccess={() => {
          setDialogOpen(false);
          fetchUsersWithScopes().then((data) => setUsers(data.data));
        }}
      />
    </div>
  );
}
