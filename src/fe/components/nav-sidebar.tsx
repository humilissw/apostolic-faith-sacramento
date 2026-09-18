import * as React from "react"


import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"

import CustomTrigger from "@/components/sidebar-trigger"
import { useState } from "react";
import { usePathname } from "next/dist/client/components/navigation";
import { useAuth } from "@/context/auth-context";
import { useFeatureFlag } from "@/context/feature-flag-context";

const navMain = [
      {
        title: "Home",
        url: "/",
      },
      {
        title: "Our Beliefs",
        url: "/doctrines/",
      },
      {
        title: "Sermons",
        url: "https://www.youtube.com/@ApostolicFaithSacramento/streams",
        external: true
      },
      {
        title: "Events",
        url: "/events/",
      },
      {
        title: "Media",
        url: "/media/",
      },
      {
        title: "Donate",
        url: "/donate/",
      },
      {
        title: "Contact Us",
        url: "/contact/",
      },
  ]

  interface NavItem {
    title: string;
    url: string;
    external?: boolean;
  }


export function NavSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {

  const auth = useAuth();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Call all hooks at top level (unconditional)
  const enableHome = useFeatureFlag("enable_home");
  const enableDoctrines = useFeatureFlag("enable_doctrines");
  const enableMedia = useFeatureFlag("enable_media");
  const enableDonate = useFeatureFlag("enable_donate");
  const enableContact = useFeatureFlag("enable_contact");
  const enableEvents = useFeatureFlag("enable_events");

  const isAuthenticated = auth.isAuthenticated;

  const navItems: NavItem[][] = [];

  if (enableHome) {
    const publicItems = navMain.filter((item) => {
      const flagMap: Record<string, boolean> = {
        "/": enableHome,
        "/doctrines/": enableDoctrines,
        "/events/": enableEvents,
        "/media/": enableMedia,
        "/donate/": enableDonate,
        "/contact/": enableContact,
      };
      const enabled = flagMap[item.url];
      // External links (no flag) always show; internal links without a
      // registered flag stay hidden so a missing mapping can never leak a
      // disabled page into the navbar.
      if (enabled === undefined) return Boolean(item.external);
      return enabled;
    }).map((item) => ({ ...item, url: item.url === "/" ? "/" : item.url }));
    if (publicItems.length > 0) {
      navItems.push(publicItems);
    }
  }

  return (
    <Sidebar side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomTrigger state={true}/>
      </SidebarHeader>
      <SidebarContent className="px-5">
        {/* We create a SidebarGroup for each parent. */}
              <SidebarMenu>
                {navItems.map((group) => (
                  group.map((item) => (
                    <SidebarMenuItem className="pb-10" key={item.title}>
                      <SidebarMenuButton className="text-3xl" asChild >
                        {item.external ? (
                          <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.title}
                          </a>
                        ) : (
                          <a href={item.url}>
                            {item.title}
                          </a>
                        )}
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))
                ))}
              </SidebarMenu>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
