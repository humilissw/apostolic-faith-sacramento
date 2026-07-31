"use client";

import { useEffect, useRef, useState } from "react";
import { Music, Users, Calendar as CalendarIcon, RefreshCw, Clock, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import {
  fetchMyAssignments,
  fetchMyTimeOffRequests,
  type Assignment,
  type TimeOffRequest,
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
  const [timeOffRequests, setTimeOffRequests] = useState<TimeOffRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [assgnRes, toRes] = await Promise.all([
        fetchMyAssignments(),
        fetchMyTimeOffRequests(),
      ]);
      setAssignments(assgnRes.data);
      setTimeOffRequests(toRes.data);
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

      <div className="mt-8">
        <h2 className="text-2xl font-bold text-foreground mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Time Off Requests
        </h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {timeOffRequests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center py-16">
                    <Clock className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
                    <p className="text-muted-foreground">No time-off requests</p>
                  </TableCell>
                </TableRow>
              ) : (
                timeOffRequests
                  .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                  .map((req) => (
                    <TableRow key={req.id}>
                      <TableCell className="font-medium">
                        {formatDate(req.date)}
                      </TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                          req.status === "approved"
                            ? "bg-green-100 text-green-800"
                            : req.status === "declined"
                            ? "bg-red-100 text-red-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}>
                          {req.status === "approved"
                            ? <CheckCircle2 className="w-3 h-3" />
                            : req.status === "declined"
                            ? <XCircle className="w-3 h-3" />
                            : <AlertCircle className="w-3 h-3" />}
                          {req.status.charAt(0).toUpperCase() + req.status.slice(1)}
                        </span>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">{req.notes || "—"}</TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
