export const PRICE_DISCLAIMER = "Prices are market estimates and may change based on quality, quantity, negotiation, transport cost, bag size, time of day, and market conditions. PriceYard provides market information only and does not guarantee profit or exact transaction prices.";
export const MARKET_DISCLAIMER = "Market signals are observations based on available market information. They are not guaranteed predictions or financial advice. Users should verify before making major buying, selling, or storage decisions.";
export const STORAGE_DISCLAIMER = "Storage suitability is based on available market and quality information. It does not guarantee profit, preservation, or future price increase.";

export function Disclaimer({ children }: { children: React.ReactNode }) {
  return <div className="disclaimer" role="note">{children}</div>;
}
