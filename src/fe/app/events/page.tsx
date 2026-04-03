'use client'

import Link from "next/link";
import Image from 'next/image'
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from 'react';
import Calendar from "@/components/calendar";

interface EventsData {
  image: string;
  eventTitle: string;
  description: string;
  date: string;
  startTime: string;
  endTime: string;
}

const options = {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
};

export default function Events() {

    const [calendarButton, setCalendarButton] = useState(false);
    const [eventsButton, setEventsButton] = useState(true);
    const [eventButtonStyle, setEventButtonStyle] = useState("rounded-none border-y border-l border-black shadow-lg bg-zinc-900 hover:text-white");
    const [calendarButtonStyle, setCalendarButtonStyle] = useState("rounded-none border-black border shadow-lg bg-white/70 hover:bg-zinc-200 text-zinc-900")

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

    const [eventsData, setEventsData] = useState([]);
    const fetchData = async () => {
    try {
        const response = await fetch('/eventsData.json');
        if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        setEventsData(result);
    } catch (error) {
        if (error instanceof Error) {
        console.error(error.message);
        }
    }
}

    useEffect(() => {
        fetchData();
    }, [])


  return (
    <div>
        <div className="flex justify-center items-center h-50 bg-[url('../public/choir-edit.jpg')] bg-cover bg-center md:h-100 lg:h-100">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Events
            </h1>
        </div>
    

        <div className="flex flex-col justify-center py-15 sm:gap-15 sm:justify-center sm:py-20">
            <div className="flex justify-start px-65">
                <Button onClick={handleEventButton} className={eventButtonStyle} size="default" variant="default">Upcoming Events</Button>
                <Button onClick={handleCalendarButton} className={calendarButtonStyle} size="default" variant="default">Calendar</Button>
            </div>

            {eventsButton && 
            <div className='grid grid-cols-2 gap-y-20 px-65 justify-items-center'>
                {eventsData.map((data: EventsData, index) => 
                    <div className='flex flex-col md:flex-row '
                    key={index}>
                        <Image
                        src={data.image}
                        width={300}
                        height={300}
                        alt="Picture of a cross with Palm Sunday text"
                        className='w-90 h-30 md:h-60'
                        />
                        <div className='flex flex-col pl-5 font-medium font-noto-sans'>
                            <h1 className='text-3xl'>{data.eventTitle}</h1>
                            
                            <h1 className='text-black/40 font-normal'>{new Date(data.date).toLocaleDateString('en-US', options)}</h1>
                            <h1 className='text-black/40 font-normal'>{new Date(data.startTime).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit" })} - {new Date(data.endTime).toLocaleTimeString('en-US', { hour: "2-digit", minute: "2-digit" })}</h1>
                            <h1 className='text-lg pt-5'>{data.description}</h1>
                        </div>
                        
                    </div>
                )}
            </div>
            }

            {calendarButton &&
                <div>
                    <Calendar />
                </div>
            }
        </div>

    </div>
  )
}
