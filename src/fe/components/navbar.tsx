"use client";

import AFCLogo from "@/components/afc-logo";
import Link from "next/link";
import * as React from "react";
import { useEffect, useState } from "react";

import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import { useIsMobile } from "@/hooks/use-mobile";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/auth-context";

import { NavSidebar } from "@/components/nav-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

import CustomSidebarTrigger from "@/components/custom-sidebar-trigger";

export default function Navbar() {
  const isMobile = useIsMobile();
  const auth = useAuth();

  return (
    <div className="relative flex gap-35 justify-center items-center py-2 md:py-5 lg:gap-35 xl:gap-10 text-black bg-white">
      <div className="flex justify-center items-center">
        <AFCLogo width={125} height={125} />
        <div className="flex items-center lg:hidden">
          <SidebarProvider>
            <NavSidebar />
            <CustomSidebarTrigger state={false} />
            <SidebarInset />
          </SidebarProvider>
        </div>

        <NavigationMenu className="hidden lg:block " viewport={isMobile}>
          <NavigationMenuList className="flex-wrap font-noto-sans mr-10">
            <NavigationMenuItem className="hidden md:block">
              <NavigationMenuTrigger>About</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[150px] gap-4">
                  <li>
                    <NavigationMenuLink asChild>
                      <Link href="/doctrines/">Our Beliefs</Link>
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
                      <Link
                        target="_blank"
                        rel="noopener noreferrer"
                        href="https://www.youtube.com/@ApostolicFaithSacramento/streams"
                      >
                        Sermons
                      </Link>
                    </NavigationMenuLink>
                    <NavigationMenuLink asChild>
                      <Link
                        target="_blank"
                        rel="noopener noreferrer"
                        href="https://www.apostolicfaith.org/library/this-weeks-lessons"
                      >
                        Sunday School Lessons
                      </Link>
                    </NavigationMenuLink>
                    <NavigationMenuLink asChild>
                      <Link
                        target="_blank"
                        rel="noopener noreferrer"
                        href="https://www.apostolicfaith.org/apostolic-faith-magazine"
                      >
                        Apostolic Faith Magazine
                      </Link>
                    </NavigationMenuLink>
                  </li>
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>

            <NavigationMenuItem className="hidden md:block">
              <Link
                href="/media/"
                className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
              >
                Media
              </Link>
            </NavigationMenuItem>

            <NavigationMenuItem className="hidden md:block">
              <Link
                href="/contact/"
                className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
              >
                Contact Us
              </Link>
            </NavigationMenuItem>

            <NavigationMenuItem className="hidden md:block">
              <Link
                href="/donate/"
                className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium bg-green-600 text-white hover:bg-green-700 focus:bg-green-700 focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-green-700 data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-green-700 data-[state=open]:bg-green-700/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
              >
                Donate
              </Link>
            </NavigationMenuItem>

            {auth.isAuthenticated && (
              <NavigationMenuItem className="hidden md:block">
                <Link
                  href="/video-uploads/"
                  className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
                >
                  Video Uploads
                </Link>
              </NavigationMenuItem>
            )}
            {auth.isAuthenticated && (
              <NavigationMenuItem className="hidden md:block">
                <Link
                  href="/integrations/"
                  className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
                >
                  Integrations
                </Link>
              </NavigationMenuItem>
            )}
            {auth.isAuthenticated && auth.hasScope("superuser") && (
              <NavigationMenuItem className="hidden md:block">
                <Link
                  href="/users-admin/"
                  className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
                >
                  User Management
                </Link>
              </NavigationMenuItem>
            )}
            {auth.isAuthenticated && auth.hasScope("superuser") && (
              <NavigationMenuItem className="hidden md:block">
                <Link
                  href="/video-uploads-admin/"
                  className='group inline-flex h-9 w-max items-center justify-center rounded-md cursor-pointer px-7 py-2 text-base tracking-[0.04em] font-medium hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50 data-[state=open]:hover:bg-accent data-[state=open]:text-accent-foreground data-[state=open]:focus:bg-accent data-[state=open]:bg-accent/50 focus-visible:ring-ring/50 outline-none transition-[color,box-shadow] focus-visible:ring-[3px] focus-visible:outline-1"'
                >
                  Video Upload Admin
                </Link>
              </NavigationMenuItem>
            )}
          </NavigationMenuList>
        </NavigationMenu>

        <div className="absolute right-8 hidden lg:block gap-4 flex items-center">
          {auth.isAuthenticated ? (
            <>
              <Button
                className="font-noto-sans bg-black text-white hover:bg-gray-700"
                size="default"
                variant="default"
                onClick={() => auth.logout()}
              >
                Logout
              </Button>
            </>
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
        </div>
      </div>
    </div>
  );
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
  );
}
