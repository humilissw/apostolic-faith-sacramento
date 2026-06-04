"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/button";
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
} from "lucide-react";

import AFCLogo from "@/components/afc-logo";

const publicNav = [
  { title: "Home", url: "/", icon: Home },
  { title: "Our Beliefs", url: "/doctrines/", icon: BookOpen },
  { title: "Sermons", url: "https://www.youtube.com/@ApostolicFaithSacramento/streams", external: true, icon: Video },
  { title: "Media", url: "/media/", icon: Film },
  { title: "Donate", url: "/donate/", icon: CreditCard },
  { title: "Contact Us", url: "/contact/", icon: Mail },
];

interface NavItem {
  title: string;
  url: string;
  external?: boolean;
  icon: React.ComponentType<{ className?: string }>;
}

function NavItemLink({ item, isActive }: { item: NavItem; isActive: boolean }) {
  const className = `flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
    isActive
      ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
      : "text-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
  }`;

  return item.external ? (
    <a href={item.url} target="_blank" rel="noopener noreferrer" className={className}>
      <item.icon className="h-4 w-4" />
      {item.title}
    </a>
  ) : (
    <Link href={item.url} className={className}>
      <item.icon className="h-4 w-4" />
      {item.title}
    </Link>
  );
}

export default function Navbar() {
  const auth = useAuth();
  const pathname = usePathname();

  // Call all hooks at top level (unconditional)
  const enableHome = useFeatureFlag("enable_home");
  const enableDoctrines = useFeatureFlag("enable_doctrines");
  const enableMedia = useFeatureFlag("enable_media");
  const enableDonate = useFeatureFlag("enable_donate");
  const enableContact = useFeatureFlag("enable_contact");
  const enableVideoUploads = useFeatureFlag("enable_video_uploads");
  const enableSchedulerCalendar = useFeatureFlag("enable_scheduler_calendar");
  const enableSchedulerAdmin = useFeatureFlag("enable_scheduler_admin");
  const enableMyScheduler = useFeatureFlag("enable_my_scheduler");
  const enableUsersAdmin = useFeatureFlag("enable_users_admin");
  const enableVideoUploadsAdmin = useFeatureFlag("enable_video_uploads_admin");
  const enableIntegrations = useFeatureFlag("enable_integrations");
  const enableFlagsAdmin = useFeatureFlag("enable_flags_admin");

  const isAuthenticated = auth.isAuthenticated;

  const navItems: NavItem[][] = [];

  if (enableHome) {
    const publicItems = publicNav.filter((item) => {
      const flagMap: Record<string, boolean> = {
        "/": enableHome,
        "/doctrines/": enableDoctrines,
        "/media/": enableMedia,
        "/donate/": enableDonate,
        "/contact/": enableContact,
      };
      const enabled = flagMap[item.url];
      if (enabled === undefined) return true; // external links always show
      return enabled;
    }).map((item) => ({ ...item, url: item.url === "/" ? "/" : item.url }));
    if (publicItems.length > 0) {
      navItems.push(publicItems);
    }
  }

  if (isAuthenticated && enableVideoUploads) {
    navItems.push([
      { title: "Video Uploads", url: "/video-uploads/", icon: Video },
    ]);
  }

  if (isAuthenticated && enableSchedulerCalendar && (auth.hasScope("scheduler:admin") || auth.hasScope("member:limited"))) {
    const schedulerItems: NavItem[] = [
      { title: "Scheduler Calendar", url: "/scheduler-calendar/", icon: Calendar },
    ];
    if (auth.hasScope("scheduler:admin") && enableSchedulerAdmin) {
      schedulerItems.push({ title: "Scheduler Admin", url: "/scheduler-admin/", icon: Calendar });
    }
    if (enableMyScheduler && (auth.hasScope("scheduler:admin") || auth.hasScope("member:limited"))) {
      schedulerItems.push({ title: "My Scheduler", url: "/my-scheduler/", icon: Calendar });
    }
    if (schedulerItems.length > 0) {
      navItems.push(schedulerItems);
    }
  }

  if (isAuthenticated && auth.hasScope("superuser")) {
    const adminItems: NavItem[] = [];
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
      navItems.push(adminItems);
    }
  }

  return (
    <nav className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex flex-col gap-3">
          <div className="flex justify-center">
            <AFCLogo width={120} height={145} />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-1">
              {navItems.map((group) =>
                group.map((item) => (
                  <NavItemLink
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
            </div>

            <div className="flex items-center gap-2 ml-4">
              {isAuthenticated ? (
                <Button
                  className="font-noto-sans bg-black text-white hover:bg-gray-700"
                  size="sm"
                  onClick={() => auth.logout()}
                >
                  Logout
                </Button>
              ) : (
                <Link href="/login/">
                  <Button
                    className="font-noto-sans bg-black text-white hover:bg-gray-700"
                    size="sm"
                  >
                    Login
                  </Button>
                </Link>
              )}
            </div>
          </div>

          {isAuthenticated && (
            <>
              <Separator className="my-1" />
              <div className="flex items-center gap-3 pt-1 pb-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  {isAuthenticated ? "Signed in" : "Guest"}
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
