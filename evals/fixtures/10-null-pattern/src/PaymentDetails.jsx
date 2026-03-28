import React from "react";

/**
 * Displays payment method details.
 *
 * SAME PATTERN BUG: Crashes when `payment.card` is null.
 * The API returns card: null for payments made via bank transfer or PayPal.
 */
export default function PaymentDetails({ payment }) {
  return (
    <div className="payment-details">
      <h2>Payment</h2>
      <p>Amount: ${payment.amount.toFixed(2)}</p>
      <p>Date: {payment.date}</p>
      <div className="card-info">
        <h3>Card Information</h3>
        <p>Type: {payment.card.type}</p>
        <p>Ending in: {payment.card.last4}</p>
        <p>Expires: {payment.card.expiry}</p>
      </div>
      <p>Status: {payment.status}</p>
    </div>
  );
}
