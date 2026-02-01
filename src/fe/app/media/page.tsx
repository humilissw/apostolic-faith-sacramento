'use client'

import Link from 'next/link';
import { useState, useEffect } from 'react';
import Image from 'next/image'




export default function Media() {    

  const [videoData, setVideoData] = useState([]);

  const fetchData = async () => {
    try {
      const response = await fetch('data.json');
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const result = await response.json();
      setVideoData(result);
    } catch (error) {
      console.error(error.message);
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

        <div className='flex justify-center pt-15'>
            {videoData.map((data, index) => 
            <div key={index}>
              {index == 0 ?
              <Link key={index} href="/sermon">
                <h1>Latest Service</h1>
              <div className='rounded-xl shadow-xl/20'>
              <div className='flex justify-center h-100 w-200'>
                <div className='flex flex-col items-center w-75'>
                    <Image
                      src="/sacAFC.jpg"
                      width={500}
                      height={500}
                      alt="Picture of the author"
                      className='rounded-t-xl '
                    />
                      <div className='flex flex-col px-5 pt-3 w-full font-medium font-noto-sans'>
                        <h1 className='text-xl'>{data.sermonTitle}</h1>
                        <h1 className='text-xl'>{data.speaker}</h1>  
                        <h1 className='text-black/40 font-normal'>Date</h1>
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
          {videoData.map((data, index) => 
          <Link 
            key={index} 
            href={{
              pathname: '/sermon',
              query: { 
                uri: data.videoUri,
                sermonTitle: data.sermonTitle,
                speaker: data.speaker,
                date: data.createDate 
                
              },
            }}
            >
            {index > 0 ?
          <div className='rounded-xl shadow-xl/20'>
          <div className='flex justify-center h-90 w-70'>
            <div className='flex flex-col items-center w-75'>
                <Image
                  src="/sacAFC.jpg"
                  width={500}
                  height={500}
                  alt="Picture of the author"
                  className='rounded-t-xl '
                />
                  <div className='flex flex-col px-5 pt-3 w-full font-medium font-noto-sans'>
                    <h1 className='text-xl'>{data.sermonTitle}</h1>
                    <h1 className='text-xl'>{data.speaker}</h1>  
                    <h1 className='text-black/40 font-normal'>Date</h1>
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