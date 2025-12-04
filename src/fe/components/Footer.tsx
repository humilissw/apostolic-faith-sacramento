'use client';

import Link from "next/link";
import Image from 'next/image';
import HomepageImage from '@/components/ChurchLogo'
import { FaRegCopyright } from "react-icons/fa";
import { IoLocationOutline } from "react-icons/io5";
import { IoLocationSharp } from "react-icons/io5";
import { FaFacebookSquare } from "react-icons/fa";
import { FaYoutube } from "react-icons/fa";
import { TbBrandYoutubeFilled } from "react-icons/tb";
import { IoLogoYoutube } from "react-icons/io5";
import { BsTelephone } from "react-icons/bs";
import { IoMailOutline } from "react-icons/io5";
import Home from "@/app/page";







export default function Footer() {
    return (
      <footer className="sticky top-[100vh] bottom-0 w-full flex gap-40 items-center justify-center pt-20 py-5 bg-zinc-700 text-white">
                
                <div>
                    <div className="flex gap-45 pb-10 border-b">
                        <div className="flex">
                            <HomepageImage width={175} height={175}/>
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
                   

                    <div className="bottom-0 w-full flex gap-150 items-center justify-center pt-10">
                        <div className="flex flex-row items-center justify-center gap-3 mb-10">
                            <FaRegCopyright size="15"/>
                            <p>2025 Apostolic Faith Church</p>
                        </div>
                        <div className="flex flex-row gap-5 items-center justify-center mb-10">
                            <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/"> <FaFacebookSquare size="25"/> </Link>
                            <Link href="https://www.youtube.com/@ApostolicFaithSacramento"> <IoLogoYoutube size="25"/> </Link>
                        </div>
                    </div>
                </div>
        </footer>
    )
}<FaFacebookSquare size="25"/>