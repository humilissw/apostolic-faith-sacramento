'use client'
import Link from "next/link";
import Image from 'next/image';


export default function HomepageImage(props: { width: number; height: number; }) {
    return (
        <a href="/">
            <Image 
            src='/logo.png' 
            alt="Apostolic Faith Church Logo" 
            width={props.width}
            height={props.height}/>
        </a>
    )}