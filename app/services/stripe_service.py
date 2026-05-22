import os
from typing import Tuple, List

import stripe
from flask import current_app, request
from dotenv import load_dotenv

from app.models.cart import Cart
from app.models.order import Order

# Load environment variables
load_dotenv()


def _get_env_key() -> str | None:
    return os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")


def _ensure_api_key() -> bool:
    """Ensure stripe.api_key is set from env or Flask config.

    Returns True if configured, else False.
    """
    if not getattr(stripe, "api_key", None):
        key = _get_env_key()
        if not key:
            try:
                key = (
                    current_app.config.get("STRIPE_SECRET_KEY")
                    or current_app.config.get("STRIPE_API_KEY")
                )
            except Exception:
                key = None
        if key:
            stripe.api_key = key
    return bool(getattr(stripe, "api_key", None))


# Try to initialize at import time (works if env already loaded)
_ensure_api_key()


def _peso_to_centavos(amount_php: float) -> int:
    try:
        return int(round(float(amount_php) * 100))
    except Exception:
        return 0


def build_line_items(user_id: int) -> Tuple[List[dict], float]:
    """Build Stripe line_items from the user's cart.

    Returns: (line_items, total_php)
    """
    items = Cart.get_user_cart(user_id)
    line_items: List[dict] = []
    total = 0.0
    for it in items or []:
        price_each = float(it.get("price", 0))
        qty = int(it.get("quantity", 1))
        total += price_each * qty
        name = it.get("name") or f"Product #{it.get('product_id')}"
        image = it.get("image_url")
        
        # Stripe requires absolute URLs for images, so skip relative URLs
        # Only include image if it's a valid absolute URL
        image_list = []
        if image and (image.startswith('http://') or image.startswith('https://')):
            image_list = [image]
        
        line = {
            "price_data": {
                "currency": "php",
                "product_data": {
                    "name": name[:250],
                    **({"images": image_list} if image_list else {}),
                },
                "unit_amount": _peso_to_centavos(price_each),
            },
            "quantity": max(qty, 1),
        }
        line_items.append(line)
    return line_items, total


def create_checkout_session(user_id: int, shipping_address: str, notes: str | None, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout Session for the current cart.

    Returns the hosted checkout URL to redirect the user to.
    """
    if not _ensure_api_key():
        raise RuntimeError("Stripe secret key is not configured")

    line_items, total = build_line_items(user_id)
    if not line_items:
        raise ValueError("Cart is empty")
    
    # Stripe requires minimum 50 cents (or ~₱29 PHP at current rates)
    # For testing: Add padding fee if total is below minimum
    STRIPE_MINIMUM_PHP = 50.0
    if total < STRIPE_MINIMUM_PHP:
        padding_amount = STRIPE_MINIMUM_PHP - total
        current_app.logger.info(f"Adding padding of ₱{padding_amount:.2f} to meet Stripe minimum")
        # Add a padding line item
        line_items.append({
            "price_data": {
                "currency": "php",
                "product_data": {
                    "name": "Processing Fee (Minimum Order Adjustment)",
                },
                "unit_amount": _peso_to_centavos(padding_amount),
            },
            "quantity": 1,
        })
        total = STRIPE_MINIMUM_PHP

    # Debug logging
    current_app.logger.info(f"Creating Stripe session with success_url: {success_url}")
    current_app.logger.info(f"Creating Stripe session with cancel_url: {cancel_url}")
    current_app.logger.info(f"Line items count: {len(line_items)}, Total: ₱{total:.2f}")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=line_items,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": str(user_id),
            "shipping_address": shipping_address[:500] if shipping_address else "",
            "notes": (notes or "")[:500],
        },
        allow_promotion_codes=True,
        billing_address_collection="auto",
    )
    return session.url


def fulfill_checkout_session(session_obj) -> List[int]:
    """Create orders from the cart when a Checkout Session completes.

    Returns list of created order IDs.
    """
    metadata = (session_obj.get("metadata") or {}) if isinstance(session_obj, dict) else {}
    user_id = int(metadata.get("user_id")) if metadata.get("user_id") else None
    shipping_address = metadata.get("shipping_address") or ""
    notes = metadata.get("notes") or None

    if not user_id:
        return []

    order_ids = Order.create_from_cart(user_id, shipping_address, payment_method="online", notes=notes)

    # Mark payment as paid for each order
    try:
        for oid in order_ids or []:
            try:
                Order.update_payment_status(oid, "paid")
                Order.update_status(oid, "confirmed")
            except Exception:
                # Best effort; continue
                pass
    except Exception:
        pass

    return order_ids
