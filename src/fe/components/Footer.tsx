'use client';

import AFCLogo from "@/components/AFCLogo";
import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { FaFacebookSquare, FaRegCopyright } from "react-icons/fa";
import { IoLocationOutline, IoLogoYoutube, IoMailOutline } from "react-icons/io5";







export default function Footer() {
    return (
      <footer className="flex flex-col md:items-center md:justify-center md:px-10 bg-zinc-700 text-white md:sticky md:top-[100vh] lg:bottom-0 lg:w-full md:t-20 md:py-5 ">
                
                
                    <div className="flex flex-col gap-10 pt-7 pl-5 md:border-b pb-10 md:flex-row md:gap-25 ">
                        <div className="hidden md:flex">
                            <AFCLogo width={175} height={175}/>
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
                                    <IoMailOutline size="15"/>
                                    <Link className="hover:underline" href="/">
                                        exampleemail@info.com
                                    </Link>
                                </div>

                            </ul>
            
                            <ul className="flex flex-col gap-4 static bold">
                                
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
                   
                    <div className="items-center justify-center pt-10 pb-10 bg-zinc-800 md:bg-zinc-700 md:bottom-0 md:w-full md:flex md:gap-100">
                            <div className="flex flex-row items-center justify-center gap-3 mb-5">
                                <FaRegCopyright size="15"/>
                                <p>2025 Apostolic Faith Church</p>
                            </div>
                            <div className="flex flex-row items-center justify-center gap-5 md:gap-5 md:mb-10">
                                <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/"> <FaFacebookSquare size="25"/> </Link>
                                <Link href="https://www.youtube.com/@ApostolicFaithSacramento"> <IoLogoYoutube size="25"/> </Link>
                            </div>
                        </div>
        </footer>
    )
}<FaFacebookSquare size="25"/>