"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface FlyerImageProps {
  src: string;
  alt: string;
  /** Tailwind classes for the thumbnail <img>. */
  className?: string;
  /** Optional title shown in the full-size dialog header. */
  title?: string;
  /**
   * Override the click behaviour (e.g. to also stop a wrapping <Link> from
   * navigating). Receives the open-full-size callback so custom handlers can
   * still show the dialog.
   */
  onImageClick?: (openFullSize: () => void) => (event: React.MouseEvent) => void;
}

// Flyer images are served by the backend API via the BFF, not a static host,
// so use a plain img rather than next/image. Clicking opens the flyer at
// full size in a dialog.
export function FlyerImage({ src, alt, className, title, onImageClick }: FlyerImageProps) {
  const [open, setOpen] = useState(false);
  const openFullSize = () => setOpen(true);
  const handleClick = onImageClick
    ? onImageClick(openFullSize)
    : () => openFullSize();

  return (
    <>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={alt}
        onClick={handleClick}
        className={`${className ?? ""} cursor-zoom-in`}
      />
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{title ?? alt}</DialogTitle>
          </DialogHeader>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={src} alt={alt} className="w-full h-auto rounded-md" />
        </DialogContent>
      </Dialog>
    </>
  );
}
