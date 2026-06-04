"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Check, ChevronDown, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface TypeaheadOption {
  id: string;
  label: string;
  subtitle?: string;
}

interface TypeaheadSelectProps<T extends TypeaheadOption> {
  options: T[];
  value: T | null;
  onChange: (value: T | null) => void;
  label?: string;
  placeholder?: string;
  searchPlaceholder?: string;
  searchFn: (option: T, query: string) => boolean;
  renderOption: (option: T) => React.ReactNode;
  renderValue: (option: T) => React.ReactNode;
  className?: string;
  disabled?: boolean;
}

export function TypeaheadSelect<T extends TypeaheadOption>({
  options,
  value,
  onChange,
  label,
  placeholder = "Search...",
  searchPlaceholder = "Search...",
  searchFn,
  renderOption,
  renderValue,
  className,
  disabled = false,
}: TypeaheadSelectProps<T>) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = query
    ? options.filter((o) => searchFn(o, query))
    : options;

  const handleClick = useCallback(() => {
    if (disabled) return;
    setOpen((v) => !v);
    if (!open) {
      setQuery("");
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [disabled, open]);

  const handleSelect = useCallback(
    (option: T) => {
      onChange(option);
      setOpen(false);
      setQuery("");
    },
    [onChange],
  );

  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onChange(null);
      setQuery("");
    },
    [onChange],
  );

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
        setQuery("");
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={wrapperRef} className={cn("relative", className)}>
      {label && (
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          {label}
        </label>
      )}

      <div
        className={cn(
          "flex items-center gap-2 border rounded-md px-3 py-2 cursor-pointer min-h-10 bg-background",
          "hover:border-input transition-colors",
          open && "border-ring ring-1 ring-ring/20",
          disabled && "opacity-50 cursor-not-allowed",
        )}
        onClick={handleClick}
      >
        {value ? (
          <>
            <div className="flex-1 truncate">{renderValue(value)}</div>
            <button
              type="button"
              onClick={handleClear}
              className="shrink-0 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </>
        ) : (
          <>
            <Search className="h-4 w-4 text-muted-foreground shrink-0" />
            <span className="text-muted-foreground">{placeholder}</span>
          </>
        )}
        <ChevronDown className={cn("h-4 w-4 text-muted-foreground shrink-0 transition-transform", open && "rotate-180")} />
      </div>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-popover border rounded-md shadow-lg overflow-hidden">
          <div className="p-2 border-b">
            <div className="flex items-center gap-2 border rounded-md px-3 py-1.5 bg-background">
              <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={searchPlaceholder}
                className="flex-1 text-sm bg-transparent outline-none placeholder:text-muted-foreground"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>

          <div className="max-h-60 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="px-3 py-4 text-sm text-muted-foreground text-center">
                No results
              </div>
            ) : (
              filtered.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  className={cn(
                    "flex items-center gap-3 w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground transition-colors",
                    value?.id === option.id && "bg-accent text-accent-foreground",
                  )}
                  onClick={() => handleSelect(option)}
                >
                  <Check
                    className={cn(
                      "h-4 w-4 shrink-0",
                      value?.id === option.id
                        ? "opacity-100"
                        : "opacity-0",
                    )}
                  />
                  <div className="flex-1 min-w-0">
                    {renderOption(option)}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
