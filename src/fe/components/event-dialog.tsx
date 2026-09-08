"use client";

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field, FieldGroup } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { createEvent, updateEvent, uploadEventFlyer, deleteEventFlyer, flyerImageUrl, parseServerDate, type Event } from "@/lib/api"
import { toast } from "sonner"

interface EventDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  event: Event | null;
  onSuccess: () => void;
}

// Events are stored/displayed in the church's local timezone (see events-admin page).
const EVENT_TIME_ZONE = "America/Los_Angeles";

function zonedOffsetMs(zone: string, timestamp: number): number {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: zone,
    hourCycle: "h23",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).formatToParts(new Date(timestamp));
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    Number(parts.find((p) => p.type === type)?.value ?? "0");
  const asUtc = Date.UTC(
    get("year"),
    get("month") - 1,
    get("day"),
    get("hour"),
    get("minute"),
    get("second"),
  );
  return asUtc - (timestamp - (timestamp % 1000));
}

// Convert a wall-clock "yyyy-MM-dd" + "HH:mm" in EVENT_TIME_ZONE to a UTC ISO string.
function fromZonedTime(dateStr: string, timeStr: string): string {
  const [year, month, day] = dateStr.split("-").map(Number);
  const [hour, minute] = timeStr.split(":").map(Number);
  const guess = Date.UTC(year, month - 1, day, hour, minute);
  // Two-pass offset lookup so DST transitions resolve correctly.
  const firstPass = guess - zonedOffsetMs(EVENT_TIME_ZONE, guess);
  return new Date(guess - zonedOffsetMs(EVENT_TIME_ZONE, firstPass)).toISOString();
}

// "yyyy-MM-dd" input value for an ISO timestamp, viewed in EVENT_TIME_ZONE.
function toInputDateValue(isoString: string): string {
  const date = parseServerDate(isoString);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: EVENT_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

// "HH:mm" input value for an ISO timestamp, viewed in EVENT_TIME_ZONE.
function toTimeInputValue(isoString: string): string {
  const date = parseServerDate(isoString);
  if (Number.isNaN(date.getTime())) return "";
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: EVENT_TIME_ZONE,
    hourCycle: "h23",
    hour: "2-digit",
    minute: "2-digit",
  }).formatToParts(date);
  const hour = (parts.find((p) => p.type === "hour")?.value ?? "00").padStart(2, "0");
  const minute = (parts.find((p) => p.type === "minute")?.value ?? "00").padStart(2, "0");
  return `${hour}:${minute}`;
}

