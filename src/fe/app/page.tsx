import {
  Button
} from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex justify-center bg-[url('../public/frontChurchCopy1.JPG')] h-screen bg-cover bg-center bg-fixed">
      <div className=" text-shadow-sm font-noto-sans text-shadow-zinc-900">
        <h1 className="text-6xl font-medium text-white tracking-wider text-center pt-60 pb-2">
          WELCOME TO 
        </h1>
        <h1 className="text-6xl font-medium text-white tracking-wider pb-4">
           APOSTOLIC FAITH CHURCH
        </h1> 
        <h1 className="text-4xl text-white text-center">
           Sundays at 11:00 AM & 5:00 PM
        </h1> 
        <div className="flex gap-8 pt-5 justify-center items-center ">
          <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900" variant="default">About Us</Button>
          <Button className="border-2 border-white bg-transparent text-shadow-md text-shadow-zinc-900" variant="default">Latest Sermon</Button>
        </div>
      </div>
    </div>
  )
}


//Apostolic Faith Church - <i>Sacramento, CA</i>