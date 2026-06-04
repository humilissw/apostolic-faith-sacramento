"use client";

import { useEffect, useState, useRef, useCallback, useMemo } from "react";
import {
  Pencil,
  Trash2,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  UserPlus,
  Search,
  X,
} from "lucide-react";
import {
  fetchUsersWithScopes,
  deleteUser,
  deleteUsers,
  type UserWithScopes,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import UserScopeDialog from "@/components/user-scope-dialog";
import CreateUserDialog from "@/components/create-user-dialog";

const PAGE_SIZE = 50;
const SCROLL_THRESHOLD = 100;

export default function UsersAdminPage() {
  const [users, setUsers] = useState<UserWithScopes[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<{
    id: string;
    email: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [removingUserId, setRemovingUserId] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<Set<string>>(new Set());
  const [total, setTotal] = useState(0);
  const hasMore = total > 0 && users.length < total;

  // Search/filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [filterScopes, setFilterScopes] = useState<string[]>([]);
  const [scopeFilterOpen, setScopeFilterOpen] = useState(false);
  const scopeFilterRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!scopeFilterOpen) return;
    const handler = (e: MouseEvent) => {
      if (scopeFilterRef.current && !scopeFilterRef.current.contains(e.target as Node)) {
        setScopeFilterOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [scopeFilterOpen]);

  type SortDir = "asc" | "desc";
  const [sortCol, setSortCol] = useState<number | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sortedUsers = useMemo(() => {
    if (sortCol === null) return users;
    const col = sortCol;
    const dir = sortDir === "asc" ? 1 : -1;
    return [...users].sort((a, b) => {
      let cmp = 0;
      if (col === 1) cmp = a.email.localeCompare(b.email);
      else if (col === 2)
        cmp = a.is_active === b.is_active ? 0 : a.is_active ? -1 : 1;
      else if (col === 3) {
        const aSu = a.assigned_scopes.includes("superuser") ? 1 : 0;
        const bSu = b.assigned_scopes.includes("superuser") ? 1 : 0;
        cmp = aSu - bSu;
      } else if (col === 4) {
        const aS = a.assigned_scopes.join(",");
        const bS = b.assigned_scopes.join(",");
        cmp = aS.localeCompare(bS);
      }
      return dir * cmp;
    });
  }, [users, sortCol, sortDir]);

  // All unique scopes from current users
  const allScopes = useMemo(() => {
    const s = new Set<string>();
    users.forEach((u) => u.assigned_scopes.forEach((sc) => s.add(sc)));
    return Array.from(s).sort();
  }, [users]);

  // Apply search + scope filters to sorted users
  const filteredUsers = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    let list = sortedUsers;
    if (q) {
      list = list.filter((u) =>
        u.email.toLowerCase().includes(q)
        || (u.full_name && u.full_name.toLowerCase().includes(q))
        || u.assigned_scopes.some((sc) => sc.toLowerCase().includes(q))
      );
    }
    if (filterScopes.length > 0) {
      list = list.filter((u) =>
        filterScopes.every((fs) => u.assigned_scopes.includes(fs))
      );
    }
    return list;
  }, [sortedUsers, searchQuery, filterScopes]);

  const scrollBodyRef = useRef<HTMLDivElement>(null);

  const colWidths = useMemo(() => [
    { width: "3rem", minWidth: "3rem" },
    { width: "25rem", minWidth: "0" },
    { width: "8rem", minWidth: "8rem" },
    { width: "6rem", minWidth: "6rem" },
    { width: "16rem", minWidth: "16rem" },
    { width: "6rem", minWidth: "6rem" },
  ], []);

  const getBodyCellStyle = useCallback(
    (colIndex: number): React.CSSProperties => colWidths[colIndex] ?? {},
    [colWidths],
  );

  const loadPage = useCallback(async (skip: number) => {
    const data = await fetchUsersWithScopes(skip, PAGE_SIZE);
    setUsers((prev) => (skip === 0 ? data.data : [...prev, ...data.data]));
    setTotal(data.count);
    return data.count;
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function init() {
      try {
        const count = await loadPage(0);
        if (!cancelled) {
          setTotal(count);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load");
      }
    }
    init();
    return () => {
      cancelled = true;
    };
  }, [loadPage]);

  const doLoadMore = useCallback(async () => {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    const nextSkip = users.length;
    try {
      await loadPage(nextSkip);
    } catch {
      setError("Failed to load more users");
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, users.length, loadPage]);

  const handleScroll = useCallback(() => {
    if (scrollBodyRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollBodyRef.current;
      if (
        scrollTop + clientHeight + SCROLL_THRESHOLD >= scrollHeight &&
        !loadingMore &&
        hasMore
      ) {
        doLoadMore();
      }
    }
  }, [loadingMore, hasMore, doLoadMore]);

  const toggleUser = (id: string) => {
    setSelectedUsers((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (selectedUsers.size === filteredUsers.length) setSelectedUsers(new Set());
    else setSelectedUsers(new Set(filteredUsers.map((u) => u.id)));
  };

  const handleRemoveUser = async (id: string) => {
    if (!confirm("Delete this user from the application?")) return;
    setRemovingUserId(id);
    try {
      await deleteUser(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
      setSelectedUsers((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } catch {
      setError("Failed to delete user");
    } finally {
      setRemovingUserId(null);
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedUsers.size} selected users?`)) return;
    const ids = Array.from(selectedUsers);
    setSelectedUsers(new Set());
    try {
      await deleteUsers(ids);
      setUsers((prev) => prev.filter((u) => !ids.includes(u.id)));
    } catch {
      setError("Failed to delete users");
    }
  };

  const handleOpenDialog = (user: UserWithScopes) => {
    setEditingUser({ id: user.id, email: user.email });
    setDialogOpen(true);
  };

  const isAllSelected = filteredUsers.length > 0 && selectedUsers.size === filteredUsers.length;
  const isIndeterminate =
    selectedUsers.size > 0 && selectedUsers.size < filteredUsers.length;

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
          <h1 className="text-4xl font-bold text-foreground">
            User Management
          </h1>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Create User
        </Button>
        {selectedUsers.size > 0 && (
          <Button variant="destructive" onClick={handleBulkDelete}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete selected ({selectedUsers.size})
          </Button>
        )}
      </div>

      {/* Search and filter bar */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by email, name, or scope..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-9 h-9 border rounded-md px-3 text-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <div className="relative">
          <button
            ref={scopeFilterRef}
            onClick={() => setScopeFilterOpen(!scopeFilterOpen)}
            className="h-9 px-3 border rounded-md text-sm flex items-center gap-1.5"
          >
            <ShieldCheck className="w-4 h-4" />
            Scopes
            {filterScopes.length > 0 && (
              <span className="flex items-center justify-center w-4 h-4 rounded-full bg-blue-600 text-white text-[10px]">
                {filterScopes.length}
              </span>
            )}
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
          {scopeFilterOpen && (
            <div className="absolute right-0 mt-1 w-56 bg-popover border rounded-lg shadow-lg z-20 p-2 space-y-1">
              {allScopes.length === 0 && (
                <p className="text-xs text-muted-foreground px-2 py-1">No scopes found</p>
              )}
              {allScopes.map((scope) => (
                <label key={scope} className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-muted cursor-pointer text-sm">
                  <input
                    type="checkbox"
                    checked={filterScopes.includes(scope)}
                    onChange={() => {
                      setFilterScopes((prev) =>
                        prev.includes(scope)
                          ? prev.filter((s) => s !== scope)
                          : [...prev, scope]
                      );
                    }}
                    className="h-3.5 w-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  {scope}
                </label>
              ))}
              {filterScopes.length > 0 && (
                <button
                  onClick={() => setFilterScopes([])}
                  className="w-full text-left px-2 py-1.5 text-xs text-red-600 hover:bg-red-50 rounded"
                >
                  Clear all
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="relative h-[calc(100vh-340px)] overflow-hidden flex flex-col">
        <Card className="flex flex-col h-full">
          {/* Header — fixed table, never scrolls */}
          <div className="w-full shrink-0">
            <Table className="w-full" style={{ tableLayout: "fixed" }}>
              <TableHeader>
                <TableRow>
                  <TableCell className="bg-card border-b sticky top-0 z-10 shrink-0 w-[3rem]">
                    <input
                      type="checkbox"
                      checked={isAllSelected}
                      ref={(el) => {
                        if (el) {
                          el.indeterminate = isIndeterminate;
                        }
                      }}
                      onChange={toggleAll}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </TableCell>
                  {[
                    { col: 1, label: "Email", w: "w-100" },
                    { col: 2, label: "Status", w: "w-32" },
                    { col: 3, label: "Superuser", w: "w-24" },
                    { col: 4, label: "Scopes", w: "w-64" },
                  ].map(({ col, label, w }) => {
                    const active = sortCol === col;
                    const Icon =
                      active && sortDir === "asc"
                        ? ChevronUp
                        : active && sortDir === "desc"
                          ? ChevronDown
                          : ArrowUpDown;
                    return (
                      <TableCell
                        key={col}
                        className={`bg-card border-b sticky top-0 z-10 shrink-0 cursor-pointer select-none hover:bg-muted/50 transition-colors ${w}`}
                        onClick={() => {
                          if (sortCol === col)
                            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
                          else {
                            setSortCol(col);
                            setSortDir("asc");
                          }
                        }}
                      >
                        <div className="flex items-center justify-center gap-1">
                          <span>{label}</span>
                          <Icon className="w-3 h-3 opacity-50" />
                        </div>
                      </TableCell>
                    );
                  })}
                  <TableCell className="bg-card border-b sticky top-0 z-10 shrink-0 w-[6rem]">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHeader>
            </Table>
          </div>
          <p className="px-4 py-2 text-sm text-muted-foreground shrink-0">
            Displaying {filteredUsers.length} of {total} Users
          </p>
          {/* Scrollable body — width synced to header */}
          <div
            ref={scrollBodyRef}
            className="overflow-y-auto flex-1"
            onScroll={handleScroll}
          >
            <Table className="w-full" style={{ tableLayout: "fixed" }}>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell
                      style={getBodyCellStyle(0)}
                      className="shrink-0 w-12"
                    >
                      <input
                        type="checkbox"
                        checked={selectedUsers.has(user.id)}
                        onChange={() => toggleUser(user.id)}
                        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </TableCell>
                    <TableCell
                      style={getBodyCellStyle(1)}
                      className="font-medium"
                    >
                      <span
                        className="block truncate hover:max-w-none hover:text-foreground transition-all duration-150 cursor-pointer"
                        style={{ maxWidth: "30ch" }}
                      >
                        {user.email}
                      </span>
                    </TableCell>
                    <TableCell style={getBodyCellStyle(2)}>
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
                    <TableCell style={getBodyCellStyle(3)}>
                      {user.assigned_scopes.includes("superuser") ? (
                        <span className="flex items-center gap-1 text-amber-600 text-sm">
                          <ShieldCheck className="w-4 h-4" /> Yes
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">No</span>
                      )}
                    </TableCell>
                    <TableCell style={getBodyCellStyle(4)}>
                      {user.assigned_scopes.includes("superuser") ? (
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
                        <span className="text-gray-400 text-sm">
                          Default (api:all)
                        </span>
                      )}
                    </TableCell>
                    <TableCell style={getBodyCellStyle(5)}>
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
                          disabled={removingUserId === user.id}
                          onClick={() => handleRemoveUser(user.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>

      <UserScopeDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        userId={editingUser?.id ?? null}
        userEmail={editingUser?.email ?? ""}
        onSuccess={async () => {
          setDialogOpen(false);
          try {
            const data = await fetchUsersWithScopes(0, PAGE_SIZE);
            setTotal(data.count);
            setUsers(data.data);
          } catch {
            setError("Failed to refresh users");
          }
        }}
      />

      <CreateUserDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={async () => {
          try {
            const data = await fetchUsersWithScopes(0, PAGE_SIZE);
            setTotal(data.count);
            setUsers(data.data);
          } catch {
            setError("Failed to refresh users after creation");
          }
        }}
      />
    </div>
  );
}
