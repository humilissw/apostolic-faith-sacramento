'use client'

import Link from "next/link";
import Image from 'next/image'
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from 'react';
import Calendar from "@/components/calendar";
import TestCalendar from "@/components/test-calendar";
import { API_BASE, API_V1 } from "@/lib/api/base";

import {
  fetchEvents,
  flyerImageUrl,
  formatEventDateRange,
  formatEventTime,
  type EventsResponse,
  type Event,
} from "@/lib/api";
import { FlyerImage } from "@/components/flyer-image";


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
            <div className="flex justify-center sm:gap-15 sm:justify-center">
                <div className='grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-y-10 lg:gap-x-25 xl:gap-x-35'>
                    {events.map((data: Event, index) =>
                        <div className='flex flex-col'
                        key={index}>
                            {data.flyer_url ? (
                                <FlyerImage
                                src={flyerImageUrl(data.flyer_url) ?? ""}
                                alt={`Flyer for ${data.title}`}
                                title={data.title}
                                className='w-90 h-30 md:h-60 object-cover'
                                />
                            ) : (
                                <Image
                                src="/tempEventsPhoto.png"
                                width={90}
                                height={30}
                                alt="Simple Background"
                                className='w-90 h-30 md:h-60 object-cover'
                                />
                                )}
                            <div className='flex flex-col pt-2 font-medium font-noto-sans w-90 group'>
                                <h1 className='text-base sm:text-lg lg:text-xl font-semibold leading-snug'>{data.title}</h1>
                                <h1 className='text-xs sm:text-sm text-gray-500 mt-1'>{formatEventDateRange(data)}</h1>
                                <h1 className='text-xs sm:text-sm text-gray-500 mt-1'>{formatEventTime(data.start_time)} - {formatEventTime(data.end_time)}</h1>
                                <h1 className='text-sm sm:text-base text-gray-600 leading-relaxed line-clamp-3 group-hover:line-clamp-none'>{data.description}</h1>
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
