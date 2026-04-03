'use client';

import AFCLogo from "@/components/afc-logo";
import Link from "next/link";
import { startOfMonth, format, endOfMonth, eachDayOfInterval, getDay, isSameDay } from  "date-fns"
import { useEffect, useState } from "react";

const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

interface CalendarEvent {
    id: number;
    date: string;
    title: string;
    description: string;
}

export default function Calendar() {

      const [calendarData, setCalendarData] = useState([]);
      const fetchData = async () => {
        try {
          const response = await fetch('/calendarData.json');
          if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
          }
    
          const result = await response.json();
          setCalendarData(result);
        } catch (error) {
          if (error instanceof Error) {
            console.error(error.message);
          }
        }
    }
    
      useEffect(() => {
        fetchData();
      }, [])
    
    const currentDate = new Date();
    const firstDayOfMonth = startOfMonth(currentDate);
    const lastDayOfMonth = endOfMonth(currentDate);

    const daysInMonth = eachDayOfInterval({
        start: firstDayOfMonth, 
        end: lastDayOfMonth
    })

    const firstDayOfMonthIndex = getDay(firstDayOfMonth);

    const emptyDays = Array(firstDayOfMonthIndex).fill("")

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-4xl text-center">{format(currentDate, "MMMM yyyy")}</h2>
            </div>
            <div className="grid grid-cols-7 content-center px-65">
                {WEEKDAYS.map((day) => (
                    <div key={day} className="text-center text-xl p-2 bg-zinc-600 text-white">
                        {day}
                    </div>
                ))}
                {emptyDays.map((_, index) => (
                    <div key={index} />
                ))}
                {daysInMonth.map((day, index) => (
                   <div 
                    key={index} 
                    className="border h-40 text-right pr-3 pt-2"> 
                    {format(day, "d")} 
                    <div className="text-sm text-left pl-3">
                        {calendarData
                            .filter((data: CalendarEvent) => isSameDay(new Date(data.date), day))
                            .map((data: CalendarEvent) => (
                                <div key={data.id}>{data.title}</div>
                            ))}
                        </div>
                   </div> 
                ))}
            </div>
        </div>
    )
}