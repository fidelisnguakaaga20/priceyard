import { Navigate, Route, Routes } from "react-router-dom";
import { AdminLayout } from "./components/AdminLayout";
import { AdminRoute } from "./components/AdminRoute";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { CommodityDetailPage } from "./pages/CommodityDetailPage";
import { DashboardPage } from "./pages/DashboardPage";
import { FAQPage } from "./pages/FAQPage";
import { FeedbackPage } from "./pages/FeedbackPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { MarketDaysPage } from "./pages/MarketDaysPage";
import { PaymentCallbackPage } from "./pages/PaymentCallbackPage";
import { PriceHistoryPage } from "./pages/PriceHistoryPage";
import { PricesPage } from "./pages/PricesPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { WatchlistPage } from "./pages/WatchlistPage";
import { AdminActivityPage } from "./pages/admin/AdminActivityPage";
import { AdminAuditLogsPage } from "./pages/admin/AdminAuditLogsPage";
import { AdminCommoditiesPage } from "./pages/admin/AdminCommoditiesPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminExportPage } from "./pages/admin/AdminExportPage";
import { AdminFAQPage } from "./pages/admin/AdminFAQPage";
import { AdminFeedbackPage } from "./pages/admin/AdminFeedbackPage";
import { AdminBuyingZonesPage, AdminCostBreakdownPage, AdminSellWatchPage, AdminStoragePage } from "./pages/admin/AdminIntelligencePages";
import { AdminMarketsPage } from "./pages/admin/AdminMarketsPage";
import { AdminPriceUpdatesPage } from "./pages/admin/AdminPriceUpdatesPage";
import { AdminMarketSignalsPage, AdminQualitySignalsPage } from "./pages/admin/AdminSignalsPage";
import { AdminPaymentsPage } from "./pages/admin/AdminPaymentsPage";
import { AdminSubscriptionsPage } from "./pages/admin/AdminSubscriptionsPage";
import { AdminUsersPage } from "./pages/admin/AdminUsersPage";

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
        <Route path="forgot-password" element={<ForgotPasswordPage />} />
        <Route path="reset-password" element={<ResetPasswordPage />} />
        <Route path="dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="payment/callback" element={<ProtectedRoute><PaymentCallbackPage /></ProtectedRoute>} />
        <Route path="watchlist" element={<ProtectedRoute><WatchlistPage /></ProtectedRoute>} />
        <Route path="feedback" element={<ProtectedRoute><FeedbackPage /></ProtectedRoute>} />
        <Route path="admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="activity" element={<AdminActivityPage />} />
          <Route path="users" element={<AdminUsersPage />} />
          <Route path="commodities" element={<AdminCommoditiesPage />} />
          <Route path="markets" element={<AdminMarketsPage />} />
          <Route path="prices" element={<AdminPriceUpdatesPage />} />
          <Route path="market-signals" element={<AdminMarketSignalsPage />} />
          <Route path="quality-signals" element={<AdminQualitySignalsPage />} />
          <Route path="buying-zones" element={<AdminBuyingZonesPage />} />
          <Route path="sell-watch" element={<AdminSellWatchPage />} />
          <Route path="storage" element={<AdminStoragePage />} />
          <Route path="costs" element={<AdminCostBreakdownPage />} />
          <Route path="faq" element={<AdminFAQPage />} />
          <Route path="subscriptions" element={<AdminSubscriptionsPage />} />
          <Route path="payments" element={<AdminPaymentsPage />} />
          <Route path="feedback" element={<AdminFeedbackPage />} />
          <Route path="audit" element={<AdminAuditLogsPage />} />
          <Route path="export" element={<AdminExportPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
