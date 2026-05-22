import os
import stripe
from flask import Blueprint, jsonify, request
from dotenv import load_dotenv

load_dotenv()

payment_bp = Blueprint('payment_bp', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


@payment_bp.route('/stripe/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json() or {}
        shipping_address = data.get('shipping_address', '')
        notes = data.get('notes', '')

        # You can store or log these details as needed
        print("Shipping address:", shipping_address)
        print("Notes:", notes)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'Php',
                    'product_data': {
                        'name': 'Pawfect Finds Order',
                    },
                    'unit_amount': 2000,  # amount in cents ($20)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:5000/success',
            cancel_url='http://127.0.0.1:5000/cancel',
        )

        return jsonify({
            'success': True,
            'checkout_url': session.url
        })

    except Exception as e:
        print("Stripe error:", e)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
