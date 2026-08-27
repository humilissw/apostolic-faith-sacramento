const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- Scheduler / Assignment types ---

export interface Assignment {
  id: string;
  user_id: string;
  user_email: string;
  user_full_name: string | null;
  event_date: string;
  type: "music" | "service";
  role: string;
  instrument: string | null;
  notes: string | null;
  group_leader: boolean;
  created_on: string;
  updated_on: string | null;
}

export interface AssignmentConflict {
  id: string;
  type: string;
  role: string;
  event_date: string;
}

export interface AssignmentCreateInput {
  user_id: string;
  event_date: string;
  type: "music" | "service";
  role?: string;
  instrument?: string | null;
  notes?: string | null;
}

export interface AssignmentUpdateInput {
  event_date?: string;
  type?: "music" | "service";
  role?: string;
  instrument?: string | null;
  notes?: string | null;
  user_id?: string;
}

export interface BulkAssignEntry {
  user_id: string;
  role: string;
  instrument: string | null;
  notes: string | null;
  group_leader: boolean;
}

export interface BulkAssignRequest {
  event_date: string;
  type: "music" | "service";
  entries: BulkAssignEntry[];
}

export interface BulkAssignConflict {
  user_id: string;
  message: string;
  conflicts?: AssignmentConflict[];
}

export interface BulkAssignResponse {
  created: Assignment[];
  conflicts: BulkAssignConflict[];
}

export interface AssignmentsResponse {
  data: Assignment[];
  count: number;
}

// --- Time-off request types ---

export interface TimeOffRequest {
  id: string;
  user_id: string;
  date: string;
  status: "pending" | "approved" | "declined";
  notes: string | null;
  created_on: string;
  updated_on: string | null;
}

export interface TimeOffRequestsResponse {
  data: TimeOffRequest[];
  count: number;
}

// --- Scheduler API functions ---

export async function fetchAssignments(): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/`);
  if (!res.ok) {
    throw new Error("Failed to fetch assignments");
  }
  return res.json();
}

export async function fetchAssignment(id: string): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch assignment");
  }
  return res.json();
}

export async function createAssignment(data: AssignmentCreateInput): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    if (res.status === 409) {
      const detail = JSON.parse(body);
      throw new Error(detail.detail?.message || detail.detail || "Conflict: user already has an assignment on this date.");
    }
    throw new Error(body || "Failed to create assignment");
  }
  return res.json();
}

export async function updateAssignment(id: string, data: AssignmentUpdateInput): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update assignment");
  }
  return res.json();
}

export async function deleteAssignment(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete assignment");
  }
}

export async function bulkAssignAssignments(data: BulkAssignRequest): Promise<BulkAssignResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/bulk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to bulk assign assignments");
  }
  return res.json();
}

export async function fetchMyAssignments(): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/my-assignments`);
  if (!res.ok) {
    throw new Error("Failed to fetch my assignments");
  }
  return res.json();
}

export async function fetchCalendarAssignments(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/calendar?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch calendar assignments");
  }
  return res.json();
}

export async function fetchCalendarWithNames(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/calendar-with-names?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch calendar with names");
  }
  return res.json();
}

export async function fetchMyCalendar(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/my-calendar?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch my calendar");
  }
  return res.json();
}

// --- Time-off request API functions ---

export async function createTimeOffRequest(data: { date: string; notes?: string | null }): Promise<TimeOffRequest> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/time-off-request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create time-off request");
  }
  return res.json();
}

export async function fetchMyTimeOffRequests(): Promise<TimeOffRequestsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/time-off-requests`);
  if (!res.ok) {
    throw new Error("Failed to fetch time-off requests");
  }
  return res.json();
}

export async function approveTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}/approve`,
    { method: "PATCH" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to approve time-off request");
  }
}

export async function declineTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}/decline`,
    { method: "PATCH" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to decline time-off request");
  }
}

export async function deleteTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete time-off request");
  }
}

export async function fetchTimeOffByDateRange(start: string, end: string): Promise<TimeOffRequestsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch time-off requests");
  }
  return res.json();
}
