import SermonVideos from "@/components/sermon-videos";
import { Suspense } from "react";

export default function Sermon() {
  return (
    <Suspense>
      <SermonVideos />
    </Suspense>
  );
}
