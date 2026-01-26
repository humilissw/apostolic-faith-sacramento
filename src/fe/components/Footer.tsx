'use client';

import AFCLogo from "@/components/AFCLogo";
import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { FaFacebookSquare, FaRegCopyright } from "react-icons/fa";
import { IoLocationOutline, IoLogoYoutube, IoMailOutline } from "react-icons/io5";

export default function Footer() {
    return (
      <footer className="flex flex-col md:items-center md:justify-center bg-zinc-700 text-white md:sticky md:top-[100vh] lg:bottom-0 lg:w-full md:t-20">
                    <div className="flex flex-col gap-10 pt-7 pl-5 pb-10 md:flex-row md:gap-20 ">
                        <div className="hidden md:flex md:flex-col">
                            <AFCLogo width={175} height={175}/>
                            <div className="flex flex-row items-center justify-center gap-5 md:gap-5">
                                <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/"> <FaFacebookSquare size="25"/> </Link>
                                <Link href="https://www.youtube.com/@ApostolicFaithSacramento"> <IoLogoYoutube size="25"/> </Link>
                            </div>
                        </div>
                        

                            <ul className="flex flex-col gap-4 static bold">
                                <h1 className="font-bold text-[17px]"> Contact Us </h1>
                                <div className="flex flex-row items-center gap-2">
                                    <IoLocationOutline size="15"/>
                                    <Link className="hover:underline" href="/">
                                        7842 Elmont Ave, Elverta, CA 95626
                                    </Link>
                                </div>

                                <div className="flex flex-row items-center gap-2">
                                    <BsTelephone size="15"/>
                                    <Link className="hover:underline" href="/">
                                        123-456-7890
                                    </Link>
                                </div>

                                <div className="flex flex-row items-center gap-2">
                                    <div className="pt-1">
                                        <IoMailOutline size="15"/>
                                    </div>
                                    <Link className="hover:underline" href="/">
                                        exampleemail@info.com
                                    </Link>
                                </div>

                            </ul>
            
                            <ul className="flex flex-col gap-4 static bold md:pr-5">
                                
                                <h1 className="font-bold text-[17px]">Quick Links</h1>

                                <Link className="hover:underline" href="/about">
                                    About 
                                </Link>

                                <Link className="hover:underline"href="/media">
                                    Media
                                </Link>

                                <Link className="hover:underline" href="/events">
                                    Events
                                </Link>

                                <Link className="hover:underline" href="/contact">
                                    Contact
                                </Link>

                                <Link className="hover:underline" href="/give">
                                    Give
                                </Link>
                            </ul>
                    </div>

                    <div className="flex flex-row items-center pl-5 gap-5 pb-5 md:hidden">
                        <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/"> <FaFacebookSquare size="25"/> </Link>
                        <Link href="https://www.youtube.com/@ApostolicFaithSacramento"> <IoLogoYoutube size="25"/> </Link>
                    </div>
                   
                    <div className="items-center justify-center pt-3 pb-4 bg-zinc-800 md:bottom-0 md:w-full md:flex md:gap-100">
                            <div className="flex flex-row items-center justify-center gap-3">
                                <FaRegCopyright size="15"/>
                                <p>2025 Apostolic Faith Church</p>
                            </div>
                            
                        </div>
        </footer>
    )
}