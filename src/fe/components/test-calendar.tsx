import React, { useEffect, useMemo, useState } from 'react';
import { fetchEvents, eventCalendarDays, formatEventTime, type Event } from '@/lib/api';

interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  /** Every calendar day ("yyyy-MM-dd") this event occupies (multi-day aware). */
  days: string[];
}

const Calendar = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    let cancelled = false;
    const fetchEventsFromApi = async () => {
      try {
        // Public events endpoint — new events created in the admin show up here.
        const response = await fetchEvents();

        if (cancelled) return;

        const mapped: CalendarEvent[] = response.data.map((event: Event) => ({
          id: event.id,
          title: event.title,
          description: event.description ?? '',
          start_time: event.start_time,
          end_time: event.end_time,
          days: eventCalendarDays(event),
        }));

        setEvents(mapped);
      } catch (error) {
        console.error('Error fetching events:', error);
      }
    };

    fetchEventsFromApi();
    return () => {
      cancelled = true;
    };
  }, []);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);

  const daysInMonth = lastDayOfMonth.getDate();
  const startingDayOfWeek = firstDayOfMonth.getDay();

  const previousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const groupedEvents = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {};

    events.forEach((event) => {
      // A multi-day event is registered on every day it spans.
      event.days.forEach((key) => {
        if (!map[key]) {
          map[key] = [];
        }
        map[key].push(event);
      });
    });

    return map;
  }, [events]);

  const days = [];

  // Empty cells before month starts
  for (let i = 0; i < startingDayOfWeek; i++) {
    days.push(
      <div
        key={`empty-${i}`}
        className="border min-h-[90px] sm:min-h-[120px] md:min-h-[140px] bg-gray-50"
      />
    );
  }

  // Calendar days
  for (let day = 1; day <= daysInMonth; day++) {
    const key = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const dayEvents = groupedEvents[key] || [];

    days.push(
      <div
        key={day}
        className="border min-h-[90px] sm:min-h-[120px] md:min-h-[140px] p-1 sm:p-2 bg-white overflow-visible relative"
      >
        <div className="font-semibold text-xs sm:text-sm md:text-base mb-1 sm:mb-2">
          {day}
        </div>

        <div className="space-y-1">
          {dayEvents.map((event) => {
            const isContinuation = event.days[0] !== key;

            return (
              <div
                key={`${event.id}-${key}`}
                className="relative group"
              >
                {/* Event Card */}
                <div className="bg-blue-100 rounded p-1 text-[10px] sm:text-xs cursor-pointer hover:bg-blue-200 transition">
                  <div className="font-medium truncate">
                    {event.title}
                  </div>

                  <div className="text-gray-600 truncate">
                    {isContinuation ? 'Continues' : formatEventTime(event.start_time)}
                  </div>
                </div>

                {/* Popup */}
                <div className="absolute hidden group-hover:block z-[9999] left-1/2 -translate-x-1/2 sm:left-full sm:translate-x-0 top-full sm:top-0 mt-2 sm:mt-0 sm:ml-3 w-56 sm:w-72 bg-white border border-gray-200 shadow-2xl rounded-xl p-3 sm:p-4">
                  <h3 className="font-semibold text-sm sm:text-base mb-1">
                    {event.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-gray-500 mb-3">
                    {formatEventTime(event.start_time)} – {formatEventTime(event.end_time)}
                  </p>

                  <div>
                    <p className="text-[10px] sm:text-xs uppercase tracking-wide text-gray-400 mb-1">
                      Description
                    </p>

                    <p className="text-xs sm:text-sm text-gray-700">
                      {event.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full p-2 sm:p-4 overflow-x-auto">
      <div className="min-w-[700px] sm:min-w-0 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 gap-2">
          <button
            onClick={previousMonth}
            className="px-2 sm:px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition text-xs sm:text-sm"
          >
            Previous
          </button>

          <h2 className="text-lg sm:text-2xl font-bold text-center">
            {currentDate.toLocaleDateString('en-US', {
              month: 'long',
              year: 'numeric',
            })}
          </h2>

          <button
            onClick={nextMonth}
            className="px-2 sm:px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition text-xs sm:text-sm"
          >
            Next
          </button>
        </div>

        {/* Weekday Headers */}
        <div className="grid grid-cols-7">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(
            (day) => (
              <div
                key={day}
                className="border p-1 sm:p-2 text-center font-semibold bg-gray-100 text-[10px] sm:text-sm"
              >
                {day}
              </div>
            )
          )}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 overflow-visible">
          {days}
        </div>
      </div>
    </div>
  );
};

export default Calendar;
