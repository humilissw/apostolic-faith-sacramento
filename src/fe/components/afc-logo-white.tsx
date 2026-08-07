'use client'
import Image from 'next/image';
import Link from 'next/link';


export default function AFCLogoGrey(props: { width: number; height: number; }) {
    return (
        <Link href="/" className="shrink-0">
            <Image
            src='/logo-grey.jpg'
            alt="Apostolic Faith Church Logo"
            width={props.width}
            height={props.height}/>
        </Link>
    )}
