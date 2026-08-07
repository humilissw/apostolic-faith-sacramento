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
        console.log("what about here");
        const trimmedTitle = eventTitle.trim();
        const trimmedDescription = eventDescription.trim();
        console.log("trimmedTitle: ", trimmedTitle, "trimmedDescription: ", trimmedDescription, "eventDate: ", eventDate);
        if (!trimmedTitle || !trimmedDescription || !eventDate || !eventStartTime || !eventEndTime) {
            console.log("One or more fields are empty");
            return;
        }
        const start = new Date(`${eventDate}T${eventStartTime}:00`);
        const end = new Date(`${eventDate}T${eventEndTime}:00`);
        const date = new Date(eventDate);
        setSaving(true);
        setError(null);
        try {
        console.log("what about here 2");
        const payload = {
            title: trimmedTitle,
            description: trimmedDescription,
            date: date.toISOString(),
            start_time: start.toISOString(),
            end_time: end.toISOString(),
        };
        console.log("Why am i not here")
        console.log("payload: ", payload);
        if (!event) {
            await createEvent(payload);
            toast.success("Event created");
        } else {
            await updateEvent(event.id, payload);
            toast.success("Event updated");
        }
        console.log("donw here")
        onOpenChange(false);
        onSuccess();
        } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to save");
        console.log("Error: ", err);
        } finally {
        setSaving(false);
        }
    };
  return (
    <Dialog>
      <form>
        <DialogTrigger asChild>
          <Button variant="outline">Create Event</Button>
        </DialogTrigger>
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
              <Input id="title-1" name="title" value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} />
            </Field>
            <Field>
              <Label htmlFor="description-1">Description</Label>
              <Input id="description-1" name="description" value={eventDescription} onChange={(e) => setEventDescription(e.target.value)} />
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
              <Input id="start-time-1" name="start_time" type="time" value={eventStartTime} onChange={(e) => {console.log("Start time: ", e.target.value); setEventStartTime(e.target.value)}} />
            </Field>
            <Field>
              <Label htmlFor="end-time-1">End Time</Label>
              <Input id="end-time-1" name="end_time" type="time" value={eventEndTime} onChange={(e) => setEventEndTime(e.target.value)} />
            </Field>
          </FieldGroup>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button 
                type="submit"
                onClick={() => {console.log("HERE!! eventTitle: ", eventTitle, "eventDescription: ", eventDescription, "eventDate: ", eventDate, "eventStartTime: ", eventStartTime, "eventEndTime: ", eventEndTime); handleSave()}}
            >
                Save changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  )
}
