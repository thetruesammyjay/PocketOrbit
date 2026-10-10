"use client";

import { useEffect, useRef, type ReactNode } from "react";

export function ScrollReveal({
  children,
  className
}: Readonly<{
  children: ReactNode;
  className?: string;
}>) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    if (!("IntersectionObserver" in window)) {
      container.classList.add("is-visible");
      return;
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (!entry?.isIntersecting) return;
      container.classList.add("is-visible");
      observer.disconnect();
    }, { threshold: 0.18 });

    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  return <div className={className} ref={containerRef}>{children}</div>;
}
