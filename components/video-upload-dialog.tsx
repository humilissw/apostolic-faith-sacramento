"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { patchVideoUpload, createVideoUpload, type VideoUploadAdmin } from "@/lib/api";
import { toast } from "sonner";

interface VideoUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  upload: VideoUploadAdmin | null;
  onSuccess: () => void;
}

export default function VideoUploadDialog({
  open,
  onOpenChange,
  upload,
  onSuccess,
}: VideoUploadDialogProps) {
  const [uploadLocation, setUploadLocation] = useState(
    upload?.upload_location ?? "",
  );
  const [uploadName, setUploadName] = useState(upload?.upload_name ?? "");
  const [mediaDate, setMediaDate] = useState(
    upload?.media_association_date
      ? new Date(upload.media_association_date).toISOString().split("T")[0]
      : "",
  );
  const [speakerName, setSpeakerName] = useState(upload?.speaker_name ?? "");
  const [referenceText, setReferenceText] = useState(
    upload?.reference_text ?? "",
  );
  const [description, setDescription] = useState(upload?.description ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const handleSave = async () => {
    const trimmedName = uploadName.trim();
    const trimmedLocation = uploadLocation.trim();
    if (!trimmedName || !trimmedLocation || !mediaDate) return;
    setSaving(true);
    setError(null);
    try {
      const payload = {
        upload_location: trimmedLocation,
        upload_name: trimmedName,
        media_association_date: new Date(mediaDate).toISOString(),
        speaker_name: speakerName || null,
        reference_text: referenceText || null,
        description: description || null,
      };

      if (!upload) {
        await createVideoUpload(payload);
        toast.success("Video upload created");
      } else {
        await patchVideoUpload(upload.id, payload);
        toast.success("Video upload updated");
      }
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const isCreate = !upload;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isCreate ? "New Video Upload" : "Edit Video Upload"}
          </DialogTitle>
          <DialogDescription>
            {isCreate
              ? "Add a new video upload entry"
              : `Edit ${upload?.upload_name}`}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="v-title" className="text-sm">
              Title *
            </Label>
            <Input
              id="v-title"
              value={uploadName}
              onChange={(e) => setUploadName(e.target.value)}
              placeholder="Video title"
              required
            />
          </div>

          <div>
            <Label htmlFor="v-url" className="text-sm">
              Video URL *
            </Label>
            <Input
              id="v-url"
              type="url"
              value={uploadLocation}
              onChange={(e) => setUploadLocation(e.target.value)}
              placeholder="https://youtube.com/..."
              required
            />
          </div>

          <div>
            <Label htmlFor="v-date" className="text-sm">
              Service Date *
            </Label>
            <Input
              id="v-date"
              type="date"
              value={mediaDate}
              onChange={(e) => setMediaDate(e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="v-speaker" className="text-sm">
              Speaker
            </Label>
            <Input
              id="v-speaker"
              value={speakerName}
              onChange={(e) => setSpeakerName(e.target.value)}
              placeholder="Speaker name"
            />
          </div>

          <div>
            <Label htmlFor="v-reference" className="text-sm">
              Bible Reference
            </Label>
            <Input
              id="v-reference"
              value={referenceText}
              onChange={(e) => setReferenceText(e.target.value)}
              placeholder="e.g. John 3:16"
            />
          </div>

          <div>
            <Label htmlFor="v-description" className="text-sm">
              Description
            </Label>
            <textarea
              id="v-description"
              className="w-full border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-20"
              placeholder="Video description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {error && <p className="text-red-600 text-sm">{error}</p>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !uploadName || !uploadLocation || !mediaDate}
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
