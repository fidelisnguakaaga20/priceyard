import { usePreferences } from "./context/PreferencesContext";

export type Language = "en" | "pcm";

// Covers the highest-traffic static UI text (nav, home page, report-a-price form).
// Dynamic server content (FAQ answers, testimonials, price notes) is never
// pre-translated here -- it comes from the database in whatever language it was
// entered in.
const TRANSLATIONS: Record<string, Record<Language, string>> = {
  nav_current_prices: { en: "Current Prices", pcm: "Price Wey Dey Now" },
  nav_price_history: { en: "Price History", pcm: "Price Wey Pass" },
  nav_market_days: { en: "Market Days", pcm: "Market Days" },
  nav_faq: { en: "FAQ", pcm: "Questions" },
  nav_watchlist: { en: "Watchlist", pcm: "My Watchlist" },
  nav_feedback: { en: "Feedback", pcm: "Tell Us Wetin You Think" },
  nav_report_price: { en: "Report a price", pcm: "Report Price" },
  nav_admin: { en: "Admin", pcm: "Admin" },
  nav_dashboard: { en: "Dashboard", pcm: "My Page" },
  nav_log_out: { en: "Log out", pcm: "Comot" },
  nav_log_in: { en: "Log in", pcm: "Enter" },

  toggle_data_saver: { en: "Data saver", pcm: "Save Data" },
  toggle_easy_reading: { en: "Easy reading", pcm: "Big Letter" },
  toggle_dark_mode: { en: "Dark mode", pcm: "Dark Mode" },
  toggle_language: { en: "Language", pcm: "Language" },
  toggle_on: { en: "On", pcm: "On" },
  toggle_off: { en: "Off", pcm: "Off" },
  language_english: { en: "English", pcm: "English" },
  language_pidgin: { en: "Pidgin", pcm: "Pidgin" },

  home_eyebrow: { en: "Market price information", pcm: "Market Price Information" },
  home_headline: { en: "Know the market before you buy or sell.", pcm: "Know market before you buy or sell." },
  home_subtext: {
    en: "See today's and past prices, price changes, and real market updates for Egusi, Honey Beans and Palm oil.",
    pcm: "See today price and old price, how price change, and real market update for Egusi, Honey Beans and Palm oil.",
  },
  home_live_now: { en: "Live now", pcm: "Wetin Dey Happen Now" },
  home_check_prices: { en: "Check prices", pcm: "Check Price" },
  home_see_market_days: { en: "See market days", pcm: "See Market Days" },
  home_panel_title: { en: "PriceYard starts focused.", pcm: "PriceYard sharp sharp." },
  home_panel_li1: { en: "PriceYard covers Egusi, Honey Beans, Palm oil", pcm: "PriceYard dey cover Egusi, Honey Beans, Palm oil" },
  home_panel_li2: { en: "Abuja/FCT, Kwali, Nasarawa, Benue", pcm: "Abuja/FCT, Kwali, Nasarawa, Benue" },
  home_panel_li3: { en: "Real price range, not one fixed number", pcm: "Real price range, no be one fix number" },
  home_panel_li4: { en: "How sure we are about the price, and when it was last checked", pcm: "How we sure well well for the price, and when we last check am" },
  home_join_whatsapp: { en: "Join our free WhatsApp updates →", pcm: "Join our free WhatsApp update →" },

  home_products_tracked: { en: "product(s) tracked", pcm: "product(s) wey we dey track" },
  home_markets_covered: { en: "market(s) covered", pcm: "market(s) wey we cover" },
  home_confirmed_prices: { en: "confirmed price(s)", pcm: "price(s) wey don confirm" },

  home_coming_soon_eyebrow: { en: "Coming soon", pcm: "Dey Come" },
  home_coming_soon_heading: { en: "New products coming soon", pcm: "New product dey come" },
  home_today_eyebrow: { en: "Latest market information", pcm: "Latest Market Gist" },
  home_today_heading: { en: "Today's prices", pcm: "Today Price" },
  home_see_all_prices: { en: "See all prices →", pcm: "See all price →" },
  home_testimonials_eyebrow: { en: "From real users", pcm: "From Real People" },
  home_testimonials_heading: { en: "What traders are saying", pcm: "Wetin Traders Dey Talk" },

  home_tile1_title: { en: "Compare prices", pcm: "Compare Price" },
  home_tile1_body: { en: "See current and previous ranges without pretending every market transaction has one exact price.", pcm: "See price wey dey now and wey pass, we no go pretend say na one correct price dey for everywhere." },
  home_tile2_title: { en: "Read our market notes", pcm: "Read Our Market Note" },
  home_tile2_body: { en: "Possible Meaning and Suggested Action stay observational and are never presented as guaranteed trading instructions.", pcm: "Wetin E Fit Mean and Wetin You Fit Do na just observation, we no dey tell you say na must-do." },
  home_tile3_title: { en: "Check how sure we are", pcm: "Check How Sure We Dey" },
  home_tile3_body: { en: "Use source confidence, market timing and freshness before making a major buying, selling or storage decision.", pcm: "Use how we sure, market time and how fresh e be before you take any big buy, sell or store decision." },

  report_eyebrow: { en: "Field report", pcm: "Market Report" },
  report_heading: { en: "Report a market price", pcm: "Report Market Price" },
  report_sub: {
    en: "Quick price report from the market. An admin will review before it goes live — no need to add commentary or sourcing.",
    pcm: "Quick price report from market. Admin go check am before e show for everybody — no need to add any comment or source.",
  },
  report_commodity: { en: "Commodity", pcm: "Wetin You Dey Sell" },
  report_choose_commodity: { en: "Choose a commodity", pcm: "Pick wetin you dey sell" },
  report_market: { en: "Market", pcm: "Market" },
  report_choose_market: { en: "Choose a market", pcm: "Pick market" },
  report_price_low: { en: "Price low", pcm: "Price Wey Low" },
  report_price_high: { en: "Price high", pcm: "Price Wey High" },
  report_unit: { en: "Number of bags", pcm: "How Many Bag" },
  report_bag_size: { en: "Bag size (kg)", pcm: "Bag Size (kg)" },
  report_movement: { en: "Movement", pcm: "Price Movement" },
  report_date_seen: { en: "Date/time seen", pcm: "Date/Time You See Am" },
  report_submit: { en: "Submit price report", pcm: "Send Price Report" },
  report_submitting: { en: "Submitting…", pcm: "E Dey Send…" },
};

export function translate(language: Language, key: keyof typeof TRANSLATIONS): string {
  return TRANSLATIONS[key]?.[language] ?? TRANSLATIONS[key]?.en ?? key;
}

export function useTranslation() {
  const { language } = usePreferences();
  return (key: keyof typeof TRANSLATIONS) => translate(language, key);
}
