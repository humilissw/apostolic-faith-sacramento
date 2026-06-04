"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Music, Users, Clock, Crown } from "lucide-react";
import {
  fetchCalendarWithNames,
  fetchMyTimeOffRequests,
  fetchMyCalendar,
  fetchUsersWithScopes,
  type Assignment,
  type TimeOffRequest,
  type UserWithScopes,
} from "@/lib/api";
import { toast } from "sonner";
import DayDetailDialog from "@/components/day-detail-dialog";

export default function SchedulerCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const [calendarAssignments, setCalendarAssignments] = useState<Assignment[]>([]);
  const [myAssignments, setMyAssignments] = useState<Assignment[]>([]);
  const [myTimeOff, setMyTimeOff] = useState<TimeOffRequest[]>([]);
  const [users, setUsers] = useState<UserWithScopes[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDateForDialog, setSelectedDateForDialog] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [usersRes] = await Promise.all([
          fetchUsersWithScopes(),
        ]);
        setUsers(usersRes.data);
      } catch {
        toast.error("Failed to load users");
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    const startDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
    const endDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

    const loadData = async () => {
      setLoading(true);
      try {
        const [calRes, myCalRes, timeOffRes] = await Promise.all([
          fetchCalendarWithNames(startDate, endDate),
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

  const handleRefresh = () => {
    const startDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-01`;
    const lastDay = new Date(currentMonth.year, currentMonth.month + 1, 0).getDate();
    const endDate = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;
    Promise.all([
      fetchCalendarWithNames(startDate, endDate),
      fetchMyCalendar(startDate, endDate),
      fetchMyTimeOffRequests(),
    ]).then(([calRes, myCalRes, timeOffRes]) => {
      setCalendarAssignments(calRes.data);
      setMyAssignments(myCalRes.data);
      setMyTimeOff(timeOffRes.data);
    }).catch(() => {
      toast.error("Failed to refresh calendar data");
    });
  };

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

  const handleDayClick = (day: number) => {
    const dk = dateKey(day);
    const calDays = calendarAssignmentsForDay(day);
    const myDays = myAssignmentsForDay(day);
    // Only make days clickable if they have assignments or time-off
    if (calDays.length > 0 || myDays.length > 0 || timeOffForDay(day)) {
      setSelectedDateForDialog(dk);
      setDialogOpen(true);
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

            return (
              <div
                key={day}
                className={`min-h-[100px] border p-1 ${dayClass(day)} ${
                  (calDays.length > 0 || myDays.length > 0 || dayTimeOff) ? "cursor-pointer hover:opacity-80" : ""
                }`}
                onClick={() => handleDayClick(day)}
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
                      title={`${a.type}: ${a.role}${a.group_leader ? " (Group Leader)" : ""}`}
                    >
                      <span className="inline-flex items-center gap-0.5">
                        {a.type === "music" ? (
                          <Music className="w-2 h-2" />
                        ) : (
                          <Users className="w-2 h-2" />
                        )}
                        {a.user_full_name || a.user_email}
                        {a.group_leader ? (
                          <Crown className="w-2 h-2 text-amber-500" />
                        ) : null}
                      </span>
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

      {selectedDateForDialog && (
        <DayDetailDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          date={selectedDateForDialog}
          assignments={calendarAssignmentsForDay(Number(selectedDateForDialog.split("-")[2]))}
          myAssignments={myAssignmentsForDay(Number(selectedDateForDialog.split("-")[2]))}
          timeOff={timeOffForDay(Number(selectedDateForDialog.split("-")[2]))}
          users={users.map((u) => ({ id: u.id, email: u.email }))}
          isAdmin={true}
          onRefresh={handleRefresh}
        />
      )}
    </div>
  );
}
