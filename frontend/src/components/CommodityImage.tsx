import { useState } from "react";
import { usePreferences } from "../context/PreferencesContext";

export function CommodityImage({ src, alt, className = "" }: { src: string | null | undefined; alt: string; className?: string }) {
  const [failed, setFailed] = useState(false);
  const { dataSaver } = usePreferences();
  if (!src || failed || dataSaver) {
    return <div className={`commodity-image commodity-image-placeholder ${className}`} aria-hidden="true" title={dataSaver && src ? "Image hidden — Data saver is on" : undefined}>{alt.slice(0, 1).toUpperCase()}</div>;
  }
  return <img className={`commodity-image ${className}`} src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} />;
}
