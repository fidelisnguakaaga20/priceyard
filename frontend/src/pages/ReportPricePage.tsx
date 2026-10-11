import { FormEvent, useEffect, useState } from "react";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { ApiError, apiFetch } from "../services/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useTranslation } from "../translations";
import type { Commodity, Market } from "../types/api";

const movements = ["up", "down", "stable", "unknown"];

function errorText(err: unknown): string {
  return err instanceof ApiError ? err.detail : err instanceof Error ? err.message : "Request failed.";
}

function nowForInput(): string {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

export function ReportPricePage() {
  useDocumentTitle("Report a price");
  const { token, user } = useAuth();
  const { showToast } = useToast();
  const t = useTranslation();
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setOptionsLoading(true);
    void Promise.all([apiFetch<Commodity[]>("/commodities"), apiFetch<Market[]>("/markets")])
      .then(([c, m]) => { setCommodities(c); setMarkets(m); })
      .catch((err) => setError(errorText(err)))
      .finally(() => setOptionsLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || busy) return;
    const form = event.currentTarget;
    const f = new FormData(form);
    const priceLow = Number(f.get("price_low"));
    const priceHigh = Number(f.get("price_high"));
    const payload = {
      commodity_id: Number(f.get("commodity_id")),
      market_id: Number(f.get("market_id")),
      price_low: priceLow,
      price_high: priceHigh,
      average_price: Math.round((priceLow + priceHigh) * 50) / 100,
      unit: String(f.get("unit")),
      bag_size: String(f.get("bag_size")),
      movement: String(f.get("movement")),
      confidence_level: "Reporter submitted",
      update_date_time: new Date(String(f.get("update_date_time"))).toISOString(),
      is_outdated: false,
      suggested_action: "Watch",
    };
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await apiFetch("/price-updates", { method: "POST", body: JSON.stringify(payload) }, token);
      setMessage("Thank you. Your price report was submitted for review.");
      showToast("Price report submitted for review.");
      form.reset();
    } catch (err) {
      setError(errorText(err));
      showToast(errorText(err), "error");
    } finally {
      setBusy(false);
    }
  }

  if (user && user.role !== "reporter" && user.role !== "admin") {
    return <section className="page page-section narrow">
      <div className="status-box error">This page is only available to approved field reporters.</div>
    </section>;
  }

  return <section className="page page-section narrow">
    <div className="page-title">
      <span className="eyebrow">{t("report_eyebrow")}</span>
      <h1>{t("report_heading")}</h1>
      <p>{t("report_sub")}</p>
    </div>
    <form className="form-stack card" onSubmit={submit}>
      <label>
        {t("report_commodity")}
        <select name="commodity_id" required disabled={optionsLoading}>
          <option value="">{t("report_choose_commodity")}</option>
          {commodities.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
        </select>
      </label>
      <label>
        {t("report_market")}
        <select name="market_id" required disabled={optionsLoading}>
          <option value="">{t("report_choose_market")}</option>
          {markets.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}
        </select>
      </label>
      <div className="form-grid">
        <label>{t("report_price_low")}<input name="price_low" type="number" min="0" step="0.01" required /></label>
        <label>{t("report_price_high")}<input name="price_high" type="number" min="0" step="0.01" required /></label>
        <label>{t("report_unit")}<input name="unit" defaultValue="1 bag" placeholder="e.g. 1 bag" required /></label>
        <label>{t("report_bag_size")}<input name="bag_size" placeholder="e.g. 50kg" required /></label>
        <label>{t("report_movement")}<select name="movement" defaultValue="unknown">{movements.map((item) => <option key={item}>{item}</option>)}</select></label>
        <label>{t("report_date_seen")}<input name="update_date_time" type="datetime-local" defaultValue={nowForInput()} required /></label>
      </div>
      {message && <div className="status-box success">{message}</div>}
      {error && <div className="status-box error">{error}</div>}
      <button className="button" disabled={busy || optionsLoading}>
        {busy ? <ButtonSpinner label={t("report_submitting")} /> : t("report_submit")}
      </button>
    </form>
  </section>;
}
