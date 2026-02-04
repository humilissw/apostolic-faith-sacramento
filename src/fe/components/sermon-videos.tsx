"use client";
import { useSearchParams } from "next/navigation";

export default function SermonVideos() {
  const searchParams = useSearchParams();

  const videoUri = searchParams.get("uri")?.toString();
  const sermonTitle = searchParams.get("sermonTitle")?.toString();
  const speaker = searchParams.get("speaker");
  const date = searchParams.get("date");

  return (
    <div className="flex flex-col bg-white h-screen font-noto-sans">
      <div className="flex flex-col py-15 justify-center items-center sm:hidden">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="250"
          height="auto"
        ></iframe>
      </div>

      <div className="xs:hidden md:hidden sm:flex sm:flex-col sm:justify-center sm:items-center sm:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="400"
          height="250"
        ></iframe>
      </div>

      <div className="xs:hidden lg:hidden md:flex md:flex-col md:justify-center md:items-center">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="600"
          height="400"
        ></iframe>
      </div>

      <div className="xs:hidden xl:hidden lg:flex lg:flex-col lg:justify-center lg:items-center lg:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="1000"
          height="600"
        ></iframe>
      </div>

      <div className="xs:hidden xl:flex xl:flex-col xl:justify-center xl:items-center xl:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="1250"
          height="700"
        ></iframe>
      </div>
    </div>
  );
}
