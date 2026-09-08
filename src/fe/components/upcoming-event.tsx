"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { fetchEvents, flyerImageUrl, formatEventDateRange, formatEventTime, parseServerDate, type Event } from "@/lib/api";
import { FlyerImage } from "@/components/flyer-image";
import { useFeatureFlag } from "@/context/feature-flag-context";

// The next upcoming event (based on start_time) is highlighted on the homepage.
// When events exist at all, an "Events" button links to the events page — even
// if every event has already ended.
export default function UpcomingEvent() {
  const eventsEnabled = useFeatureFlag("enable_events");
  const [event, setEvent] = useState<Event | null>(null);
  const [hasAnyEvents, setHasAnyEvents] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!eventsEnabled) return;
    let cancelled = false;
    async function load() {
      try {
        // Public endpoint: no auth required.
        const eventsRes = await fetchEvents();
        if (cancelled) return;
        const now = Date.now();
        const all = list0(eventsRes.data);
        setHasAnyEvents(all.length > 0);
        const upcoming = all
          .filter((e) => parseServerDate(e.start_time).getTime() >= now)
          .sort(
            (a, b) =>
              parseServerDate(a.start_time).getTime() - parseServerDate(b.start_time).getTime(),
          );
        setEvent(upcoming[0] ?? null);
      } catch {
        // Homepage must stay usable even if the events API is down.
        setEvent(null);
        setHasAnyEvents(false);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [eventsEnabled]);

  // Events exist but none are upcoming: still surface a link to the events page.
  if (!loading && !event && hasAnyEvents) {
    return (
      <div className="flex justify-center items-center bg-zinc-50 px-6 py-10">
        <Link href="/events">
          <Button className="rounded-sm h-10 bg-[#7A5C10] hover:bg-[#5C450C]">
            Events
          </Button>
        </Link>
      </div>
    );
  }

  if (loading || !eventsEnabled || !event) return null;

  const flyer = flyerImageUrl(event.flyer_url);
  const dateLabel = formatEventDateRange(event);
  const timeLabel = `${formatEventTime(event.start_time)} - ${formatEventTime(event.end_time)}`;

  return (
    <div className="flex flex-col md:flex-row justify-center items-center gap-8 md:gap-16 bg-zinc-50 px-6 md:px-16 py-12 md:py-15">
      {flyer && (
        <FlyerImage
          src={flyer}
          alt={`Flyer for ${event.title}`}
          title={event.title}
          className="w-full max-w-sm h-64 md:h-80 rounded-lg object-cover shadow-lg"
        />
      )}
      <div className="flex flex-col gap-3 font-noto-sans max-w-xl">
        <h2 className="text-xs uppercase tracking-widest text-[#7A5C10] font-semibold">
          Next Upcoming Event
        </h2>
        <h1 className="font-noto-sans text-3xl sm:text-4xl font-light">
          {event.title}
        </h1>
        <p className="text-black/50">
          {dateLabel} · {timeLabel}
        </p>
        {event.description && (
          <p className="text-sm md:text-base text-black/70 line-clamp-4">
            {event.description}
          </p>
        )}
        <div className="pt-2 flex gap-4">
          <Link href="/events">
            <Button className="rounded-sm h-10 bg-[#7A5C10] hover:bg-[#5C450C]">
              View All Events
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

function list0(events: Event[] | undefined): Event[] {
  return Array.isArray(events) ? events : [];
}
