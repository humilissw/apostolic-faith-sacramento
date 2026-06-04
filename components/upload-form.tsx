"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { fetchWithAuth } from "@/lib/api";

const API_V1 = "api/v1";

interface UploadFormProps {
  onSuccess: () => void;
}

export default function UploadForm({ onSuccess }: UploadFormProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadLocation, setUploadLocation] = useState("");
  const [uploadName, setUploadName] = useState("");
  const [speakerName, setSpeakerName] = useState("");
  const [referenceText, setReferenceText] = useState("");
  const [description, setDescription] = useState("");
  const [mediaDate, setMediaDate] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();

    setUploading(true);
    setError(null);

    try {
      const res = await fetchWithAuth(
        `${process.env.NEXT_PUBLIC_API_URL}${API_V1}/video-uploads/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            upload_location: uploadLocation.trim(),
            upload_name: uploadName.trim(),
            media_association_date: new Date(mediaDate).toISOString(),
            ...(speakerName && { speaker_name: speakerName }),
            ...(referenceText && { reference_text: referenceText }),
            ...(description && { description }),
          }),
        },
      );

      if (!res.ok) {
        const body = await res.text();
        throw new Error(body || "Upload failed");
      }

      setUploadLocation("");
      setUploadName("");
      setSpeakerName("");
      setReferenceText("");
      setDescription("");
      setMediaDate("");
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 px-1">
      {error && <p className="text-red-600 text-sm">{error}</p>}

      <div>
        <Label htmlFor="u-video_url" className="text-sm mb-1">
          Video URL *
        </Label>
        <Input
          id="u-video_url"
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={uploadLocation}
          onChange={(e) => setUploadLocation(e.target.value)}
          required
        />
      </div>

      <div>
        <Label htmlFor="u-upload_name" className="text-sm mb-1">
          Video Title *
        </Label>
        <Input
          id="u-upload_name"
          type="text"
          placeholder="Enter video title"
          value={uploadName}
          onChange={(e) => setUploadName(e.target.value)}
          required
        />
      </div>

      <div>
        <Label htmlFor="u-media_date" className="text-sm mb-1">
          Service Date *
        </Label>
        <Input
          id="u-media_date"
          type="date"
          required
          value={mediaDate}
          onChange={(e) => setMediaDate(e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="u-speaker" className="text-sm mb-1">
          Speaker
        </Label>
        <Input
          id="u-speaker"
          type="text"
          placeholder="Speaker name"
          value={speakerName}
          onChange={(e) => setSpeakerName(e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="u-reference" className="text-sm mb-1">
          Bible Reference
        </Label>
        <Input
          id="u-reference"
          type="text"
          placeholder="e.g. John 3:16"
          value={referenceText}
          onChange={(e) => setReferenceText(e.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="u-description" className="text-sm mb-1">
          Description
        </Label>
        <textarea
          id="u-description"
          className="w-full border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-20"
          placeholder="Video description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <Button className="w-full" type="submit" disabled={uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </Button>
    </form>
  );
}
