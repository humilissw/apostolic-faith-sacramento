"use client"

import AFCLogo from '@/components/AFCLogo'
import Link from "next/link"
import * as React from "react"
import { useState } from "react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger
} from "@/components/ui/navigation-menu"
import { useIsMobile } from "@/hooks/use-mobile"

import {
  Button
} from "@/components/ui/button"

import { NavSidebar } from "@/components/nav-sidebar"
import { Separator } from "@/components/ui/separator"
import {
  SidebarHeader,
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

import CustomTrigger from "@/components/sidebartrigger"


export default function Navbar() {
  const isMobile = useIsMobile()

  return (
    <div className="flex gap-35 justify-center items-center py-2 md:py-5 lg:gap-35 xl:gap-10 text-black bg-white">

    <div className="flex justify-center items-center xs:gap-40 sm:gap-110 md:gap-125 lg:mr-95 xl:mr-175 2xl:mr-275">
      <AFCLogo width={125} height={125}/>
      <div className="flex justify-center items-center lg:hidden">
        <SidebarProvider className='' >
        <NavSidebar />
        <CustomTrigger state={false}/>
        <SidebarInset className=''>
        </SidebarInset>
      </SidebarProvider>
      </div>
    </div>

    <NavigationMenu className="hidden lg:block absolute" viewport={isMobile}>
      <NavigationMenuList className="flex-wrap font-noto-sans">
      
        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger>About</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[150px] gap-4">
              <li>
                <NavigationMenuLink asChild>
                  <Link href="/doctrines">Our Beliefs</Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger className="">Resources</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[150px] gap-4">
              <li>
                <NavigationMenuLink asChild>
                  <Link href="#">Sermons</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="https://www.apostolicfaith.org/library/this-weeks-lessons">Sunday School Lessons</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="https://www.apostolicfaith.org/apostolic-faith-magazine">Apostolic Faith Magazine</Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuItem className="hidden md:block">
          <Link href="#" className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'>Contact Us</Link>
        </NavigationMenuItem>
       
      </NavigationMenuList>
    </NavigationMenu>

    <Button className="hidden lg:block md:bg-zinc-800 md:ml-60 md:rounded-md md:font-noto-sans" variant="default">LOGIN</Button>
  
    </div>
  )
}

function ListItem({
  title,
  children,
  href,
  ...props
}: React.ComponentPropsWithoutRef<"li"> & { href: string }) {
  return (
    <li {...props}>
      <NavigationMenuLink asChild>
        <Link href={href}>
          <div className="text-sm leading-none font-medium">{title}</div>
          <p className="text-muted-foreground line-clamp-2 text-sm leading-snug">
            {children}
          </p>
        </Link>
      </NavigationMenuLink>
    </li>
  )
}