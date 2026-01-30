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

import CustomSidebarTrigger from "@/components/custom-sidebar-trigger"
import Link from "next/link"

import { useSidebar } from "@/components/ui/sidebar"

const data = {
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
      url: "/contact",
      empty: true,
      items: [

      ],
    },
  ],
}

export function NavSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {

  const {
    state,
    open,
    setOpen,
    openMobile,
    setOpenMobile,
    isMobile,
    toggleSidebar,
  } = useSidebar()

  return (
 <Sidebar className="" side="right" {...props}>
      <SidebarHeader className="items-end">
        <CustomSidebarTrigger state={true}/>
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
                  {item.empty ? <Link onClick={toggleSidebar} href={item.url}>{item.title}</Link> : item.title}
                  {item.empty ? <></> : (<ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90"/>)}
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="pl-5 pt-3">
                <SidebarGroupContent>
                  <SidebarMenu>
                    {item.items.map((item) => (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton className="text-xl" asChild>
                          <Link href={item.url} onClick={toggleSidebar}>{item.title}</Link>
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
