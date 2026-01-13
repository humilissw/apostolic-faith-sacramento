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

import Hamburger from 'hamburger-react';


export default function NavigationMenuDemo() {
  const isMobile = useIsMobile()
  const [isOpen, setOpen] = useState(false)

  return (
    <div className="flex gap-35 justify-center items-center py-2 md:py-2 text-black bg-transparent">

    <div className="flex md:gap-5 md:justify-center md:items-center md:mr-95 lg:mr-95 xl:mr-175 2xl:mr-250">
      <AFCLogo width={125} height={125}/>
    </div>

    <NavigationMenu className="hidden lg:block absolute" viewport={isMobile}>
      <NavigationMenuList className="flex-wrap font-noto-sans">
      
        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger>About</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[150px] gap-4">
              <li>
                <NavigationMenuLink asChild>
                  <Link href="#">About Us</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Our Beliefs</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Our History</Link>
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
                  <Link href="#">Sunday School Lessons</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Curriclum</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Apostolic Faith Magazine</Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger>Events</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[150px] gap-4">
              <li>
                <NavigationMenuLink asChild>
                  <Link href="#">Calendar</Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger>Give</NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[150px] gap-4">
              <li>
                <NavigationMenuLink asChild>
                  <Link href="#">Components</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Documentation</Link>
                </NavigationMenuLink>
                <NavigationMenuLink asChild>
                  <Link href="#">Blocks</Link>
                </NavigationMenuLink>
              </li>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>

        <NavigationMenuItem className="hidden md:block">
          <NavigationMenuTrigger>Contact Us</NavigationMenuTrigger>
        </NavigationMenuItem>
       
      </NavigationMenuList>
    </NavigationMenu>

    <Button className="hidden lg:block md:bg-zinc-800 md:ml-60 md:rounded-md md:font-noto-sans" variant="default">LOGIN</Button>
    <div className="lg:hidden">
      <Hamburger toggled={isOpen} toggle={setOpen} />
    </div>
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