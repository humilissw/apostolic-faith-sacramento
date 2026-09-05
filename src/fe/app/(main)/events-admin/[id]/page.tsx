// TODO: fetch event details with fetchEvent(id) once the detail view is implemented.

export function generateStaticParams() {
  // output: 'export' requires at least one path for this dynamic route.
  return [{ id: 'placeholder' }];
}

export default function EventDetailPage() {
    return (
      <div className="flex flex-col md:items-center md:justify-center bg-[#373434] text-white mt-auto">
        Hello, this is the event detail page. This page will show the details of a specific event.
        </div>
    )
}
