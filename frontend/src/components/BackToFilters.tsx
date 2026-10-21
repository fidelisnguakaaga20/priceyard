import { useEffect, useState } from "react";
import type { RefObject } from "react";

export function BackToFilters({ filtersRef, enabled }: { filtersRef: RefObject<HTMLFormElement>; enabled: boolean }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const filters = filtersRef.current;
    if (!enabled || !filters) { setVisible(false); return; }
    const header = document.querySelector(".site-header");
    let observer: IntersectionObserver;
    const watch = () => {
      observer?.disconnect();
      const headerBottom = Math.max(0, header?.getBoundingClientRect().bottom ?? 0);
      setVisible(filters.getBoundingClientRect().bottom <= headerBottom);
      observer = new IntersectionObserver(([entry]) => {
        setVisible(!entry.isIntersecting && entry.boundingClientRect.bottom <= headerBottom);
      }, { rootMargin: `-${Math.ceil(headerBottom)}px 0px 0px 0px` });
      observer.observe(filters);
    };
    watch();
    const headerSize = new ResizeObserver(watch);
    if (header) headerSize.observe(header);
    window.addEventListener("resize", watch);
    return () => { observer?.disconnect(); headerSize.disconnect(); window.removeEventListener("resize", watch); };
  }, [enabled, filtersRef]);

  if (!enabled || !visible) return null;
  const back = () => {
    const filters = filtersRef.current;
    if (!filters) return;
    const headerBottom = Math.max(0, document.querySelector(".site-header")?.getBoundingClientRect().bottom ?? 0);
    const top = window.scrollY + filters.getBoundingClientRect().top - headerBottom - 16;
    filters.querySelector("select")?.focus({ preventScroll: true });
    window.scrollTo({ top: Math.max(0, top), behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  };
  return <button type="button" className="button history-back-to-filters" onClick={back} aria-label="Back to filters">
    <span aria-hidden="true">↑</span> Back to filters
  </button>;
}
