import { useState } from "react";

export function CommodityImage({ src, alt, className = "" }: { src: string | null | undefined; alt: string; className?: string }) {
  const [failed, setFailed] = useState(false);
  if (!src || failed) {
    return <div className={`commodity-image commodity-image-placeholder ${className}`} aria-hidden="true">{alt.slice(0, 1).toUpperCase()}</div>;
  }
  return <img className={`commodity-image ${className}`} src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} />;
}
