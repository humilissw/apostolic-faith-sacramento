"use client";

import { useEffect, useRef, useState } from "react";
import { Music, Users, Calendar as CalendarIcon, RefreshCw } from "lucide-react";
import {
  fetchMyAssignments,
  type Assignment,
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

export default function MySchedulerPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMyAssignments();
      setAssignments(data.data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load";
      console.error("my-scheduler load failed:", msg);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const loadRef = useRef(load);
  useEffect(() => {
    loadRef.current();
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
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
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={load}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-12 max-w-6xl">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-foreground">My Scheduler</h1>
          <p className="text-muted-foreground mt-1">
            Your assigned music and service roles
          </p>
        </div>
        <Button onClick={load} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Instrument</TableHead>
              <TableHead>Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assignments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-16">
                  <CalendarIcon className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">No assignments yet</p>
                </TableCell>
              </TableRow>
            ) : (
              assignments
                .sort((a, b) => new Date(a.event_date).getTime() - new Date(b.event_date).getTime())
                .map((assignment) => (
                  <TableRow key={assignment.id}>
                    <TableCell className="font-medium">{formatDate(assignment.event_date)}</TableCell>
                    <TableCell>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                        assignment.type === "music"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-green-100 text-green-800"
                      }`}>
                        {assignment.type === "music" ? <Music className="w-3 h-3" /> : <Users className="w-3 h-3" />}
                        {assignment.type}
                      </span>
                    </TableCell>
                    <TableCell>{assignment.role || "—"}</TableCell>
                    <TableCell>{assignment.instrument || "—"}</TableCell>
                    <TableCell className="max-w-xs truncate">{assignment.notes || "—"}</TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
