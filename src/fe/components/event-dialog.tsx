import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Field, FieldGroup } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"
import { createEvent, updateEvent, type Event } from "@/lib/api"
import { toast } from "sonner"
import { Plus } from 'lucide-react';
import { fromZonedTime } from 'date-fns-tz';

interface EventDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  event: Event | null;
  onSuccess: () => void;
}

export function EventDialog({
  open,
  onOpenChange,
  event,
  onSuccess,
}: EventDialogProps) {

    const [eventTitle, setEventTitle] = useState(event?.title ?? "");
    const [eventDescription, setEventDescription] = useState(event?.description ?? "");
    const [eventDate, setEventDate] = useState(event?.date ?? "");
    const [eventStartTime, setEventStartTime] = useState(event?.start_time ? toTimeInputValue(event.start_time) : "");
    const [eventEndTime, setEventEndTime] = useState(event?.end_time ? toTimeInputValue(event.end_time) : "");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function toTimeInputValue(isoString: string): string {
        const date = new Date(isoString);
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    const handleSave = async () => {
        console.log("Saving event with values:", {
            title: eventTitle,
            description: eventDescription,
            date: eventDate,
            start_time: eventStartTime,
            end_time: eventEndTime,
        });
        const trimmedTitle = eventTitle.trim();
        const trimmedDescription = eventDescription.trim();
        if (!trimmedTitle || !trimmedDescription || !eventDate || !eventStartTime || !eventEndTime) {
            setError("One or more fields are empty");
            console.log("One or more fields are empty");
            return;
        }
        const start = fromZonedTime(`${eventDate}T${eventStartTime}:00`);
        const end = fromZonedTime(`${eventDate}T${eventEndTime}:00`);
        const date = new Date(eventDate);
        setSaving(true);
        setError(null);
        try {
          console.log("2 Saving event with values:", {
            title: trimmedTitle,
            description: eventDescription,
            date: date.toISOString(),
            start_time: start.toISOString(),
            end_time: end.toISOString(),
        });
        const payload = {
            title: trimmedTitle,
            description: trimmedDescription,
            date: date.toISOString(),
            start_time: start.toISOString(),
            end_time: end.toISOString(),
        };
        console.log(" I dont think i get here")
        if (!event) {
          console.log("In here?")
            await createEvent(payload);
            toast.success("Event created");
            setEventTitle("");
            setEventDescription("");
            setEventDate("");
            setEventStartTime("");
            setEventEndTime("");
        } else {
          console.log("Updating event with payload:", payload);
            await updateEvent(event.id, payload);
            toast.success("Event updated");
        }
        onOpenChange(false);
        onSuccess();
        } catch (err) {
        console.log("Error occurred while saving event:", err);
        setError(err instanceof Error ? err.message : "Failed to save");
        } finally {
        setSaving(false);
        }
    };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <form>
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
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <DialogClose asChild>
              <Button 
                type="submit"
                disabled={!eventTitle || !eventDescription || !eventDate || !eventStartTime || !eventEndTime || saving}
                onClick={handleSave}
              >
                Save changes
              </Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  )
}
