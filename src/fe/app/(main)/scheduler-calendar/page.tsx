"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Music, Users } from "lucide-react";
import {
  fetchCalendarAssignments,
  type Assignment,
} from "@/lib/api";

export default function SchedulerCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const startDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
    const endDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;
    fetchCalendarAssignments(startDate, endDate).then((data) => setAssignments(data.data)).finally(() => setLoading(false));
  }, [currentMonth]);

  const monthName = new Date(currentMonth.year, currentMonth.month).toLocaleString("default", { month: "long" });

  const daysInMonth = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
  const firstDayOfWeek = new Date(currentMonth.year, currentMonth.month, 1).getDay();

  const prevMonth = () => {
    setCurrentMonth((prev) => {
      const m = prev.month === 0 ? 11 : prev.month - 1;
      const y = prev.month === 0 ? prev.year - 1 : prev.year;
      return { year: y, month: m };
    });
  };

  const nextMonth = () => {
    setCurrentMonth((prev) => {
      const m = prev.month === 11 ? 0 : prev.month + 1;
      const y = prev.month === 11 ? prev.year + 1 : prev.year;
      return { year: y, month: m };
    });
  };

  const dateKey = (day: number) =>
    `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

  const assignmentsForDay = (day: number) =>
    assignments.filter((a) => dateKey(day) === new Date(a.event_date).toISOString().split("T")[0]);

  if (loading) {
    return (
      <div className="container mx-auto py-12">
        <div className="flex justify-center items-center min-h-dvh">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-12 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground">Scheduler Calendar</h1>
        <p className="text-muted-foreground mt-1">
          View all assignments by date
        </p>
      </div>

      <div className="border rounded-lg overflow-hidden">
        {/* Month navigation */}
        <div className="flex items-center justify-between bg-muted p-4">
          <button onClick={prevMonth} className="p-2 hover:bg-muted-foreground/10 rounded">
            <ChevronLeft className="w-5 h-5" />
          </button>
          <h2 className="text-xl font-semibold">
            {monthName} {currentMonth.year}
          </h2>
          <button onClick={nextMonth} className="p-2 hover:bg-muted-foreground/10 rounded">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Weekday headers */}
        <div className="grid grid-cols-7 bg-muted border-b">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <div key={day} className="p-2 text-center text-sm font-medium text-muted-foreground">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div className="grid grid-cols-7">
          {Array.from({ length: firstDayOfWeek }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-[80px] bg-muted/30" />
          ))}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const dayAssignments = assignmentsForDay(day);
            const isToday =
              day === new Date().getDate() &&
              currentMonth.month === new Date().getMonth() &&
              currentMonth.year === new Date().getFullYear();
            return (
              <div
                key={day}
                className={`min-h-[80px] border p-1 ${
                  isToday ? "bg-blue-50" : "bg-background"
                }`}
              >
                <span className={`text-sm font-medium ${isToday ? "text-blue-600" : "text-foreground"}`}>
                  {day}
                </span>
                <div className="mt-1 space-y-0.5">
                  {dayAssignments.slice(0, 3).map((a, idx) => (
                    <div
                      key={idx}
                      className={`text-[10px] px-1 py-0.5 rounded truncate ${
                        a.type === "music"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-green-100 text-green-800"
                      }`}
                      title={`${a.type}: ${a.role}`}
                    >
                      {a.type === "music" ? (
                        <span className="inline-flex items-center gap-0.5">
                          <Music className="w-2 h-2" /> {a.role || "music"}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-0.5">
                          <Users className="w-2 h-2" /> {a.role || "service"}
                        </span>
                      )}
                    </div>
                  ))}
                  {dayAssignments.length > 3 && (
                    <div className="text-[10px] text-muted-foreground">+{dayAssignments.length - 3} more</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex gap-4 mt-4 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1">
          <Music className="w-3 h-3" /> Music
        </span>
        <span className="inline-flex items-center gap-1">
          <Users className="w-3 h-3" /> Service
        </span>
      </div>
    </div>
  );
}
