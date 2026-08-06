'use client'

import Link from "next/link";
import Image from 'next/image'
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from 'react';
import Calendar from "@/components/calendar";
import TestCalendar from "@/components/test-calendar";

import {
  fetchEvents,
  type EventsResponse,
  type Event,
} from "@/lib/api";


export default function Events() {

    const [calendarButton, setCalendarButton] = useState(false);
    const [eventsButton, setEventsButton] = useState(true);
    const [eventButtonStyle, setEventButtonStyle] = useState("rounded-none border-y border-l border-black shadow-lg bg-zinc-900 hover:text-white");
    const [calendarButtonStyle, setCalendarButtonStyle] = useState("rounded-none border-black border shadow-lg bg-white/70 hover:bg-zinc-200 text-zinc-900")
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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
            console.log("Events: ", res[0].data);
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
        <div className="flex justify-center items-center h-50 bg-[url('../public/choir-edit.jpg')] bg-cover bg-center md:h-100 lg:h-100">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Events
            </h1>
        </div>
    

        <div className="flex flex-col justify-center py-15 sm:gap-15 sm:justify-center sm:py-20">
            <div className="flex min-w-[700px] sm:min-w-0 max-w-6xl mx-auto">
                <Button onClick={handleEventButton} className={eventButtonStyle} size="default" variant="default">Special Events</Button>
                <Button onClick={handleCalendarButton} className={calendarButtonStyle} size="default" variant="default">Calendar</Button>
            </div>

            {eventsButton && 
            <div className="flex flex-col justify-center items-center">
                <div className='ustify-center items-center w-sm py-15 sm:gap-15 sm:justify-center sm:py-20'>
                    <Button size="sm">Add Event</Button>
                </div>
                <div className='grid grid-cols-2 gap-y-20 px-65 justify-items-center'>
                    {events.map((data: Event, index) =>
                        <div className='flex flex-col md:flex-row '
                        key={index}>
                            <Image
                            src="/tempEventsPhoto.png"
                            width={300}
                            height={300}
                            alt="Beige background with photo of cross"
                            className='w-90 h-30 md:h-60'
                            />
                            <div className='flex flex-col pl-5 font-medium font-noto-sans'>
                                <h1 className='text-3xl'>{data.title}</h1>
                
                                <h1 className='text-black/40 font-normal'>{new Date(data.date).toLocaleDateString('en-US', { day: "2-digit", month: "short"})}</h1>
                                <h1 className='text-black/40 font-normal'>{new Date(data.start_time).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit", hour12: true })} - {new Date(data.end_time).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit" })}</h1>
                                <h1 className='text-lg pt-5'>{data.description}</h1>
                            </div>
                
                        </div>
                    )}
                </div>
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
