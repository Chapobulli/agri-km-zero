from flask import Blueprint, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import Product, Message, User

cart = Blueprint('cart', __name__)

def _get_cart():
    return session.setdefault('cart', {})

def _save_session():
    session.modified = True

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    farmer_id = product.user_id
    qty = request.form.get('qty', '1')
    try:
        qty = max(1, int(qty))
    except Exception:
        qty = 1
    c = _get_cart()
    farmer_cart = c.setdefault(str(farmer_id), {})
    item = farmer_cart.setdefault(str(product_id), {
        'name': product.name,
        'unit': product.unit or 'pz',
        'price': float(product.price or 0),
        'qty': 0
    })
    item['qty'] += qty
    _save_session()
    flash('✓ Prodotto aggiunto al carrello', 'success')
    farmer = User.query.get(farmer_id)
    return redirect(url_for('profiles.view_profile', username=farmer.username))

@cart.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    product = Product.query.get_or_404(product_id)
    farmer_id = product.user_id
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id), {})
    if str(product_id) in farmer_cart:
        farmer_cart.pop(str(product_id))
        if not farmer_cart:
            c.pop(str(farmer_id), None)
        _save_session()
        flash('Prodotto rimosso dal carrello', 'info')
    farmer = User.query.get(farmer_id)
    return redirect(url_for('profiles.view_profile', username=farmer.username))

@cart.route('/cart/clear/<int:farmer_id>', methods=['POST'])
@login_required
def clear_cart(farmer_id):
    c = _get_cart()
    c.pop(str(farmer_id), None)
    _save_session()
    flash('Carrello svuotato', 'info')
    farmer = User.query.get_or_404(farmer_id)
    return redirect(url_for('profiles.view_profile', username=farmer.username))

@cart.route('/cart/send/<int:farmer_id>', methods=['POST'])
@login_required
def send_order(farmer_id):
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id))
    if not farmer_cart:
        flash('Il carrello è vuoto', 'warning')
        farmer = User.query.get_or_404(farmer_id)
        return redirect(url_for('profiles.view_profile', username=farmer.username))
    # Compose order summary
    lines = [f"Nuovo ordine da {current_user.display_name or current_user.username}"]
    total = 0.0
    for pid, item in farmer_cart.items():
        subtotal = float(item['price']) * int(item['qty'])
        total += subtotal
        lines.append(f"- {item['name']} x{item['qty']} ({item['unit']}) → {subtotal:.2f} €")
    lines.append(f"Totale: {total:.2f} €")
    if current_user.address:
        lines.append(f"Indirizzo: {current_user.address}")
    if current_user.city or current_user.province:
        lines.append(f"Località: {current_user.city or ''} {('('+current_user.province+')') if current_user.province else ''}")
    content = "\n".join(lines)
    # Persist as message
    msg = Message(content=content, sender_id=current_user.id, recipient_id=farmer_id)
    db.session.add(msg)
    db.session.commit()
    # Clear cart after sending
    c.pop(str(farmer_id), None)
    _save_session()
    flash('Ordine inviato all\'azienda via messaggio', 'success')
    return redirect(url_for('messages.conversation', user_id=farmer_id))
