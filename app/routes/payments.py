import os
from flask import Blueprint, request, jsonify, current_app, url_for, session
try:
    from app import csrf
except ImportError:
    csrf = None
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

payments_bp = Blueprint('payments', __name__)

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@payments_bp.route('/payments/stripe/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout session and return the redirect URL."""
    try:
        # Verify Stripe key is configured
        if not stripe.api_key:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        if not stripe.api_key:
            current_app.logger.error("STRIPE_SECRET_KEY not found in environment")
            return jsonify({"success": False, "message": "Payment system not configured. Please contact support."}), 500
        
        data = request.get_json(silent=True) or request.form
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        shipping_address = (data.get('shipping_address') or '').strip()
        notes = (data.get('notes') or '').strip() or None

        # Build absolute URLs for Stripe
        # Use the request origin to build proper URLs
        scheme = request.scheme  # http or https
        host = request.host  # e.g., localhost:5000 or yourdomain.com
        success_url = f"{scheme}://{host}{url_for('user.orders')}?paid=1"
        cancel_url = f"{scheme}://{host}{url_for('user.checkout')}"
        
        # Debug logging
        current_app.logger.info(f"Success URL: {success_url}")
        current_app.logger.info(f"Cancel URL: {cancel_url}")

        from app.services.stripe_service import create_checkout_session as create_stripe_session
        checkout_url = create_stripe_session(
            user_id=int(user_id),
            shipping_address=shipping_address,
            notes=notes,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return jsonify({"success": True, "checkout_url": checkout_url})
    except ValueError as e:
        current_app.logger.error(f"Validation error: {e}")
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Failed to create Stripe Checkout session")
        return jsonify({"success": False, "message": f"Payment error: {str(e)}"}), 500


@payments_bp.route('/payments/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Stripe webhook endpoint for checkout completion and payment events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=webhook_secret
            )
        else:
            # If no secret configured, accept the payload as-is (development only)
            event = request.get_json(force=True)
    except Exception as e:
        current_app.logger.warning(f"Stripe webhook signature verification failed: {e}")
        return jsonify({"success": False}), 400

    try:
        event_type = event.get('type') if isinstance(event, dict) else getattr(event, 'type', None)
        data_object = (event.get('data', {}) or {}).get('object') if isinstance(event, dict) else event.data.object

        if event_type in ('checkout.session.completed',):
            # Fulfill the order(s)
            from app.services.stripe_service import fulfill_checkout_session
            created_ids = fulfill_checkout_session(data_object)
            current_app.logger.info(f"Created orders from Stripe session: {created_ids}")
        elif event_type in ('payment_intent.succeeded',):
            # Not used with Checkout directly, but keep for completeness
            pass
    except Exception as e:
        current_app.logger.exception("Error processing Stripe webhook")
        return jsonify({"received": True, "processed": False}), 200

    return jsonify({"received": True}), 200
