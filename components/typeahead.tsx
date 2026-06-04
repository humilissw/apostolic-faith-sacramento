"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Check, Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

// --- Types ---

export interface TypeaheadOption {
  id: string;
  label: string;
  subtitle?: string;
}

export interface TypeaheadProps<T extends TypeaheadOption> {
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
  emptyText?: string;
}

// --- Component ---

export function Typeahead<T extends TypeaheadOption>({
  options,
  value,
  onChange,
  label,
  placeholder = "Search...",
  searchFn,
  renderOption,
  renderValue,
  className,
  disabled = false,
  emptyText = "No results",
}: TypeaheadProps<T>) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const filtered = query
    ? options.filter((o) => searchFn(o, query))
    : options;

  const showDropdown = focused && !disabled;

  const handleClick = useCallback(() => {
    if (!disabled) {
      setFocused(true);
      inputRef.current?.focus();
    }
  }, [disabled]);

  const handleSelect = useCallback(
    (option: T) => {
      onChange(option);
      setQuery("");
      setFocused(false);
    },
    [onChange],
  );

  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onChange(null);
      setQuery("");
      inputRef.current?.focus();
    },
    [onChange],
  );

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setFocused(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        setFocused(false);
        return;
      }
      if (e.key === "ArrowDown" && showDropdown) {
        e.preventDefault();
        inputRef.current?.blur();
      }
    },
    [showDropdown],
  );

  return (
    <div ref={wrapperRef} className={cn("relative", className)}>
      {label && (
        <label className="block text-sm font-medium text-muted-foreground mb-1">
          {label}
        </label>
      )}

      <div
        className={cn(
          "flex items-center gap-2 border rounded-md px-3 py-2 min-h-10 bg-background cursor-text",
          "hover:border-input transition-colors",
          focused && "border-ring ring-1 ring-ring/20",
          disabled && "opacity-50 cursor-not-allowed",
        )}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={showDropdown}
        aria-haspopup="listbox"
        aria-controls={`typeahead-list-${placeholder}`}
      >
        {value ? (
          <>
            <div className="flex-1 truncate">{renderValue(value)}</div>
            {!disabled && (
              <button
                type="button"
                onClick={handleClear}
                className="shrink-0 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </>
        ) : (
          <>
            <Search className="h-4 w-4 text-muted-foreground shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={value ? "" : placeholder}
              className={cn(
                "flex-1 text-sm bg-transparent outline-none placeholder:text-muted-foreground",
                value && "placeholder-transparent",
              )}
              onFocus={() => !disabled && setFocused(true)}
              disabled={disabled}
              aria-label={placeholder}
            />
          </>
        )}
      </div>

      {showDropdown && (
        <div className="absolute z-50 mt-1 w-full bg-popover border rounded-md shadow-lg overflow-hidden">
          {filtered.length === 0 ? (
            <div className="px-3 py-4 text-sm text-muted-foreground text-center">
              {emptyText}
            </div>
          ) : (
            <div className="max-h-60 overflow-y-auto" role="listbox">
              {filtered.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  className={cn(
                    "flex items-center gap-3 w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground transition-colors",
                    value?.id === option.id && "bg-accent text-accent-foreground",
                  )}
                  onClick={() => handleSelect(option)}
                  role="option"
                  aria-selected={value?.id === option.id}
                >
                  <Check
                    className={cn(
                      "h-4 w-4 shrink-0",
                      value?.id === option.id ? "opacity-100" : "opacity-0",
                    )}
                  />
                  <div className="flex-1 min-w-0">{renderOption(option)}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
