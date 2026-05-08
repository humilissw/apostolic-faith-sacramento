"use client";
import { useSearchParams } from "next/navigation";

// Only allow known safe video providers
const ALLOWED_HOSTS = new Set([
  "www.youtube.com",
  "youtube.com",
  "www.youtu.be",
  "youtu.be",
  "player.vimeo.com",
  "vimeo.com",
]);

function validateVideoUri(uri: string): string | null {
  // Reject non-http(s) schemes
  if (!uri.startsWith("http://") && !uri.startsWith("https://")) return null;

  let url: URL;
  try {
    url = new URL(uri);
  } catch {
    return null;
  }

  // Reject javascript: and data: URIs
  if (url.protocol === "javascript:" || url.protocol === "data:") return null;

  // Whitelist allowed hosts
  if (!ALLOWED_HOSTS.has(url.hostname)) return null;

  return url.toString();
}

export default function SermonVideos() {
  const searchParams = useSearchParams();

  const rawUri = searchParams.get("uri")?.toString();
  const videoUri = rawUri ? validateVideoUri(rawUri) : null;
  const sermonTitle = searchParams.get("sermonTitle")?.toString();
  const speaker = searchParams.get("speaker");
  const date = searchParams.get("date");

  // Don't render iframe if URI is invalid or missing
  if (!videoUri) {
    return null;
  }

  return (
    <div className="flex flex-col bg-white h-screen font-noto-sans">
      <div className="flex flex-col py-15 justify-center items-center sm:hidden">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="250"
          height="auto"
          sandbox="allow-scripts allow-same-origin allow-popups allow-formats"
        ></iframe>
      </div>

      <div className="xs:hidden md:hidden sm:flex sm:flex-col sm:justify-center sm:items-center sm:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="400"
          height="250"
          sandbox="allow-scripts allow-same-origin allow-popups allow-formats"
        ></iframe>
      </div>

      <div className="xs:hidden lg:hidden md:flex md:flex-col md:justify-center md:items-center">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="600"
          height="400"
          sandbox="allow-scripts allow-same-origin allow-popups allow-formats"
        ></iframe>
      </div>

      <div className="xs:hidden xl:hidden lg:flex lg:flex-col lg:justify-center lg:items-center lg:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="1000"
          height="600"
          sandbox="allow-scripts allow-same-origin allow-popups allow-formats"
        ></iframe>
      </div>

      <div className="xs:hidden xl:flex xl:flex-col xl:justify-center xl:items-center xl:py-15">
        <iframe
          src={videoUri}
          allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share"
          title={sermonTitle}
          width="1250"
          height="700"
          sandbox="allow-scripts allow-same-origin allow-popups allow-formats"
        ></iframe>
      </div>
    </div>
  );
}
