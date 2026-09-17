import { API_BASE, API_V1 } from "./base";

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

// --- YouTube sync ---

export interface YouTubeSyncResult {
  message: string;
  media_created: number;
  video_uploads_created: number;
  skipped_existing: number;
  skipped_live: number;
  total_channel_videos: number;
}

/**
 * Sync the connected YouTube account's uploaded videos (live videos excluded)
 * into the app. The backend pulls the channel uploads via the configured
 * YouTube integration and only inserts videos that are not yet present.
 */
export async function syncYouTubeVideos(): Promise<YouTubeSyncResult> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/media/sync-youtube`, {
    method: "POST",
  });
  if (!res.ok) {
    let detail = "Failed to sync YouTube videos";
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : detail;
    } catch {
      /* keep default message */
    }
    throw new Error(detail);
  }
  return res.json();
}
