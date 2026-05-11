"use client";

import { useEffect, useState } from "react";
import { Plus, Pencil, Trash2, Youtube, Calendar, Film } from "lucide-react";
import { toast } from "sonner";
import {
  deleteVideoUpload,
  fetchAllVideoUploads,
  type VideoUploadAdmin,
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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import VideoUploadDialog from "@/components/video-upload-dialog";

export default function VideoUploadsAdminPage() {
  const [uploads, setUploads] = useState<VideoUploadAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUpload, setEditingUpload] = useState<VideoUploadAdmin | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const timeout = new Promise((_, rej) => setTimeout(() => rej(new Error("Request timed out. Is the API running?")), 15000));
        const res = await Promise.race([fetchAllVideoUploads(), timeout]);
        const data = res as Awaited<ReturnType<typeof fetchAllVideoUploads>>;
        if (!cancelled) setUploads(data.data);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const handleDeleteClick = (id: string) => {
    setPendingDeleteId(id);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!pendingDeleteId) return;
    setDeleteConfirmOpen(false);
    setDeletingId(pendingDeleteId);
    try {
      await deleteVideoUpload(pendingDeleteId);
      setUploads((prev) => prev.filter((u) => u.id !== pendingDeleteId));
      toast.success("Video upload deleted");
    } catch {
      toast.error("Failed to delete video upload");
    } finally {
      setDeletingId(null);
      setPendingDeleteId(null);
    }
  };

  const handleOpenDialog = (upload: VideoUploadAdmin | null) => {
    setEditingUpload(upload);
    setDialogOpen(true);
  };

  const handleCreate = () => {
    setEditingUpload(null);
    setDialogOpen(true);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
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
          <h1 className="text-4xl font-bold text-foreground">Video Upload Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage all video uploads
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" />
          New
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Speaker</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>URL</TableHead>
              <TableHead className="w-24">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {uploads.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-16">
                  <Film className="w-8 h-8 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">No video uploads yet</p>
                </TableCell>
              </TableRow>
            ) : (
              uploads.map((upload) => (
                <TableRow key={upload.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {upload.upload_name}
                  </TableCell>
                  <TableCell>{upload.speaker_name || "—"}</TableCell>
                  <TableCell>
                    <span className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      {formatDate(upload.media_association_date)}
                    </span>
                  </TableCell>
                  <TableCell>
                    {upload.upload_location && (
                      <a
                        href={upload.upload_location}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline inline-flex items-center gap-1 text-sm"
                      >
                        <Youtube className="w-3 h-3" />
                        Link
                      </a>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenDialog(upload)}
                      >
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === upload.id}
                        onClick={() => handleDeleteClick(upload.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {dialogOpen && (
        <VideoUploadDialog
          key={editingUpload?.id ?? "create"}
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          upload={editingUpload}
          onSuccess={() => {
            fetchAllVideoUploads().then((data) => setUploads(data.data));
          }}
        />
      )}

      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete video upload</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. The video upload will be permanently removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
