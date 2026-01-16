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

import CustomTrigger from "@/components/sidebartrigger"

// This is sample data.
const data = {
  versions: ["1.0.1", "1.1.0-alpha", "2.0.0-beta1"],
  navMain: [
    {
      title: "Getting Started",
      url: "#",
      items: [
        {
          title: "About",
          url: "#",
          isActive: true,
        },
        {
          title: "Resources",
          url: "#",
        },
        {
          title: "Events",
          url: "#",
        },
        {
          title: "Give",
          url: "#",
        },
        {
          title: "Contact Us",
          url: "#",
        },
      ],
    },
  ],
}

export function NavSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar className="" side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomTrigger state={true}/>
      </SidebarHeader>
      <SidebarContent className="">
        {/* We create a SidebarGroup for each parent. */}
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((item) => (
                  <SidebarMenuItem className="pb-10" key={item.title}>
                    <SidebarMenuButton className="text-3xl" asChild /*isActive={item.isActive}*/>
                      <a href={item.url}>{item.title}</a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
