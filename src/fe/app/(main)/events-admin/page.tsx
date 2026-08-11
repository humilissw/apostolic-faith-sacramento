'use client'

import Link from "next/link";
import Image from 'next/image'
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from 'react';
import Calendar from "@/components/calendar";
import TestCalendar from "@/components/test-calendar";
import { EventDialog } from "@/components/event-dialog";
import { Trash2, Pencil, Plus } from 'lucide-react';
import { toast } from "sonner"

import {
  fetchEvents,
  deleteEvent,
  type EventsResponse,
  type Event,
} from "@/lib/api";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";


export default function Events() {

    const [calendarButton, setCalendarButton] = useState(false);
    const [eventsButton, setEventsButton] = useState(true);
    const [eventButtonStyle, setEventButtonStyle] = useState("rounded-none border-y border-l border-black shadow-lg bg-zinc-900 hover:text-white");
    const [calendarButtonStyle, setCalendarButtonStyle] = useState("rounded-none border-black border shadow-lg bg-white/70 hover:bg-zinc-200 text-zinc-900")
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [editingEvent, setEditingEvent] = useState<Event | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
    const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
    const [deletingId, setDeletingId] = useState<string | null>(null);

    function handleCalendarButton () {
        setCalendarButton(true);
        setEventsButton(false);
        setEventButtonStyle("rounded-none border-y border-l border-black shadow-lg bg-white/70 hover:bg-zinc-200 text-zinc-900")
        setCalendarButtonStyle("rounded-none border border-black shadow-lg bg-zinc-900 hover:text-white")
    }

    function handleEventButton () {
        setEventsButton(true); 
        setCalendarButton(false);
        setEventButtonStyle("rounded-none border-y border-l border-black shadow-lg bg-zinc-900 hover:text-white")
        setCalendarButtonStyle("rounded-none border border-black bg-white/70 shadow-lg hover:bg-zinc-200 text-zinc-900")
    }

    const handleDeleteClick = (id: string) => {
      setPendingDeleteId(id);
      setDeleteConfirmOpen(true);
    };

    const handleDeleteConfirm = async () => {
    if (!pendingDeleteId) return;
    setDeleteConfirmOpen(false);
    setDeletingId(pendingDeleteId);
    try {
      await deleteEvent(pendingDeleteId);
      setEvents((prev) => prev.filter((u) => u.id !== pendingDeleteId));
      toast.success("Video upload deleted");
    } catch {
      toast.error("Failed to delete video upload");
    } finally {
      setDeletingId(null);
      setPendingDeleteId(null);
    }
  };

    function handleOpenDialog(event: Event | null) {
        setEditingEvent(event);
        setDialogOpen(true);
    }

    function handleCreate() {
        setEditingEvent(null);
        setDialogOpen(true);
    }
    

    useEffect(() => {
        let cancelled = false;
        async function load() {
          try {
            const res = await Promise.all([
              fetchEvents(),
              fetch(`${API_BASE}${API_V1}/events/`).then((r) => r.json()),
            ]);
            if (!cancelled) {
              setEvents(res[0].data);
            }
          } catch (err) {
            if (!cancelled)
              setError(err instanceof Error ? err.message : "Failed to load");
          } finally {
            if (!cancelled) setLoading(false);
          }
        }
    
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
        const API_V1 = "api/v1";
        load();
        return () => { cancelled = true; };
      }, []);


  return (
    <div>
        <div className="flex justify-center items-center h-50 bg-[url('../public/events.jpeg')] bg-cover bg-[position:center_70%] md:h-100 lg:h-100">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Events
            </h1>
        </div>
    

        <div className="flex flex-col justify-center pt-15">
            <div className="flex min-w-[700px] sm:min-w-0 max-w-6xl mx-auto">
                <Button onClick={handleEventButton} className={eventButtonStyle} size="default" variant="default">Special Events</Button>
                <Button onClick={handleCalendarButton} className={calendarButtonStyle} size="default" variant="default">Calendar</Button>
            </div>

            {eventsButton && 
            <div className="flex flex-col justify-center items-center pb-25">
                <div className='flex w-full justify-start items-center py-5 px-65'>
                    <Button className="bg-zinc-900 text-white" variant="outline" onClick={handleCreate}>Create Event<Plus className="w-4 h-4" /></Button>
                    {dialogOpen && (
                      <EventDialog 
                        key={editingEvent?.id ?? "create"}
                        open={dialogOpen}
                        onOpenChange={setDialogOpen}
                        event={editingEvent}
                        onSuccess={() => {
                          fetchEvents().then((data) => setEvents(data.data));
                        }}/>
                    )} 
                </div>
                <div className='grid grid-cols-2 gap-y-20 gap-x-30 px-65'>
                    {events.length === 0 && !loading && <p>No events found.</p>}
                    {loading && <p>Loading events...</p>}
                    {error && <p>Error loading events: {error}</p>}

                    {events.length > 0 && !loading && !error &&
                    events.map((data: Event, index) =>
                        <div key={index} >
                            <Link href={`/events/${data.id}`}>
                                <div className='flex flex-col md:flex-row '
                                >
                                    <Image
                                    src="/tempEventsPhoto.png"
                                    width={300}
                                    height={300}
                                    alt="Simple Events Background Photo"
                                    className='w-90 h-30 md:h-60'
                                    />
                                    <div className='flex flex-col pl-5 font-medium font-noto-sans'>
                                        <h1 className='text-3xl'>{data.title}</h1>
                                        <h1 className='text-black/40 font-normal'>{new Date(data.date).toLocaleDateString('en-US', { day: "2-digit", month: "short"})}</h1>
                                        <h1 className='text-black/40 font-normal'>{new Date(data.start_time).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit", hour12: true })} - {new Date(data.end_time).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit" })}</h1>
                                    </div>
                                </div>
                            </Link>
                            <div className='flex flex-row gap-2 pt-2'> 
                                <button onClick={() => handleDeleteClick(data.id)}>
                                    <Trash2 color="red" size={16} />
                                </button>
                                <button onClick={() => handleOpenDialog(data)}>
                                    <Pencil size={16} />
                                </button>
                            </div>
                        </div>
                        
                    )}
                </div>

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
            }

            {calendarButton &&
                <div>
                    <TestCalendar />
                </div>
            }
        </div>

    </div>
  )
}
