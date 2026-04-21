import {
  Button
} from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";

import HomepageParagraph from "@/components/homepage-paragraph"

export default function Home() {
  return (
    <div className="">
    <div className="w-full flex justify-center xl:justify-start relative min-h-[100dvh] pb-20 sm:pb-32 md:pb-40 before:content-[''] before:absolute before:inset-0 before:bg-[url('../public/option2-copy.jpg')] before:bg-cover before:bg-center before:bg-fixed before:opacity-90 before:z-[-2] after:content-[''] after:absolute after:inset-0 after:bg-black/48 after:z-[-1]">
      <div className="font-noto-sans xs:text-center xl:text-left text-shadow-lg/20 pb-16 xs:pt-20 lg:pt-56 lg:pl-24">
      <div className="font-light px-3">
        <h1 className="leading-none pb-4 text-4xl md:text-5xl text-white lg:text-6xl tracking-wider ">
          WELCOME TO THE
        </h1>
        <h1 className="leading-none pb-4 text-4xl md:text-5xl lg:text-6xl text-white tracking-wider ">
           APOSTOLIC FAITH CHURCH
        </h1>
        <h2 className="text-2xl text-white lg:text-4xl tracking-wider">
           Sundays at 11:00 am & 5:00 pm
        </h2> 
        
      </div>
        <div className="flex gap-8 xs:justify-center xl:justify-start pt-5 items-center px-3">
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
        <Button className="rounded-sm h-10 bg-[#7A5C10] hover:bg-[#5C450C]">Learn More</Button>
      </div>
    </div>
    </div>
  )
}