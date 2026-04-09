import {
  Button
} from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";

import HomepageParagraph from "@/components/homepage-paragraph"

export default function Home() {
  return (
    <div>
    <div className="w-full flex justify-start relative h-dvh pb-40 before:content-[''] before:absolute before:inset-0 before:bg-[url('../public/option2-copy.jpg')] before:bg-cover before:bg-center before:bg-fixed before:opacity-90 before:z-[-2] after:content-[''] after:absolute after:inset-0 after:bg-black/30 after:z-[-1]">
      <div className="font-noto-sans text-left text-shadow-lg/20 xs:pt-30 sm:pt-10 md:pt-20 lg:pt-50 pl-8 md:pl-16 lg:pl-24">
      <div className="space-y-4">
        <h1 className="text-4xl text-white md:text-5xl lg:text-6xl tracking-wider ">
          WELCOME TO 
        </h1>
        <h1 className="text-4xl md:text-5xl lg:text-6xl text-white tracking-wider ">
           APOSTOLIC FAITH
        </h1>
        <h1 className="text-4xl md:text-5xl lg:text-6xl text-white tracking-wider ">
           CHURCH
        </h1> 
        <h1 className="text-2xl text-white md:text-3xl lg:text-4xl tracking-wider">
           Sundays at 11:00 am & 5:00 pm
        </h1> 
      </div>
        <div className="flex gap-8 justify-start pt-5 items-center">
          <Link href="/doctrines">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" variant="default">About Us</Button>
          </Link>
          <Link href="https://www.youtube.com/@ApostolicFaithSacramento/streams">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" size="default" variant="default">Latest Sermon</Button>
          </Link>

        </div>
      </div>
    </div>
    <div className="text-center bg-white py-16">
      <div className="container flex justify-center px-4 text-center">
        <HomepageParagraph />
      </div>
    </div>
    </div>
  )
}