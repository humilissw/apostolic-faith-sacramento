import { Button } from "@/components/ui/button"
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { useFeatureFlag } from "@/context/feature-flag-context";

import { Separator } from "@/components/ui/separator";
import {
  Home,
  BookOpen,
  Video,
  Film,
  CreditCard,
  Mail,
  Calendar,
  Users,
  Settings,
  ToggleRight,
  User,
  CircleUserRound,
  Circle,
  ShieldIcon,
  X,
  XIcon
} from "lucide-react";

import AFCLogo from "@/components/afc-logo";
import { AnimatedSheet } from "./animated-sheet";
import { useState } from "react";

const publicNav = [
  { title: "Home", url: "/", icon: Home },
  { title: "Our Beliefs", url: "/doctrines/", icon: BookOpen },
  { title: "Sermons", url: "https://www.youtube.com/@ApostolicFaithSacramento/streams", external: true, icon: Video },
  { title: "Media", url: "/media/", icon: Film },
  { title: "Donate", url: "/donate/", icon: CreditCard },
  { title: "Contact Us", url: "/contact/", icon: Mail },
];

interface DrawerItem {
  title: string;
  url: string;
  external?: boolean;
  icon: React.ComponentType<{ className?: string }>;
}

function DrawerItemLink({ item, isActive }: { item: DrawerItem; isActive: boolean }) {
  const className = `flex justify-start items-center rounded-md h-auto text-sm p-4 transition-colors gap-2 ${
    isActive
      ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
      : "text-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
  }`;

  return item.external ? (
    <a href={item.url} target="_blank" rel="noopener noreferrer" className={className}>
      {<item.icon className="h-4 w-4" />}
      {item.title}
    </a>
  ) : (
    <Link href={item.url} className={className}>
      {<item.icon className="h-4 w-4" />}
      {item.title}
    </Link>
  );
}

export function AdminMenu() {
      const auth = useAuth();
      const pathname = usePathname();
      const [open, setOpen] = useState(false);

      // Call all hooks at top level (unconditional)
      const enableVideoUploads = useFeatureFlag("enable_video_uploads");
      const enableSchedulerCalendar = useFeatureFlag("enable_scheduler_calendar");
      const enableSchedulerAdmin = useFeatureFlag("enable_scheduler_admin");
      const enableMyScheduler = useFeatureFlag("enable_my_scheduler");
      const enableUsersAdmin = useFeatureFlag("enable_users_admin");
      const enableVideoUploadsAdmin = useFeatureFlag("enable_video_uploads_admin");
      const enableIntegrations = useFeatureFlag("enable_integrations");
      const enableFlagsAdmin = useFeatureFlag("enable_flags_admin");

      const isAuthenticated = auth.isAuthenticated;

      const drawerItems: DrawerItem[][] = [];

      if (isAuthenticated && enableVideoUploads) {
        drawerItems.push([
          { title: "Video Uploads", url: "/video-uploads/", icon: Video },
        ]);
      }

      if (isAuthenticated && enableSchedulerCalendar && (auth.hasScope("scheduler:admin") || auth.hasScope("member:limited"))) {
        const schedulerItems: DrawerItem[] = [
          { title: "Scheduler Calendar", url: "/scheduler-calendar/", icon: Calendar },
        ];
        if (auth.hasScope("scheduler:admin") && enableSchedulerAdmin) {
          schedulerItems.push({ title: "Scheduler Admin", url: "/scheduler-admin/", icon: Calendar });
        }
        if (enableMyScheduler && (auth.hasScope("scheduler:admin") || auth.hasScope("member:limited"))) {
          schedulerItems.push({ title: "My Scheduler", url: "/my-scheduler/", icon: Calendar });
        }
        if (schedulerItems.length > 0) {
          drawerItems.push(schedulerItems);
        }
      }

      if (isAuthenticated && auth.hasScope("superuser")) {
        const adminItems: DrawerItem[] = [];
        if (enableUsersAdmin) {
          adminItems.push({ title: "User Management", url: "/users-admin/", icon: Users });
        }
        if (enableVideoUploadsAdmin) {
          adminItems.push({ title: "Video Upload Admin", url: "/video-uploads-admin/", icon: Film });
        }
        if (enableIntegrations) {
          adminItems.push({ title: "Integrations", url: "/integrations/", icon: Settings });
        }
        if (enableFlagsAdmin) {
          adminItems.push({ title: "Feature Flags", url: "/flags-admin/", icon: ToggleRight });
        }
        if (adminItems.length > 0) {
          drawerItems.push(adminItems);
        }
      }
  return (
    <Drawer open={open} onOpenChange={setOpen} direction="right">
      <DrawerTrigger asChild>
        <Button onClick={() => setOpen(true)} className="bg-zinc-300 hover:bg-zinc-400" variant="outline" size="sm">Admin <ShieldIcon className="w-4 h-4" /></Button>
      </DrawerTrigger>
      <DrawerContent aria-describedby={undefined}>
        <DrawerHeader className="flex flex-row justify-between pb-3 ">
          <DrawerTitle className="">Admin Menu</DrawerTitle>
          <button onClick={() => setOpen(false)}>
            <XIcon color="gray"/>
          </button>
        </DrawerHeader>
            <div className="flex-1 overflow-y-auto">
                {drawerItems.map((group) =>
                group.map((item) => (
                  <DrawerItemLink
                    key={item.title}
                    item={item}
                    isActive={
                      item.external
                        ? false
                        : item.url === "/"
                          ? pathname === "/" || pathname === ""
                          : pathname.startsWith(item.url)
                    }
                  />
                ))
              )}
              <button
                className = "flex justify-start items-center rounded-md h-auto w-full text-sm p-4 transition-colors gap-2 border-t text-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                onClick={() => auth.logout()}
              >
                <CircleUserRound className="w-4 h-4"/> Log out
              </button>
            </div>
      </DrawerContent>
    </Drawer>
  )
}
