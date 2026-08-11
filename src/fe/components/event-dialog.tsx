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

    const [eventTitle, setEventTitle] = useState("");
    const [eventDescription, setEventDescription] = useState("");
    const [eventDate, setEventDate] = useState("");
    const [eventStartTime, setEventStartTime] = useState("");
    const [eventEndTime, setEventEndTime] = useState("");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSave = async () => {
        const trimmedTitle = eventTitle.trim();
        const trimmedDescription = eventDescription.trim();
        if (!trimmedTitle || !trimmedDescription || !eventDate || !eventStartTime || !eventEndTime) {
            setError("One or more fields are empty");
            return;
        }
        const start = new Date(`${eventDate}T${eventStartTime}:00`);
        const end = new Date(`${eventDate}T${eventEndTime}:00`);
        const date = new Date(eventDate);
        setSaving(true);
        setError(null);
        try {

        const payload = {
            title: trimmedTitle,
            description: trimmedDescription,
            date: date.toISOString(),
            start_time: start.toISOString(),
            end_time: end.toISOString(),
        };
        if (!event) {
            await createEvent(payload);
            toast.success("Event created");
            setEventTitle("");
            setEventDescription("");
            setEventDate("");
            setEventStartTime("");
            setEventEndTime("");
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
      <form>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Add Event</DialogTitle>
            <DialogDescription>
              Fill in the details for the new event.
            </DialogDescription>
          </DialogHeader>
          <FieldGroup>
            <Field>
              <Label htmlFor="title-1">Event Title</Label>
              <Input id="title-1" name="title" value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} required/>
            </Field>
            <Field>
              <Label htmlFor="description-1">Description</Label>
              <Input id="description-1" name="description" value={eventDescription} onChange={(e) => setEventDescription(e.target.value)} required/>
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
