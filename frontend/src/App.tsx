import { lazy, Suspense } from "react";
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
import { ReportPricePage } from "./pages/ReportPricePage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { WatchlistPage } from "./pages/WatchlistPage";
import { VerifyEmailPage } from "./pages/VerifyEmailPage";

const AdminActivityPage = lazy(() => import("./pages/admin/AdminActivityPage").then((module) => ({ default: module.AdminActivityPage })));
const AdminAuditLogsPage = lazy(() => import("./pages/admin/AdminAuditLogsPage").then((module) => ({ default: module.AdminAuditLogsPage })));
const AdminCommoditiesPage = lazy(() => import("./pages/admin/AdminCommoditiesPage").then((module) => ({ default: module.AdminCommoditiesPage })));
const AdminDashboardPage = lazy(() => import("./pages/admin/AdminDashboardPage").then((module) => ({ default: module.AdminDashboardPage })));
const AdminExportPage = lazy(() => import("./pages/admin/AdminExportPage").then((module) => ({ default: module.AdminExportPage })));
const AdminFAQPage = lazy(() => import("./pages/admin/AdminFAQPage").then((module) => ({ default: module.AdminFAQPage })));
const AdminFeedbackPage = lazy(() => import("./pages/admin/AdminFeedbackPage").then((module) => ({ default: module.AdminFeedbackPage })));
const AdminFlaggedPricesPage = lazy(() => import("./pages/admin/AdminFlaggedPricesPage").then((module) => ({ default: module.AdminFlaggedPricesPage })));
const AdminBuyingZonesPage = lazy(() => import("./pages/admin/AdminIntelligencePages").then((module) => ({ default: module.AdminBuyingZonesPage })));
const AdminCostBreakdownPage = lazy(() => import("./pages/admin/AdminIntelligencePages").then((module) => ({ default: module.AdminCostBreakdownPage })));
const AdminSellWatchPage = lazy(() => import("./pages/admin/AdminIntelligencePages").then((module) => ({ default: module.AdminSellWatchPage })));
const AdminStoragePage = lazy(() => import("./pages/admin/AdminIntelligencePages").then((module) => ({ default: module.AdminStoragePage })));
const AdminMarketsPage = lazy(() => import("./pages/admin/AdminMarketsPage").then((module) => ({ default: module.AdminMarketsPage })));
const AdminPriceUpdatesPage = lazy(() => import("./pages/admin/AdminPriceUpdatesPage").then((module) => ({ default: module.AdminPriceUpdatesPage })));
const AdminMarketSignalsPage = lazy(() => import("./pages/admin/AdminSignalsPage").then((module) => ({ default: module.AdminMarketSignalsPage })));
const AdminQualitySignalsPage = lazy(() => import("./pages/admin/AdminSignalsPage").then((module) => ({ default: module.AdminQualitySignalsPage })));
const AdminPaymentsPage = lazy(() => import("./pages/admin/AdminPaymentsPage").then((module) => ({ default: module.AdminPaymentsPage })));
const AdminSubscriptionsPage = lazy(() => import("./pages/admin/AdminSubscriptionsPage").then((module) => ({ default: module.AdminSubscriptionsPage })));
const AdminUsersPage = lazy(() => import("./pages/admin/AdminUsersPage").then((module) => ({ default: module.AdminUsersPage })));

export default function App() {
  return (
    <Suspense fallback={<p role="status" className="page page-section">Loading page?</p>}><Routes>
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
        <Route path="verify-email" element={<VerifyEmailPage />} />
        <Route path="dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="payment/callback" element={<ProtectedRoute><PaymentCallbackPage /></ProtectedRoute>} />
        <Route path="watchlist" element={<ProtectedRoute><WatchlistPage /></ProtectedRoute>} />
        <Route path="feedback" element={<ProtectedRoute><FeedbackPage /></ProtectedRoute>} />
        <Route path="report-price" element={<ProtectedRoute><ReportPricePage /></ProtectedRoute>} />
        <Route path="admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="activity" element={<AdminActivityPage />} />
          <Route path="users" element={<AdminUsersPage />} />
          <Route path="commodities" element={<AdminCommoditiesPage />} />
          <Route path="markets" element={<AdminMarketsPage />} />
          <Route path="prices" element={<AdminPriceUpdatesPage />} />
          <Route path="flagged" element={<AdminFlaggedPricesPage />} />
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
    </Routes></Suspense>
  );
}
