"use client";

import { useEffect, useState } from "react";
import Navbar from "./navbar";

export default function NavbarClient() {
  const [hydrated, setHydrated] = useState(false);
  /* eslint-disable-next-line */
  useEffect(() => setHydrated(true), []);
  if (!hydrated) return null;
  return <Navbar />;
}
