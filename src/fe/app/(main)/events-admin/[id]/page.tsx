'use client';

import { fetchEvent, type Event } from '@/lib/api';

export default function EventDetailPage({
    params, 
}: {
    params: { id: string };
}) {

    const event = null; // Replace with actual event fetching logic using params.id


    return (
      <div className="flex flex-col md:items-center md:justify-center bg-[#373434] text-white mt-auto">
        Hello, this is the event detail page. This page will show the details of a specific event.
        </div>
    )
}
