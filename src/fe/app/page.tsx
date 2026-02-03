import {
  Button
} from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="w-full flex justify-center bg-[url('../public/frontChurchCopy1.JPG')] h-screen bg-cover bg-center bg-fixed">
      <div className="font-noto-sans text-center text-shadow-lg/20 xs:pt-40 sm:pt-20 md:pt-60">
      <div /*className="bg-zinc-900/60 p-7 rounded-lg"*/>
        <h1 className="text-4xl text-white md:text-5xl lg:text-6xl md:pb-2 tracking-wider ">
          WELCOME TO 
        </h1>
        <h1 className="text-4xl md:text-5xl md:pb-4 lg:text-6xl text-white tracking-wider ">
           APOSTOLIC FAITH CHURCH
        </h1> 
        <h1 className="text-2xl pt-3 text-white md:text-3xl lg:text-4xl tracking-wider">
           Sundays at 11:00 am & 5:00 pm
        </h1> 
      </div>
        <div className="flex gap-8 justify-center pt-5 items-center">
          <Link href="/doctrines">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" variant="default">About Us</Button>
          </Link>
          <Link href="https://www.youtube.com/@ApostolicFaithSacramento/streams">
              <Button className=" border-white bg-white/70 hover:text-white text-zinc-900" size="default" variant="default">Latest Sermon</Button>
          </Link>
          
        </div>
      </div>
    </div>
  )
}

