'use client'

import Link from "next/link";
import Image from 'next/image'
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";
import { Button } from "@/components/ui/button";
import { useState, useEffect, useLayoutEffect, useRef } from 'react';
import Calendar from "@/components/calendar";
import TestCalendar from "@/components/test-calendar";
import { EventDialog } from "@/components/event-dialog";
import { Trash2, Pencil, Plus, ChevronDown } from 'lucide-react';
import { toast } from "sonner"

import {
  fetchEvents,
  deleteEvent,
  deleteEvents,
  flyerImageUrl,
  formatEventDateRange,
  formatEventTime,
  type EventsResponse,
  type Event,
} from "@/lib/api";
import { FlyerImage } from "@/components/flyer-image";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { API_BASE, API_V1 } from "@/lib/api/base";


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
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const [bulkDeleteConfirmOpen, setBulkDeleteConfirmOpen] = useState(false);
    const [bulkDeleting, setBulkDeleting] = useState(false);

    const toggleSelect = (id: string) => {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) {
          next.delete(id);
        } else {
          next.add(id);
        }
        return next;
      });
    };

    const allSelected = events.length > 0 && selectedIds.size === events.length;

    const toggleSelectAll = () => {
      setSelectedIds(allSelected ? new Set() : new Set(events.map((e) => e.id)));
    };

    const handleBulkDeleteClick = () => {
      if (selectedIds.size === 0) return;
      setBulkDeleteConfirmOpen(true);
    };

    const handleBulkDeleteConfirm = async () => {
      const ids = Array.from(selectedIds);
      if (ids.length === 0) return;
      setBulkDeleteConfirmOpen(false);
      setBulkDeleting(true);
      try {
        await deleteEvents(ids);
        setEvents((prev) => prev.filter((e) => !ids.includes(e.id)));
        setSelectedIds(new Set());
        toast.success(`Deleted ${ids.length} event${ids.length === 1 ? "" : "s"}`);
      } catch {
        toast.error("Failed to delete events");
      } finally {
        setBulkDeleting(false);
      }
    };

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

    function EventCard({ event }: { event: Event }) {
    const [expanded, setExpanded] = useState(false);
    const [isOverflowing, setIsOverflowing] = useState(false);
    const textRef = useRef<HTMLHeadingElement>(null);

    useLayoutEffect(() => {
        const el = textRef.current;
        if (el) {
            setIsOverflowing(el.scrollHeight > el.clientHeight + 1);
        }
    }, [event.description]);

    return (
        <div className='flex flex-col'>
            {event.flyer_url ? (
                <FlyerImage
                src={flyerImageUrl(event.flyer_url) ?? ""}
                alt={`Flyer for ${event.title}`}
                title={event.title}
                className='w-90 h-60 object-cover'
                />
            ) : (
                <Image
                src="/tempEventsPhoto.png"
                width={90}
                height={60}
                alt="Simple Background"
                className='w-90 h-60 object-cover'
                />
                )}
            <div className='flex flex-col pt-2 font-medium font-noto-sans w-90 group'>
                <h1 className='text-base sm:text-lg lg:text-xl font-semibold leading-snug'>{event.title}</h1>
                <h1 className='text-xs sm:text-sm text-gray-500 mt-1'>{formatEventDateRange(event)}</h1>
                <h1 className='text-xs sm:text-sm text-gray-500 mt-1'>{formatEventTime(event.start_time)} - {formatEventTime(event.end_time)}</h1>
                <h1
                    ref={textRef}
                    className={`text-sm sm:text-base text-gray-600 leading-relaxed
                    ${expanded ? "" : "line-clamp-3" }`}>
                    {event.description}
                </h1>

                {isOverflowing && (
                <button
                    onClick={() => setExpanded((e) => !e)}
                    className="text-slate-700 hover:text-slate-900 text-sm mt-1 hover:underline flex items-center"
                >
                    {expanded ? "Show Less" : "Read More"}
                    <ChevronDown className={`ml-1 transition-transform duration-300 ${expanded ? "transform rotate-180" : ""}`} />

                </button>
                )}
                <div className='flex flex-row gap-2 pt-2 items-center'>
                  <label className='flex items-center gap-1 text-sm text-black/60 cursor-pointer select-none'>
                      <input
                          type="checkbox"
                          className="w-4 h-4 accent-zinc-900"
                          checked={selectedIds.has(event.id)}
                          onChange={() => toggleSelect(event.id)}
                          aria-label={`Select ${event.title} for bulk delete`}
                      />
                      Select
                  </label>
                  <button onClick={() => handleDeleteClick(event.id)}>
                      <Trash2 color="red" size={16} />
                  </button>
                  <button onClick={() => handleOpenDialog(event)}>
                      <Pencil size={16} />
                  </button>
              </div>
            </div>
        </div>
    )}

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
      setSelectedIds((prev) => {
        const next = new Set(prev);
        next.delete(pendingDeleteId);
        return next;
      });
      toast.success("Event deleted");
    } catch {
      toast.error("Failed to delete event");
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


        <div className="flex flex-col justify-center py-15 sm:gap-15 sm:justify-center sm:py-20">
            <div className="md:flex min-w-[700px] sm:min-w-0 max-w-6xl mx-auto hidden">
                <Button onClick={handleEventButton} className={eventButtonStyle} size="default" variant="default">Special Events</Button>
                <Button onClick={handleCalendarButton} className={calendarButtonStyle} size="default" variant="default">Calendar</Button>
            </div>

            {eventsButton &&
            <div className="flex flex-col justify-center items-center pb-15">

                <div className="flex justify-center sm:gap-15 sm:justify-center">
                  <div className='grid grid-cols-1 px-10 lg:grid-cols-2 xl:grid-cols-3 gap-y-10 lg:gap-x-25 xl:gap-x-35'>
                    <div className='flex gap-3 col-span-1 lg:col-span-2 xl:col-span-3'>
                    <Button className="bg-zinc-900 text-white" variant="outline" onClick={handleCreate}>Create Event<Plus className="w-4 h-4" /></Button>
                    {events.length > 0 && (
                      <label className="flex items-center gap-2 text-sm font-medium cursor-pointer select-none">
                        <input
                          type="checkbox"
                          className="w-4 h-4 accent-zinc-900"
                          checked={allSelected}
                          onChange={toggleSelectAll}
                        />
                        Select all
                      </label>
                    )}
                    {selectedIds.size > 0 && (
                      <Button
                        variant="outline"
                        className="border-red-600 text-red-600 hover:bg-red-50"
                        onClick={handleBulkDeleteClick}
                        disabled={bulkDeleting}
                      >
                        Delete Selected ({selectedIds.size})
                      </Button>
                    )}
                    {dialogOpen && (
                      <EventDialog
                        //key={editingEvent?.id ?? "create"}
                        open={dialogOpen}
                        onOpenChange={setDialogOpen}
                        event={editingEvent}
                        onSuccess={() => {
                          fetchEvents().then((data) => setEvents(data.data));
                        }}/>
                    )}
                </div>
                      {events.length === 0 && !loading && <p>No events found.</p>}
                      {loading && <p>Loading events...</p>}
                      {error && <p>Error loading events: {error}</p>}
                      {events.length > 0 && !loading && !error &&
                      events.map((data: Event, index) =>
                        <EventCard key={index} event={data} />
                      )}
                  </div>
                </div>

                <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete event</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. The event will be permanently removed.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleDeleteConfirm}>Delete</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>

                <AlertDialog open={bulkDeleteConfirmOpen} onOpenChange={setBulkDeleteConfirmOpen}>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete {selectedIds.size} event{selectedIds.size === 1 ? "" : "s"}</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. The selected events will be permanently removed.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={handleBulkDeleteConfirm}>Delete</AlertDialogAction>
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
