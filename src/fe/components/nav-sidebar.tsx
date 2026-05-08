import * as React from "react";
import { ChevronRight } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";

import CustomSidebarTrigger from "@/components/custom-sidebar-trigger";
import Link from "next/link";

import { useSidebar } from "@/components/ui/sidebar";
import { useAuth } from "@/context/auth-context";
import { Button } from "./ui/button";

const data = {
  navMain: [
    {
      title: "About",
      url: "#",
      empty: false,
      items: [
        {
          title: "Our Beliefs",
          url: "/doctrines/",
          target: "_self",
          isActive: true,
        },
      ],
    },
    {
      title: "Resources",
      url: "#",
      empty: false,
      items: [
        {
          title: "Sermons",
          url: "https://www.youtube.com/@ApostolicFaithSacramento/streams",
          target: "_blank",
        },
        {
          title: "Sunday School Lessons",
          url: "https://www.apostolicfaith.org/library/this-weeks-lessons",
          target: "_blank",
        },
        {
          title: "Apostolic Faith Magazine",
          url: "https://www.apostolicfaith.org/apostolic-faith-magazine",
          target: "_blank",
        },
      ],
    },
    {
      title: "Media",
      url: "/media/",
      target: "_self",
      empty: true,
      items: [],
    },
    {
      title: "Donate",
      url: "/donate/",
      target: "_self",
      empty: true,
      items: [],
    },
    {
      title: "Contact Us",
      url: "/contact/",
      target: "_self",
      empty: true,
      items: [],
    },
  ],
};

function NavSidebarContent({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { isAuthenticated, hasScope, logout } = useAuth();

  if (!isAuthenticated) return null;

  return (
    <Sidebar className="" side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomSidebarTrigger state={true} />
      </SidebarHeader>

      <SidebarContent className="pl-3">
        {isAuthenticated && (
          <Collapsible key="video-uploads" className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                <Link href="/video-uploads/">Video Uploads</Link>
              </SidebarGroupLabel>
            </SidebarGroup>
          </Collapsible>
        )}
        {isAuthenticated && hasScope("superuser") && (
          <Collapsible key="integrations" className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                <Link href="/integrations/">Integrations</Link>
              </SidebarGroupLabel>
            </SidebarGroup>
          </Collapsible>
        )}
        {isAuthenticated && hasScope("superuser") && (
          <Collapsible key="user-management" className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                <Link href="/users-admin/">User Management</Link>
              </SidebarGroupLabel>
            </SidebarGroup>
          </Collapsible>
        )}
        {isAuthenticated && hasScope("superuser") && (
          <Collapsible key="video-admin" className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                <Link href="/video-uploads-admin/">Video Uploads</Link>
              </SidebarGroupLabel>
            </SidebarGroup>
          </Collapsible>
        )}
        {/* We create a collapsible SidebarGroup for each parent. */}
        {data.navMain.map((item) => (
          <Collapsible
            key={item.title}
            //title={item.title}
            className="group/collapsible"
          >
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                {item.empty ? (
                  <Link href={item.url}>{item.title}</Link>
                ) : (
                  <CollapsibleTrigger className="">
                    {item.title}{" "}
                    <ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90" />
                  </CollapsibleTrigger>
                )}
              </SidebarGroupLabel>
              <CollapsibleContent className="pl-5 pt-3">
                <SidebarGroupContent>
                  <SidebarMenu>
                    {item.items.map((item) => (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton className="text-xl" asChild>
                          <Link target={item.target} href={item.url}>
                            {item.title}
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
        ))}
      </SidebarContent>

      <SidebarFooter className="items-end mr-2 mb-2">
        {isAuthenticated ? (
          <Button
            className="font-noto-sans bg-black text-white hover:bg-gray-700"
            size="default"
            variant="default"
            onClick={() => logout()}
          >
            Logout
          </Button>
        ) : (
          <Link href="/login/">
            <Button
              className="font-noto-sans bg-black text-white hover:bg-gray-700"
              size="default"
              variant="default"
            >
              Login
            </Button>
          </Link>
        )}
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}

export function NavSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  // Render null outside AuthProvider
  try {
    return <NavSidebarContent {...props} />;
  } catch {
    return <Sidebar className="" side="right" {...props} />;
  }
}
