import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";

export default function Contact() {
  return (
    <div >
        <div className="flex justify-center items-center h-40 bg-position-[center_top_31rem] bg-[url('../public/choir-edit.jpg')] bg-cover md:h-35 md:bg-position-[center_top_19rem] lg:bg-position-[center_top_80rem] lg:h-75">
            <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Contact
            </h1>
        </div>
    
        <div className="flex gap-10 justify-center py-20">
            <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3113.280133482945!2d-121.46131482355433!3d38.71137695765789!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x809b2888f7a1ddb5%3A0x860cfaa4c9c406da!2sTrinity%20Apostolic%20Faith%20Church!5e0!3m2!1sen!2sus!4v1769206276874!5m2!1sen!2sus" 
                width="100" 
                height="75"
                loading="lazy"
                title="Apostolic Faith Church Location"
                > 
            </iframe>


            <div className="flex flex-col gap-10 font-noto-sans">
                <div>
                    <h1>Address</h1>
                    <div className="flex flex-row items-center gap-2">
                        <IoLocationOutline size="15"/>
                        <Link className="hover:underline" href="/">
                            7842 Elmont Ave, Elverta, CA 95626
                        </Link>
                    </div>
                </div>

                <div>
                    <h1>Phone Number</h1>
                    <div className="flex flex-row items-center gap-2">
                        <BsTelephone size="15"/>
                        <Link className="hover:underline" href="/">
                            123-456-7890
                        </Link>
                    </div>
                </div>
                
                <div>
                    <h1>Pastor Email</h1>
                    <div className="flex flex-row items-center gap-2">
                        <div className="pt-1">
                            <IoMailOutline size="15"/>
                        </div>
                        <Link className="hover:underline" href="/">
                            exampleemail@info.com
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}
