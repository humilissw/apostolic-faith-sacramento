"use client";

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

interface AnimatedSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  side?: "left" | "right";
  className?: string;
  children: React.ReactNode;
  title?: string;
  triggerContent?: React.ReactNode;
}

export function AnimatedSheet({ open, onOpenChange, side = "right", className, children, title, triggerContent }: AnimatedSheetProps) {
  const animClass = open ? "sheet-animate-open" : "sheet-animate-close";
  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        {triggerContent && <SheetTrigger asChild>{triggerContent}</SheetTrigger>}
        <SheetContent side={side} className={cn("w-full max-w-lg overflow-y-auto", animClass, className)}>
          {title && (
            <SheetHeader>
              <SheetTitle>{title}</SheetTitle>
            </SheetHeader>
          )}
          {children}
        </SheetContent>
      </Sheet>
    </>
  );
}
