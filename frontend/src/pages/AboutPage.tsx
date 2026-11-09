import { SUPPORT_WHATSAPP_NUMBER } from "../components/WhatsAppSupportButton";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { WHATSAPP_COMMUNITY_URL } from "../utils";

const SUPPORT_URL = `https://wa.me/${SUPPORT_WHATSAPP_NUMBER}?text=${encodeURIComponent("Hi PriceYard, I need help with...")}`;
const PARTNER_URL = `https://wa.me/${SUPPORT_WHATSAPP_NUMBER}?text=${encodeURIComponent("Hi PriceYard, I'm interested in exploring a partnership.")}`;

export function AboutPage() {
  useDocumentTitle("About");
  return (
    <section className="page page-section narrow about-page">
      <div className="page-title">
        <h1>About PriceYard</h1>
        <p>
          PriceYard helps traders like bulk buyers who are also into storage of bulk Agricultural products know the
          market before they buy or sell. Instead of guessing, you get clear, checked prices for farm produce in one
          market at a time before decision.
        </p>
      </div>

      <h2>What you get</h2>
      <ul>
        <li>
          Current price ranges for Egusi, Honey Beans, Palm oil and Soybeans etc from real markets, including Kwali
          Market, Owukpa Market and Beans Market Auta Balefi etc.
        </li>
        <li>Price history, so you can see how prices have moved over time.</li>
        <li>Market days, so you know when each market holds.</li>
        <li>
          Market insights for each produce, for full-access members (paid plan or free trial):
          <ul>
            <li>📊 Market signals</li>
            <li>✅ How to identify good produce for storage</li>
            <li>🛒 Right time to buy for storage</li>
            <li>📈 Right time to sell</li>
            <li>💰 Cost breakdown</li>
          </ul>
        </li>
      </ul>

      <h2>Where our prices come from</h2>
      <p>
        Our reporters and team are traders actively buying and selling in each market covered. Every price is checked
        before it is published, and each one shows how it was confirmed. We show a price range, from lowest to highest,
        because traders sell at different prices in the same market.
      </p>

      <h2>Please note</h2>
      <p>PriceYard gives market insights or intelligence only. It does not guarantee profit or predict prices.</p>

      <h2>Who we are</h2>
      <p>PriceYard is run by NGU TOP PRODUCTS AND SERVICES, founded by Nguakaaga Mvendaga.</p>

      <h2>Contact us</h2>
      <p className="about-contact">
        <a className="text-link" href={SUPPORT_URL} target="_blank" rel="noopener noreferrer">
          Chat with us on WhatsApp
        </a>
        {" · "}
        <a className="text-link" href={WHATSAPP_COMMUNITY_URL} target="_blank" rel="noopener noreferrer">
          Join our free WhatsApp updates
        </a>
        {" · "}
        <a className="text-link" href={PARTNER_URL} target="_blank" rel="noopener noreferrer">
          Partner with us
        </a>
      </p>
    </section>
  );
}
