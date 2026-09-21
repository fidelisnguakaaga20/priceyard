import { Link } from "react-router-dom";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function PaymentCallbackPage() {
  useDocumentTitle("Payment received");
  return (
    <section className="page page-section narrow">
      <div className="page-title">
        <span className="eyebrow">Payment</span>
        <h1>Thank you</h1>
        <p>
          If your payment was successful, your account will update within a few moments. If it does not update
          shortly, please contact support before trying again.
        </p>
      </div>
      <Link className="button" to="/dashboard">Go to Dashboard</Link>
    </section>
  );
}
