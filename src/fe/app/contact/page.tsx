import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";

export default function Contact() {
  return (
    <div>
        <div className="flex justify-center items-center h-50 bg-position-[center_top_31rem] bg-[url('../public/choir-edit.jpg')] bg-cover md:h-100 md:bg-position-[center_top_25rem] lg:bg-position-[center_top_34rem] xl:bg-position-[center_top_38rem] 2xl:bg-position-[center_top_52rem] lg:h-75">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Contact
            </h1>
        </div>
    

        <div className="flex flex-col justify-center px-10 py-15 sm:hidden">
            <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3113.280133482945!2d-121.46131482355433!3d38.71137695765789!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x809b2888f7a1ddb5%3A0x860cfaa4c9c406da!2sTrinity%20Apostolic%20Faith%20Church!5e0!3m2!1sen!2sus!4v1769206276874!5m2!1sen!2sus" 
                width="" 
                height=""
                loading="lazy"
                title="Apostolic Faith Church Location"
                className="h-auto w-auto"
                > 
            </iframe>

            <div className="flex flex-col gap-10 pt-10 font-noto-sans">
                <div>
                    <h1 className="text-2xl font-normal ">Address</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        
                        <Link className="hover:underline font-light" href="/">
                            7842 Elmont Ave, Elverta, CA 95626
                        </Link>
                    </div>
                </div>

                <div>
                    <h1 className="text-2xl font-normal ">Phone Number</h1>
                    <div className="flex flex-row items-center pt-3">
                        
                        <Link className="hover:underline font-light" href="/">
                            123-456-7890
                        </Link>
                    </div>
                </div>
                
                <div>
                    <h1 className="text-2xl font-normal ">Email</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        <Link className="hover:underline font-light" href="/">
                            info@afcsacramento.org
                        </Link>
                    </div>
                </div>
            </div>

        </div>


        <div className="xs:hidden sm:flex sm:gap-15 sm:justify-center sm:py-30 sm:px-10">
            <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3113.280133482945!2d-121.46131482355433!3d38.71137695765789!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x809b2888f7a1ddb5%3A0x860cfaa4c9c406da!2sTrinity%20Apostolic%20Faith%20Church!5e0!3m2!1sen!2sus!4v1769206276874!5m2!1sen!2sus" 
                width="" 
                height=""
                loading="lazy"
                title="Apostolic Faith Church Location"
                className="md:w-100 md:h-100 lg:w-125"
                > 
            </iframe>


            <div className="flex flex-col gap-10 font-noto-sans">
                <div>
                    <h1 className="text-3xl font-normal ">Address</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        <Link className="hover:underline text-xl font-light" href="/">
                            7842 Elmont Ave, Elverta, CA 95626
                        </Link>
                    </div>
                </div>

                <div>
                    <h1 className="text-3xl font-normal ">Phone Number</h1>
                    <div className="flex flex-row items-center pt-3">
                        
                        <Link className="hover:underline text-xl font-light" href="/">
                            123-456-7890
                        </Link>
                    </div>
                </div>
                
                <div>
                    <h1 className="text-3xl font-normal  ">Email</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        <Link className="hover:underline text-xl font-light" href="/">
                            info@afcsacramento.org
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    </div>
  )
}
