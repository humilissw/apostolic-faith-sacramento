// Re-export all domain-specific API modules for backwards compatibility.
// New code should import directly from the domain module (e.g., "@/lib/api/auth").

export * from "./auth";
export * from "./payments";
export * from "./integrations";
export * from "./users";
export * from "./scheduler";
export * from "./feature-flags";
export * from "./video-uploads";
