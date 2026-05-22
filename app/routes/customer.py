from flask import Blueprint, redirect, url_for, flash

customer_bp = Blueprint('customer', __name__)

# All customer routes temporarily disabled during Supabase migration

@customer_bp.route('/dashboard')
def dashboard():
    flash('Customer features are being migrated to Supabase.', 'info')
    return redirect(url_for('public.landing'))

@customer_bp.route('/orders')
def orders():
    flash('Orders page is being migrated to Supabase.', 'info')
    return redirect(url_for('public.landing'))
