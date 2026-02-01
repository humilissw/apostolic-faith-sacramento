'use client'

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';


export default function Sermon() { 
    const searchParams = useSearchParams();

    const videoUri = searchParams.get("uri")
    const sermonTitle = searchParams.get("sermonTitle")
    const speaker = searchParams.get("speaker")
    const date = searchParams.get("date")

  return (
    <div className=''>
      <div className="flex flex-col justify-center bg-white">
    

    <div className='flex flex-col justify-center items-center py-15'>
        <iframe 
            src={videoUri}
            allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" 
            title="The Wise Men — Bro. Sorin Filimon • Matthew 2:1-12">
        </iframe>
        <h1>{sermonTitle}</h1>
        <h1>{speaker}</h1>
    </div>
      </div>
    </div>
  )
}