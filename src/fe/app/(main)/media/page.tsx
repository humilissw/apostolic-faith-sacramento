'use client'

import Link from 'next/link';
import { useState, useEffect } from 'react';
import Image from 'next/image'

interface sermonData {
  videoUri: string;
  sermonTitle: string;
  speaker: string;
  createDate: string;
}


export default function Media() {    

  const [videoData, setVideoData] = useState([]);
  const fetchData = async () => {
    try {
      const response = await fetch('/data.json');
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const result = await response.json();
      setVideoData(result);
    } catch (error) {
      if (error instanceof Error) {
        console.error(error.message);
      }
    }
}

  useEffect(() => {
    fetchData();
  }, [])


  return (
    <div className=''>
      <div className="flex flex-col justify-center bg-white">
          <div className="flex justify-center items-center h-50 bg-[url('../public/media.jpg')] bg-cover bg-center md:h-100 lg:h-100">
              <h1 className="text-white text-5xl md:text-6xl lg:text-8xl text-shadow-lg font-noto-sans p-3 rounded-xl">
                  Media
              </h1>
          </div>
        <div className='flex justify-center pt-20'>
          <h1 className='text-4xl md:text-6xl text-center tracking-wider'>Latest Services</h1>
        </div>
        <div className='flex justify-center pt-15'>
            {videoData.map((data: sermonData, index) => 
            <div key={index}>
              {index == 0 ?
              <Link 
                key={index} 
                href={data.videoUri}
            >
              <div className='rounded-xl shadow-xl/20'>
              <div className='flex xs:h-100 xs:w-60 md:h-75 md:w-150 lg:h-100 lg:w-200'>
                <div className='flex flex-col md:flex-row items-center'>
                    <Image
                      src="/sacAFC.jpg"
                      width={500}
                      height={500}
                      alt="Picture of the Apostolic Faith Church"
                      className='xs:h-50 md:h-75 xs:rounded-t-xl md:rounded-l-xl 2xl:h-100'
                    />
                      <div className='flex flex-col px-5 pt-3 w-full font-medium font-noto-sans'>
                        <h1 className='xs:text-xl md:text-4xl'>{data.sermonTitle}</h1>
                        <h1 className='text-black/40 font-normal'>{data.speaker}</h1>  
                        <h1 className='text-black/40 font-normal'>{new Date(data.createDate).toLocaleDateString('en-US')}</h1>
                      </div>

                </div>
              </div>
              </div>
              </Link> : <></>
            }
            </div>
            )}
        </div>

        <div className='flex flex-wrap gap-x-5 gap-y-5 justify-center py-15 sm:px-10 md:px-20 lg:px-40 xl:px-80'>
          {videoData.map((data: sermonData, index) => 
          <Link 
            key={index} 
            href={data.videoUri}
            >
            {index > 0 ?
          <div className='rounded-xl shadow-xl/10'>
          <div className='flex xs:h-100 xs:w-60 md:h-60 md:w-140'>
            <div className='flex flex-col md:flex-row items-center'>
                <Image
                  src="/sacAFC.jpg"
                  width={300}
                  height={300}
                  alt="Picture of the Apostolic Faith Church"
                  className='h-50 md:h-60 rounded-t-xl md:rounded-l-xl '
                />
                  <div className='flex flex-col px-5 pt-3 w-full font-medium font-noto-sans'>
                    <h1 className='text-xl'>{data.sermonTitle}</h1>
                    <h1 className='text-black/40 font-normal'>{data.speaker}</h1>  
                    <h1 className='text-black/40 font-normal'>{new Date(data.createDate).toLocaleDateString('en-US')}</h1>
                  </div>
                
            </div>
          </div>
          </div> : <></>
          }
          </Link> 
          
          )}
        </div>


      </div>
    </div>
  )
}