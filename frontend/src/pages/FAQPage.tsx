import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
import type { FAQItem } from "../types/api";

export function FAQPage() {
  const [items, setItems] = useState<FAQItem[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<FAQItem[]>("/faq").then(setItems).catch((err: Error) => setError(err.message)); }, []);
  return <section className="page page-section narrow"><div className="page-title"><span className="eyebrow">PriceYard help</span><h1>Frequently asked questions</h1><p>Published PriceYard explanations about prices, signals, access and safe use.</p></div>{error ? <div className="status-box error">{error}</div> : items.length ? <div className="faq-list">{items.map((item) => <details key={item.id}><summary>{item.question}</summary><div><span className="eyebrow">{item.category}</span><p>{item.answer}</p></div></details>)}</div> : <div className="status-box">No published FAQ items are available yet.</div>}</section>;
}
