import {
  Button
} from "@/components/ui/button"
import Navbar from "@/components/Navbar";

export default function Home() {
  return (
    <div className="flex justify-center bg-[url('../public/frontChurchCopy1.JPG')] h-screen bg-cover bg-center bg-fixed">
      <div className="backdrop-opacity-50 text-shadow-sm text-shadow-zinc-900">
        <h1 className="text-6xl text-white tracking-wider text-center pt-60 pb-2 font-lora">
          Welcome to
        </h1>
        <h1 className="text-6xl text-white tracking-wide pb-4 font-lora">
           Apostolic Faith Church
        </h1> 
        <h1 className="text-4xl text-white text-center font-barlow">
           Sundays at 11:00 AM & 5:00 PM
        </h1> 
        <div className="flex gap-8 pt-5 justify-center items-center ">
          <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900 font-lora" variant="default">About Us</Button>
          <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900 font-lora" variant="default">Latest Sermon</Button>
        </div>
      </div>
    </div>
  )
}


//Apostolic Faith Church - <i>Sacramento, CA</i>