import {
  Button
} from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="w-full flex justify-center pt-35 bg-[url('../public/frontChurchCopy1.JPG')] h-screen bg-cover bg-center bg-fixed">
      <div className="text-shadow-sm font-noto-sans text-shadow-zinc-900 ">
        <h1 className="text-4xl text-white md:text-5xl md:font-medium lg:text-6xl lg:pt-40 md:pb-2 tracking-wider text-center ">
          WELCOME TO 
        </h1>
        <h1 className="text-4xl md:text-5xl md:font-medium md:pb-4 lg:text-6xl text-white tracking-wider text-center">
           APOSTOLIC FAITH CHURCH
        </h1> 
        <h1 className="text-2xl pt-3 text-white text-center md:text-3xl lg:text-4xl">
           Sundays at 11:00 AM & 5:00 PM
        </h1> 
        <div className="flex gap-8 pt-5 justify-center items-center ">
          <Link href="/doctrines">
              <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900" variant="default">About Us</Button>
          </Link>
          <Link href="https://www.youtube.com/@ApostolicFaithSacramento/streams">
              <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900" variant="default">Latest Sermon</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}


//Apostolic Faith Church - <i>Sacramento, CA</i>