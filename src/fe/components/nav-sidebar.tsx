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

// This is sample data.
const data = {
  versions: ["1.0.1", "1.1.0-alpha", "2.0.0-beta1"],
  navMain: [
    {
      title: "Getting Started",
      url: "#",
      items: [
        {
          title: "Home",
          url: "/",
          target: "_self",
          rel: undefined,
        },
        {
          title: "Our Beliefs",
          url: "/doctrines/",
          target: "_self",
          rel: undefined,
        },
        {
          title: "Sermons",
          url: "https://www.youtube.com/@ApostolicFaithSacramento/streams",
          target: "_blank",
          rel: "noopener noreferrer",
        },
        {
          title: "Media",
          url: "/media/",
          target: "_self",
          rel: undefined,
        },
        {
          title: "Donate",
          url: "/donate/",
          target: "_self",
          rel: undefined,
        },
        {
          title: "Contact Us",
          url: "/contact/",
          target: "_self",
          rel: undefined,
        },
      ],
    },
  ],
}

export function NavSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomTrigger state={true}/>
      </SidebarHeader>
      <SidebarContent className="px-5">
        {/* We create a SidebarGroup for each parent. */}
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((item) => (
                  <SidebarMenuItem className="pb-10" key={item.title}>
                    <SidebarMenuButton className="text-3xl" asChild >
                      <a href={item.url} target={item.target} rel={item.rel}>
                        {item.title}
                      </a>
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