export function EventDialog({
  open,
  onOpenChange,
  event,
  onSuccess,
}: EventDialogProps) {
  const [eventTitle, setEventTitle] = useState(event?.title ?? "");
  const [eventDescription, setEventDescription] = useState(event?.description ?? "");
  const [eventDate, setEventDate] = useState(
    event?.date ? toInputDateValue(event.date) : "",
  );
  // Separate end date lets an event span a range of days; defaults to the start date.
  const [eventEndDate, setEventEndDate] = useState(
    event?.end_time ? toInputDateValue(event.end_time) : "",
  );
  const [eventStartTime, setEventStartTime] = useState(
    event?.start_time ? toTimeInputValue(event.start_time) : "",
  );
  const [eventEndTime, setEventEndTime] = useState(
    event?.end_time ? toTimeInputValue(event.end_time) : "",
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flyerFile, setFlyerFile] = useState<File | null>(null);
  const [removeFlyer, setRemoveFlyer] = useState(false);

  // Re-seed the form whenever the dialog opens or switches events, so state
  // is never stale if the dialog stays mounted between edits. Adjusting state
  // during render (not in an effect) per React's "reset state on prop change".
  const seedKey = `${open ? "open" : "closed"}:${event?.id ?? "new"}`;
  const [prevSeedKey, setPrevSeedKey] = useState(seedKey);
  if (seedKey !== prevSeedKey) {
    setPrevSeedKey(seedKey);
    if (open) {
      setEventTitle(event?.title ?? "");
      setEventDescription(event?.description ?? "");
      setEventDate(event?.date ? toInputDateValue(event.date) : "");
      setEventEndDate(event?.end_time ? toInputDateValue(event.end_time) : "");
      setEventStartTime(event?.start_time ? toTimeInputValue(event.start_time) : "");
      setEventEndTime(event?.end_time ? toTimeInputValue(event.end_time) : "");
      setError(null);
      setFlyerFile(null);
      setRemoveFlyer(false);
    }
  }

  const flyerSrc = !removeFlyer ? flyerImageUrl(event?.flyer_url ?? null) : null;
  const flyerPreviewUrl = flyerFile ? URL.createObjectURL(flyerFile) : flyerSrc;

  const handleSave = async () => {
    const trimmedTitle = eventTitle.trim();
    const trimmedDescription = eventDescription.trim();
    if (!trimmedTitle || !trimmedDescription || !eventDate || !eventStartTime || !eventEndTime) {
      setError("One or more fields are empty");
      return;
    }

    const effectiveEndDate = eventEndDate || eventDate;
    if (effectiveEndDate < eventDate) {
      setError("End date must be on or after the start date");
      return;
    }

    const start = fromZonedTime(eventDate, eventStartTime);
    const end = fromZonedTime(effectiveEndDate, eventEndTime);
    if (new Date(end).getTime() <= new Date(start).getTime()) {
      setError(
        effectiveEndDate === eventDate
          ? "End time must be after start time"
          : "End date and time must be after the start",
      );
      return;
    }
    const date = fromZonedTime(eventDate, "00:00");

    setSaving(true);
    setError(null);
    try {
      const payload = {
        title: trimmedTitle,
        description: trimmedDescription,
        date,
        start_time: start,
        end_time: end,
      };
      if (!event) {
        const created = await createEvent(payload);
        if (flyerFile) {
          await uploadEventFlyer(created.id, flyerFile);
        }
        toast.success("Event created");
      } else {
        await updateEvent(event.id, payload);
        if (flyerFile) {
          await uploadEventFlyer(event.id, flyerFile);
        } else if (removeFlyer && event.flyer_url) {
          await deleteEventFlyer(event.id);
        }
        toast.success("Event updated");
      }
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* The form must live INSIDE DialogContent: Radix portals the content to
          document.body, so a form wrapping DialogContent would be left behind
          and the submit button would no longer be part of it — clicking Save
          would do nothing. */}
      <DialogContent className="sm:max-w-sm">
        <form
          className="contents"
          onSubmit={(e) => {
            e.preventDefault();
            void handleSave();
          }}
        >
          <DialogHeader>
            <DialogTitle>{event ? "Edit Event" : "Add Event"}</DialogTitle>
            <DialogDescription>
              Fill in the details for the event.
            </DialogDescription>
          </DialogHeader>
          <FieldGroup>
            <Field>
              <Label htmlFor="title-1">Event Title</Label>
              <Input id="title-1" name="title" value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} required/>
            </Field>
            <Field>
              <Label htmlFor="description-1">Description</Label>
              <textarea className="w-full border border-zinc-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-20" id="description-1" name="description" value={eventDescription} onChange={(e) => setEventDescription(e.target.value)} required/>
            </Field>
            <Field>
              <Label htmlFor="date-1">Date</Label>
              <Input
                id="date-1"
                name="date"
                type="date"
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
                required
              />
            </Field>
            <Field>
              <Label htmlFor="end-date-1">End Date (leave blank for a single-day event)</Label>
              <Input
                id="end-date-1"
                name="end_date"
                type="date"
                value={eventEndDate}
                min={eventDate || undefined}
                onChange={(e) => setEventEndDate(e.target.value)}
              />
            </Field>
            <Field>
              <Label htmlFor="start-time-1">Start Time</Label>
              <Input id="start-time-1" name="start_time" type="time" value={eventStartTime} onChange={(e) => {setEventStartTime(e.target.value)}} required/>
            </Field>
            <Field>
              <Label htmlFor="end-time-1">End Time</Label>
              <Input id="end-time-1" name="end_time" type="time" value={eventEndTime} onChange={(e) => setEventEndTime(e.target.value)} required/>
            </Field>
            <Field>
              <Label htmlFor="flyer-1">Flyer (shown on events page &amp; homepage)</Label>
              <Input
                id="flyer-1"
                name="flyer"
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                onChange={(e) => {
                  const file = e.target.files?.[0] ?? null;
                  setFlyerFile(file);
                  if (file) setRemoveFlyer(false);
                }}
              />
              {flyerPreviewUrl && !removeFlyer && (
                // Flyer images are served by the backend API, not a static host,
                // so use a plain img rather than next/image.
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={flyerPreviewUrl}
                  alt="Flyer preview"
                  className="mt-2 max-h-40 w-auto rounded-md border border-zinc-300 object-contain"
                />
              )}
              {event?.flyer_url && !removeFlyer && (
                <button
                  type="button"
                  className="mt-1 text-sm text-red-600 underline self-start"
                  onClick={() => { setRemoveFlyer(true); setFlyerFile(null); }}
                >
                  Remove flyer
                </button>
              )}
              {removeFlyer && (
                <p className="text-sm text-zinc-500">Flyer will be removed when you save.</p>
              )}
            </Field>
          </FieldGroup>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              type="submit"
              disabled={!eventTitle.trim() || !eventDescription.trim() || !eventDate || !eventStartTime || !eventEndTime || saving}
            >
              {saving ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
