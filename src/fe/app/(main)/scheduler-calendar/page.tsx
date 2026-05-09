"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Music, Users, Clock } from "lucide-react";
import {
  fetchCalendarAssignments,
  fetchMyTimeOffRequests,
  createTimeOffRequest,
  fetchMyCalendar,
  type Assignment,
  type TimeOffRequest,
} from "@/lib/api";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export default function SchedulerCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const [calendarAssignments, setCalendarAssignments] = useState<Assignment[]>([]);
  const [myAssignments, setMyAssignments] = useState<Assignment[]>([]);
  const [myTimeOff, setMyTimeOff] = useState<TimeOffRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTimeOffDialog, setShowTimeOffDialog] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [timeOffNote, setTimeOffNote] = useState("");
  const [timeOffSubmitting, setTimeOffSubmitting] = useState(false);

  useEffect(() => {
    const startDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
    const endDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

    const loadData = async () => {
      try {
        const [calRes, myCalRes, timeOffRes] = await Promise.all([
          fetchCalendarAssignments(startDate, endDate),
          fetchMyCalendar(startDate, endDate),
          fetchMyTimeOffRequests(),
        ]);
        setCalendarAssignments(calRes.data);
        setMyAssignments(myCalRes.data);
        setMyTimeOff(timeOffRes.data);
      } catch {
        toast.error("Failed to load calendar data");
      } finally {
        setLoading(false);
      }
    };
    loadData();
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

  const calendarAssignmentsForDay = (day: number) =>
    calendarAssignments.filter((a) => dateKey(day) === new Date(a.event_date).toISOString().split("T")[0]);

  const myAssignmentsForDay = (day: number) =>
    myAssignments.filter((a) => dateKey(day) === new Date(a.event_date).toISOString().split("T")[0]);

  const timeOffForDay = (day: number) =>
    myTimeOff.find((t) => dateKey(day) === new Date(t.date).toISOString().split("T")[0]);

  const dayClass = (day: number): string => {
    const myCount = myAssignmentsForDay(day).length;
    const timeOff = timeOffForDay(day);
    if (timeOff) {
      return timeOff.status === "approved"
        ? "bg-green-50 border-green-200"
        : timeOff.status === "declined"
        ? "bg-red-50 border-red-200"
        : "bg-yellow-50 border-yellow-200";
    }
    if (myCount > 3) return "bg-red-100 border-red-200";
    if (myCount > 0) return "bg-green-100 border-green-200";
    return "bg-background border-border";
  };

  const handleRequestTimeOff = async () => {
    if (!selectedDate) return;
    setTimeOffSubmitting(true);
    try {
      await createTimeOffRequest({ date: selectedDate + "T00:00:00", notes: timeOffNote || null });
      const res = await fetchMyTimeOffRequests();
      setMyTimeOff(res.data);
      setShowTimeOffDialog(false);
      setTimeOffNote("");
      toast.success("Time-off request submitted");
    } catch {
      toast.error("Failed to submit time-off request");
    } finally {
      setTimeOffSubmitting(false);
    }
  };

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
          View assignments by date
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
            <div key={`empty-${i}`} className={`min-h-[100px] ${dayClass(firstDayOfWeek + i + 1)}`} />
          ))}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const calDays = calendarAssignmentsForDay(day);
            const myDays = myAssignmentsForDay(day);
            const dayTimeOff = timeOffForDay(day);
            const isToday =
              day === new Date().getDate() &&
              currentMonth.month === new Date().getMonth() &&
              currentMonth.year === new Date().getFullYear();
            const isUnassigned = myDays.length === 0 && calDays.length > 0 && !dayTimeOff;

            return (
              <div
                key={day}
                className={`min-h-[100px] border p-1 ${dayClass(day)} ${
                  isUnassigned ? "cursor-pointer hover:opacity-80" : ""
                }`}
                onClick={isUnassigned ? () => {
                  setSelectedDate(dateKey(day));
                  setShowTimeOffDialog(true);
                } : undefined}
              >
                <div className="flex justify-between items-start">
                  <span className={`text-sm font-medium ${isToday ? "text-blue-600" : "text-foreground"}`}>
                    {day}
                  </span>
                  {dayTimeOff && (
                    <span className={`text-[10px] px-1 py-0.5 rounded ${
                      dayTimeOff.status === "approved"
                        ? "bg-green-100 text-green-700"
                        : dayTimeOff.status === "declined"
                        ? "bg-red-100 text-red-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}>
                      TO
                    </span>
                  )}
                </div>
                <div className="mt-1 space-y-0.5">
                  {calDays.slice(0, 3).map((a, idx) => (
                    <div
                      key={idx}
                      className={`text-[10px] px-1 py-0.5 rounded truncate ${
                        a.type === "music"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-green-100 text-green-800"
                      } ${myDays.some((m) => m.id === a.id) ? "ring-1 ring-green-400" : ""}`}
                      title={`${a.type}: ${a.role} - ${a.user_id}`}
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
                  {calDays.length > 3 && (
                    <div className="text-[10px] text-muted-foreground">+{calDays.length - 3} more</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex gap-4 mt-4 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-3 bg-green-100 rounded" /> Your Assignment
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="w-3 h-3 bg-red-100 rounded" /> Over 3 Days
        </span>
        <span className="inline-flex items-center gap-1">
          <Clock className="w-3 h-3" /> Time Off
        </span>
      </div>

      <AlertDialog open={showTimeOffDialog} onOpenChange={setShowTimeOffDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Request Time Off</AlertDialogTitle>
            <AlertDialogDescription>
              You have no assignment on {selectedDate}.
              <div className="mt-3 space-y-2">
                <label htmlFor="timeoff-note" className="text-sm font-medium">Notes (optional)</label>
                <input
                  id="timeoff-note"
                  className="w-full border rounded-md px-3 py-2 text-sm"
                  placeholder="Reason for time off..."
                  value={timeOffNote}
                  onChange={(e) => setTimeOffNote(e.target.value)}
                />
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRequestTimeOff}
              disabled={timeOffSubmitting}
            >
              {timeOffSubmitting ? "Submitting..." : "Submit"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
