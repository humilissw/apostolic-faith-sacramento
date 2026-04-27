import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { IoLocationOutline, IoMailOutline } from "react-icons/io5";

export default function Contact() {
  return (
    <div>
        <div className="flex justify-center items-center h-50 bg-[url('../public/choir-edit.jpg')] bg-cover bg-center md:h-100 lg:h-100">
            <h1 className="text-white text-5xl md:text-7xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                Contact
            </h1>
        </div>

        <div className="flex flex-col sm:flex-row justify-center px-10 py-15 sm:gap-15 sm:justify-center sm:py-30 sm:px-10">
            <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3113.280133482945!2d-121.46131482355433!3d38.71137695765789!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x809b2888f7a1ddb5%3A0x860cfaa4c9c406da!2sTrinity%20Apostolic%20Faith%20Church!5e0!3m2!1sen!2sus!4v1769206276874!5m2!1sen!2sus" 
                width="" 
                height=""
                loading="lazy"
                title="Apostolic Faith Church Location"
                className="h-auto w-auto md:w-100 md:h-100 lg:w-125"
                > 
            </iframe>

            <div className="flex flex-col gap-10 pt-10 font-noto-sans">
                <div>
                    <h1 className="text-2xl font-normal sm:text-3xl">Church Address</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        <Link className="hover:underline font-light sm:text-xl" href="https://www.google.com/maps/search/?api=1&query=7842%20Elmont%20Ave,%20Elverta,%20CA%2095626">
                            7842 Elmont Ave, Elverta, CA 95626
                        </Link>
                    </div>
                </div>
                <div>
                    <h1 className="text-2xl font-normal sm:text-3xl ">Mailing Address</h1>
                    <div className="flex flex-row items-center gap-2 pt-3">
                        <Link className="hover:underline font-light sm:text-xl" href="https://www.google.com/maps/search/?api=1&query=1635%20Wortell%20Drive,%20Lincoln,%20CA%2095648">
                            1635 Wortell Drive, Lincoln, CA 95648
                        </Link>
                    </div>
                </div>
                
                <div>
                    <h1 className="text-2xl font-normal sm:text-3xl">Emails</h1>
                    <div className="flex flex-col gap-2 pt-3">
                        <div className="sm:text-xl"> <b>Pastor: </b> <Link className="hover:underline font-light " href="mailto:pete@sferle.com">pete@sferle.com</Link> </div>
                        <div className="sm:text-xl"> <b>Media Team: </b><Link className="hover:underline font-light " href="mailto:info@afcsacramento.org">info@afcsacramento.org</Link> </div>
                    </div>
                </div>
            </div>

        </div>

    </div>
  )
}
