import * as React from "react"
import { ChevronRight } from "lucide-react"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

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
      title: "About",
      url: "#",
      empty: false,
      items: [
        {
          title: "Our Beliefs",
          url: "/doctrines",
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
        },
        {
          title: "Sunday School Lessons",
          url: "https://www.apostolicfaith.org/library/this-weeks-lessons",
        },
        {
          title: "Apostolic Faith Magazine",
          url: "https://www.apostolicfaith.org/apostolic-faith-magazine",
        },
      ],
    },
    {
      title: "Contact Us",
      url: "#",
      empty: true,
      items: [

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
      <SidebarContent className="pl-3">
        {/* We create a collapsible SidebarGroup for each parent. */}
        {data.navMain.map((item) => (
          <Collapsible
            key={item.title}
            title={item.title}
            className="group/collapsible"
          >
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="group/label font-normal text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-2xl"
              >
                <CollapsibleTrigger className="">
                  {item.title}{" "}
                  {item.empty ? <></> : (<ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90"/>)}
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="pl-5 pt-3">
                <SidebarGroupContent>
                  <SidebarMenu>
                    {item.items.map((item) => (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton className="text-xl" asChild /*isActive={item.isActive}*/>
                          <a href={item.url}>{item.title}</a>
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
      <SidebarRail />
    </Sidebar>
  )
}


/*
  <Sidebar className="" side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomTrigger state={true}/>
      </SidebarHeader>
      <SidebarContent className="pl-3">
        {/* We create a SidebarGroup for each parent.*/ /*
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((item) => (
                  <SidebarMenuItem className="pb-10" key={item.title}>
                    <SidebarMenuButton className="text-2xl" asChild /*isActive={item.isActive}*/
/*                      <a href={item.url}>{item.title}</a>
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
    
*/