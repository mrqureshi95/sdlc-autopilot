import React from "react";

/**
 * Displays a summary of a customer order.
 *
 * SAME PATTERN BUG: Crashes when `order.shipping` is null.
 * The API returns shipping: null for digital-only orders.
 */
export default function OrderSummary({ order }) {
  return (
    <div className="order-summary">
      <h2>Order #{order.id}</h2>
      <p>Status: {order.status}</p>
      <div className="shipping-info">
        <h3>Shipping To</h3>
        <p>{order.shipping.address}</p>
        <p>{order.shipping.city}, {order.shipping.state}</p>
        <p>Method: {order.shipping.method}</p>
      </div>
      <p>Total: ${order.total.toFixed(2)}</p>
    </div>
  );
}
