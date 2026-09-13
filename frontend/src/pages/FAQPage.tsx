import { useEffect, useState } from "react";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { FAQItem } from "../types/api";

export function FAQPage() {
  useDocumentTitle("FAQ");
  const [items, setItems] = useState<FAQItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => { apiFetch<FAQItem[]>("/faq").then(setItems).catch((err: Error) => setError(err.message)).finally(() => setLoading(false)); }, []);
  return <section className="page page-section narrow"><div className="page-title"><span className="eyebrow">PriceYard help</span><h1>Frequently asked questions</h1><p>Published PriceYard explanations about prices, signals, access and safe use.</p></div>{loading ? <LoadingSpinner label="Loading frequently asked questions…" /> : error ? <div className="status-box error">{error}</div> : items.length ? <div className="faq-list">{items.map((item) => <details key={item.id}><summary>{item.question}</summary><div><span className="eyebrow">{item.category}</span><p>{item.answer}</p></div></details>)}</div> : <div className="status-box">No published FAQ items are available yet.</div>}</section>;
}
