'use client'
import Image from 'next/image';
import Link from 'next/link';


export default function AFCLogoWhite(props: { width: number; height: number; }) {
    return (
        <Link href="/" className="shrink-0">
            <Image
            src='/logo-white.jpg'
            alt="Apostolic Faith Church Logo"
            width={props.width}
            height={props.height}/>
        </Link>
    )}
