'use client';

import AFCLogo from "@/components/afc-logo";
import Link from "next/link";
import { BsTelephone } from "react-icons/bs";
import { FaFacebookSquare, FaInstagramSquare, FaRegCopyright } from "react-icons/fa";
import { IoLocationOutline, IoLogoYoutube, IoMailOutline } from "react-icons/io5";
import { RiInstagramFill } from "react-icons/ri";


export default function Footer() {
    return (
      <footer className="flex flex-col md:items-center md:justify-center bg-zinc-700 text-white mt-auto">

            <div className="flex flex-col gap-10 pt-7 pl-5 pb-10 md:flex-row md:gap-20 ">
                <div className="hidden md:flex md:flex-col">
                    <AFCLogo width={175} height={175}/>
                    <div className="flex flex-row items-center justify-center gap-5 md:gap-5">
                        <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/" aria-label="Go to Apostolic Faith Church - Sacramento Facebook Page" target="_blank" rel="noopener noreferrer"> <FaFacebookSquare size="25"/> </Link>
                        <Link href="https://www.youtube.com/@ApostolicFaithSacramento" aria-label="Go to Apostolic Faith Church - Sacramento YouTube Channel" target="_blank" rel="noopener noreferrer"> <IoLogoYoutube size="25"/> </Link>
                        <Link href="https://www.instagram.com/p/DWfxFHDlRfO/" aria-label="Go to Apostolic Faith Church - Sacramento Instagram Page" target="_blank" rel="noopener noreferrer"> <RiInstagramFill size="25"/> </Link>
                    </div>
                </div>

                <ul className="flex flex-col gap-4 static bold">
                    <h1 className="font-bold text-[17px]"> Contact Us </h1>
                    <div className="flex flex-row items-center gap-2">
                        <IoLocationOutline size="15"/>
                        <Link className="hover:underline" href="https://www.google.com/maps/search/?api=1&query=7842%20Elmont%20Ave,%20Elverta,%20CA%2095626">
                            7842 Elmont Ave, Elverta, CA 95626
                        </Link>
                    </div>

                    <div className="flex flex-row items-center gap-2">
                        <div className="pt-1">
                            <IoMailOutline size="15"/>
                        </div>
                        <Link className="hover:underline" href="mailto:info@afcsacramento.org">
                            info@afcsacramento.org
                        </Link>
                    </div>
                </ul>

                <ul className="flex flex-col gap-4 static bold md:pr-5">

                    <h1 className="font-bold text-[17px]">Quick Links</h1>

                    <Link className="hover:underline" href="/doctrines">
                        About
                    </Link>

                    <Link className="hover:underline"href="/media">
                        Media
                    </Link>

                    <Link className="hover:underline" href="/contact">
                        Contact
                    </Link>
                </ul>
            </div>

            <div className="flex flex-row items-center pl-5 gap-5 pb-5 md:hidden">
                <Link href="https://www.facebook.com/p/Sacramento-AFC-100064440229528/" aria-label="Go to Apostolic Faith Church - Sacramento Facebook Page" target="_blank" rel="noopener noreferrer">
                    <FaFacebookSquare aria-hidden="true"size="25"/>

                </Link>
                <Link href="https://www.youtube.com/@ApostolicFaithSacramento" aria-label="Go to Apostolic Faith Church - Sacramento YouTube Channel" target="_blank" rel="noopener noreferrer">
                    <IoLogoYoutube aria-hidden="true" size="25"/>
                </Link>
                <Link href="https://www.instagram.com/p/DWfxFHDlRfO/" aria-label="Go to Apostolic Faith Church - Sacramento Instagram Page" target="_blank" rel="noopener noreferrer">
                    <RiInstagramFill aria-hidden="true" size="25"/>
                </Link>
            </div>

            <div className="items-center justify-center pt-3 pb-4 bg-zinc-800 md:bottom-0 md:w-full md:flex md:gap-100">
                <div className="flex flex-row items-center justify-center gap-3">
                    <FaRegCopyright size="15"/>
                    <p>{new Date().getFullYear()} Apostolic Faith Church</p>
                </div>
            </div>
        </footer>
    )
}
