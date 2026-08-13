import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { CommodityDetailPage } from "./pages/CommodityDetailPage";
import { DashboardPage } from "./pages/DashboardPage";
import { FAQPage } from "./pages/FAQPage";
import { FeedbackPage } from "./pages/FeedbackPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { MarketDaysPage } from "./pages/MarketDaysPage";
import { PriceHistoryPage } from "./pages/PriceHistoryPage";
import { PricesPage } from "./pages/PricesPage";
import { RegisterPage } from "./pages/RegisterPage";
import { WatchlistPage } from "./pages/WatchlistPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="prices" element={<PricesPage />} />
        <Route path="commodities/:commodityName" element={<CommodityDetailPage />} />
        <Route path="history" element={<PriceHistoryPage />} />
        <Route path="market-days" element={<MarketDaysPage />} />
        <Route path="faq" element={<FAQPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="watchlist" element={<ProtectedRoute><WatchlistPage /></ProtectedRoute>} />
        <Route path="feedback" element={<ProtectedRoute><FeedbackPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
