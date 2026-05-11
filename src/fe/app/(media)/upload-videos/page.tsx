"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { fetchWithAuth } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

export default function UploadVideosPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadLocation, setUploadLocation] = useState("");
  const [uploadName, setUploadName] = useState("");
  const [speakerName, setSpeakerName] = useState("");
  const [referenceText, setReferenceText] = useState("");
  const [description, setDescription] = useState("");
  const [mediaDate, setMediaDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();

    const valid = (e.target as HTMLFormElement).checkValidity();
    if (!valid) return;

    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      const res = await fetchWithAuth(
        `${API_BASE}${API_V1}/video-uploads/`,
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

      setSuccess(true);
      setUploadLocation("");
      setUploadName("");
      setSpeakerName("");
      setReferenceText("");
      setDescription("");
      setMediaDate("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="">
      <div className="flex flex-col justify-center bg-white">
        <div className="flex justify-center items-center h-50 bg-[url('../public/media.jpg')] bg-cover bg-center md:h-100 lg:h-100">
          <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
            Upload a Video
          </h1>
        </div>

        <div className="flex justify-center px-6 py-10">
          <form
            onSubmit={handleSubmit}
            className="bg-white border border-zinc-200 rounded-xl p-10 w-full max-w-lg shadow-sm"
          >
            {error && (
              <p className="text-red-600 text-sm mb-4 text-center">{error}</p>
            )}
            {success && (
              <p className="text-green-600 text-sm mb-4 text-center">
                Video uploaded successfully!
              </p>
            )}

            <div className="mb-5">
              <Label htmlFor="video_url" className="text-base mb-2">
                Video URL (YouTube, Vimeo, etc.) *
              </Label>
              <Input
                id="video_url"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                value={uploadLocation}
                onChange={(e) => setUploadLocation(e.target.value)}
                required
              />
            </div>

            <div className="mb-5">
              <Label htmlFor="upload_name" className="text-base mb-2">
                Video Title *
              </Label>
              <Input
                id="upload_name"
                type="text"
                placeholder="Enter video title"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
                required
              />
            </div>

            <div className="mb-5">
              <Label htmlFor="media_date" className="text-base mb-2">
                Service Date *
              </Label>
              <Input
                id="media_date"
                type="date"
                required
                value={mediaDate}
                onChange={(e) => setMediaDate(e.target.value)}
              />
            </div>

            <div className="mb-5">
              <Label htmlFor="speaker" className="text-base mb-2">
                Speaker
              </Label>
              <Input
                id="speaker"
                type="text"
                placeholder="Speaker name"
                value={speakerName}
                onChange={(e) => setSpeakerName(e.target.value)}
              />
            </div>

            <div className="mb-5">
              <Label htmlFor="reference" className="text-base mb-2">
                Bible Reference
              </Label>
              <Input
                id="reference"
                type="text"
                placeholder="e.g. John 3:16"
                value={referenceText}
                onChange={(e) => setReferenceText(e.target.value)}
              />
            </div>

            <div className="mb-8">
              <Label htmlFor="description" className="text-base mb-2">
                Description
              </Label>
              <textarea
                id="description"
                className="border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-25"
                placeholder="Video description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <Button
              className="w-full text-base py-5"
              type="submit"
              disabled={uploading}
            >
              {uploading ? "Uploading..." : "Upload Video"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
