'use client'
import Image from 'next/image';
import Link from 'next/link';


export default function AFCLogo(props: { width: number; height: number; }) {
    return (
        <Link href="/" className="shrink-0">
            <Image
            src='/logo.png'
            alt="Apostolic Faith Church Logo"
            width={props.width}
            height={props.height}/>
        </Link>
    )}
