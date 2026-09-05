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
import { createEvent, updateEvent, type Event } from "@/lib/api"
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
  const date = new Date(isoString);
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
  const date = new Date(isoString);
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
  const [eventStartTime, setEventStartTime] = useState(
    event?.start_time ? toTimeInputValue(event.start_time) : "",
  );
  const [eventEndTime, setEventEndTime] = useState(
    event?.end_time ? toTimeInputValue(event.end_time) : "",
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      setEventStartTime(event?.start_time ? toTimeInputValue(event.start_time) : "");
      setEventEndTime(event?.end_time ? toTimeInputValue(event.end_time) : "");
      setError(null);
    }
  }

  const handleSave = async () => {
    const trimmedTitle = eventTitle.trim();
    const trimmedDescription = eventDescription.trim();
    if (!trimmedTitle || !trimmedDescription || !eventDate || !eventStartTime || !eventEndTime) {
      setError("One or more fields are empty");
      return;
    }

    const start = fromZonedTime(eventDate, eventStartTime);
    const end = fromZonedTime(eventDate, eventEndTime);
    if (new Date(end).getTime() <= new Date(start).getTime()) {
      setError("End time must be after start time");
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
        await createEvent(payload);
        toast.success("Event created");
      } else {
        await updateEvent(event.id, payload);
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
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void handleSave();
        }}
      >
        <DialogContent className="sm:max-w-sm">
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
              <Label htmlFor="start-time-1">Start Time</Label>
              <Input id="start-time-1" name="start_time" type="time" value={eventStartTime} onChange={(e) => {setEventStartTime(e.target.value)}} required/>
            </Field>
            <Field>
              <Label htmlFor="end-time-1">End Time</Label>
              <Input id="end-time-1" name="end_time" type="time" value={eventEndTime} onChange={(e) => setEventEndTime(e.target.value)} required/>
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
        </DialogContent>
      </form>
    </Dialog>
  )
}
