"use client";

import { useFeatureFlag } from "@/context/feature-flag-context";
import {
  Button
} from "@/components/ui/button";
import Link from "next/link";

import HomepageParagraph from "@/components/homepage-paragraph"

export default function Home() {
  const homeEnabled = useFeatureFlag("enable_home");

  if (!homeEnabled) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return (
    <div>
    <div className="w-full flex items-start justify-center xl:justify-start relative min-h-[100dvh] pb-20 sm:pb-32 md:pb-40 before:content-[''] before:absolute before:inset-0 before:bg-[url('../public/option2-copy.jpg')] before:bg-cover before:bg-center before:bg-fixed before:opacity-90 before:z-[-2] after:content-[''] after:absolute after:inset-0 after:bg-black/48 after:z-[-1]">
      <div className="font-noto-sans 2xs:text-center xl:text-left text-shadow-lg/20 pb-16 2xs:landscape:pt-45 2xs:portrait:pt-50 lg:pt-56 xl:pl-24">
      <div className="flex flex-col gap-4 font-light px-3">
        <h1 className="2xs:leading-12 md:leading-17 lg:leading-20 text-4xl md:text-5xl text-white lg:text-6xl tracking-wider ">
          WELCOME TO THE <br/>
          APOSTOLIC FAITH CHURCH
        </h1>
        <h2 className="text-2xl text-white lg:text-4xl tracking-wider">
            Sundays at 11:00 am & 5:00 pm
        </h2>

      </div>
        <div className="flex gap-8 2xs:justify-center xl:justify-start pt-5 items-center px-3">
          <Link href="/doctrines">
              <Button className="rounded-sm border-white bg-white/70 hover:text-white text-zinc-900" variant="default">About Us</Button>
          </Link>
          <Link href="https://www.youtube.com/@ApostolicFaithSacramento/streams">
              <Button className="rounded-sm border-white bg-white/70 hover:text-white text-zinc-900" size="default" variant="default">Latest Sermon</Button>
          </Link>

        </div>
      </div>
    </div>
    <div className="flex flex-col md:flex-row justify-center items-center gap-8 md:gap-20 bg-white px-6 md:px-16 py-12 md:py-15 -mt-8">
      <div className="w-full md:w-2xl">
        <h1 className="font-noto-sans text-3xl sm:text-4xl md:text-5xl font-light pb-5">Welcome!</h1>
          <HomepageParagraph />
        </div>
      <div className="w-full md:w-auto flex md:block justify-center">
        <Link href="/doctrines">
          <Button className="rounded-sm h-10 bg-[#7A5C10] hover:bg-[#5C450C]">Learn More</Button>
        </Link>
      </div>
    </div>
    </div>
  )
}
