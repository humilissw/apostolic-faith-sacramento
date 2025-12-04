"use client"

import * as React from "react"
import Link from "next/link"
import HomepageImage from '@/components/ChurchLogo'

import { useIsMobile } from "@/hooks/use-mobile"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

import {
  Button
} from "@/components/ui/button"

export default function NavigationMenuDemo() {
  const isMobile = useIsMobile()

  return (
    <div className="flex justify-center items-center py-2 text-black bg-transparent">

    <div className="flex gap-5 justify-center items-center mr-250">
      <HomepageImage width={125} height={125}/>

    </div>

    <NavigationMenu className="absolute" viewport={isMobile}>
      <NavigationMenuList className="flex-wrap font-lora">
      
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
          <NavigationMenuTrigger>Resources</NavigationMenuTrigger>
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

    <Button className="bg-zinc-800 ml-60 rounded-md" variant="default">LOGIN</Button>
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