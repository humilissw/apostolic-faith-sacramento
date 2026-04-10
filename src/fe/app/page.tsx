import {
  Button
} from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";

import HomepageParagraph from "@/components/homepage-paragraph"

export default function Home() {
  return (
    <div className="">
    <div className="w-full flex justify-start relative min-h-screen pb-20 sm:pb-32 md:pb-40 before:content-[''] before:absolute before:inset-0 before:bg-[url('../public/option2-copy.jpg')] before:bg-cover before:bg-center before:bg-fixed before:opacity-90 before:z-[-2] after:content-[''] after:absolute after:inset-0 after:bg-black/40 after:z-[-1]">
      <div className="font-noto-sans xs:text-center lg:text-left text-shadow-lg/20 pb-16 pt-32 sm:pt-40 md:pt-48 lg:pt-56 pl-5 pr-5 sm:pl-10 md:pl-16 lg:pl-24">
      <div className="space-y-4 font-light">
        <h1 className="text-4xl text-white md:text-5xl lg:text-6xl tracking-wider ">
          WELCOME TO 
        </h1>
        <h1 className="text-4xl md:text-5xl lg:text-6xl text-white tracking-wider ">
           APOSTOLIC FAITH CHURCH
        </h1>
        <h1 className="text-2xl text-white md:text-3xl lg:text-4xl tracking-wider">
           Sundays at 11:00 am & 5:00 pm
        </h1> 
        
      </div>
        <div className="flex gap-8 xs:justify-center lg:justify-start pt-5 items-center">
          <Link href="/doctrines">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" variant="default">About Us</Button>
          </Link>
          <Link href="https://www.youtube.com/@ApostolicFaithSacramento/streams">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" size="default" variant="default">Latest Sermon</Button>
          </Link>

        </div>
      </div>
    </div>
    <div className="flex flex-col md:flex-row justify-center items-center gap-8 md:gap-20 bg-white px-6 md:px-16 py-12 md:py-15 rounded-t-2xl -mt-8">
      <div className="w-full md:w-2xl">
        <p className="font-noto-sans text-3xl sm:text-4xl md:text-5xl font-light pb-5">Welcome!</p>
        <HomepageParagraph />
      </div>
      <div className="w-full md:w-auto flex md:block justify-center">
        <Button className="bg-[#AA830E]">Learn More</Button>
      </div>
    </div>
    </div>
  )
}