const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- Video upload types ---

export interface VideoUploadAdmin {
  id: string;
  upload_location: string;
  upload_name: string;
  media_association_date: string;
  speaker_name: string | null;
  reference_text: string | null;
  description: string | null;
  owner_id: string;
  created_on: string;
  updated_on: string | null;
}

// --- Video upload API functions ---

export async function patchVideoUpload(
  id: string,
  data: Partial<VideoUploadAdmin>,
): Promise<VideoUploadAdmin> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update video upload");
  }
  return res.json();
}

export async function createVideoUpload(data: Partial<VideoUploadAdmin>): Promise<VideoUploadAdmin> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create video upload");
  }
  return res.json();
}

export async function deleteVideoUpload(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete video upload");
  }
}

export async function fetchAllVideoUploads(): Promise<{ data: VideoUploadAdmin[]; count: number }> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/`);
  if (!res.ok) {
    throw new Error("Failed to fetch video uploads");
  }
  return res.json();
}
