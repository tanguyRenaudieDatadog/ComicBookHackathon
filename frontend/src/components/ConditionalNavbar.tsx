'use client';
import { usePathname } from "next/navigation";
import { Navbar } from "@/components/landing/Navbar";

export function ConditionalNavbar() {
  const pathname = usePathname();
  if (pathname !== "/") return null;
  return <Navbar />;
} 