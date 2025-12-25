from flask import Blueprint, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import Product, Message, User, OrderRequest
from .email_utils import send_email
import json

cart = Blueprint('cart', __name__)

def _get_cart():
    return session.setdefault('cart', {})

def _save_session():
    session.modified = True

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
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

@cart.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    product = Product.query.get_or_404(product_id)
    farmer_id = product.user_id
    action = request.form.get('action', 'set')
    qty = request.form.get('qty', '1')
    try:
        qty = max(1, int(qty))
    except Exception:
        qty = 1
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id), {})
    if str(product_id) in farmer_cart:
        if action == 'increment':
            farmer_cart[str(product_id)]['qty'] += 1
        elif action == 'decrement':
            farmer_cart[str(product_id)]['qty'] = max(1, farmer_cart[str(product_id)]['qty'] - 1)
        else:
            farmer_cart[str(product_id)]['qty'] = qty
        _save_session()
    farmer = User.query.get(farmer_id)
    return redirect(url_for('profiles.view_profile', username=farmer.username))

@cart.route('/cart/clear/<int:farmer_id>', methods=['POST'])
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

@cart.route('/orders/create/<int:farmer_id>', methods=['POST'])
def create_order(farmer_id):
    # Allow guests to place orders: collect contact info
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id))
    if not farmer_cart:
        flash('Il carrello è vuoto', 'warning')
        farmer = User.query.get_or_404(farmer_id)
        return redirect(url_for('profiles.view_profile', username=farmer.username))
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    delivery = request.form.get('delivery', 'off') == 'on'
    address = request.form.get('address', '').strip()
    if not (email or phone):
        flash('Inserisci almeno email o telefono per la conferma', 'warning')
        farmer = User.query.get_or_404(farmer_id)
        return redirect(url_for('profiles.view_profile', username=farmer.username))
    if delivery and not address:
        flash('Inserisci un indirizzo per la consegna', 'warning')
        farmer = User.query.get_or_404(farmer_id)
        return redirect(url_for('profiles.view_profile', username=farmer.username))
    total = 0.0
    for _, item in farmer_cart.items():
        total += float(item['price']) * int(item['qty'])
    order = OrderRequest(
        farmer_id=farmer_id,
        client_id=current_user.id if getattr(current_user, 'is_authenticated', False) else None,
        client_name=name or (current_user.display_name if getattr(current_user, 'is_authenticated', False) else None),
        client_email=email,
        client_phone=phone,
        delivery_address=address if delivery else None,
        delivery_requested=delivery,
        items_json=json.dumps(farmer_cart),
        total_price=total,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    # Notify farmer via email (if available)
    try:
        farmer = User.query.get_or_404(farmer_id)
        if farmer.email:
            items = []
            for _, item in farmer_cart.items():
                items.append(f"<li><strong>{item['name']}</strong> x{item['qty']} {item['unit']} — {float(item['price'])*int(item['qty']):.2f} €</li>")
            html = f"""
                <h3>Nuovo ordine ricevuto</h3>
                <p><strong>Da:</strong> {order.client_name or 'Cliente'}<br/>
                <strong>Telefono:</strong> {order.client_phone or '—'}<br/>
                <strong>Email:</strong> {order.client_email or '—'}</p>
                <ul>{''.join(items)}</ul>
                <p><strong>Totale:</strong> {order.total_price:.2f} €</p>
                {'<p><strong>Consegna:</strong> ' + (order.delivery_address or '') + '</p>' if order.delivery_requested else ''}
                <p>Accedi alla tua pagina per <strong>accettare</strong> o <strong>rifiutare</strong> l'ordine.</p>
            """
            send_email(farmer.email, "Agri KM Zero: nuovo ordine", html)
        # Send confirmation to client if email provided
        if order.client_email:
            send_email(order.client_email, "Conferma ordine inviato", f"""
                <h3>Ordine inviato a {farmer.company_name or farmer.username}</h3>
                <p>Totale: <strong>{order.total_price:.2f} €</strong></p>
                <p>Riceverai conferma dall'azienda.</p>
            """)
    except Exception:
        pass
    # Clear cart after creating order
    c.pop(str(farmer_id), None)
    _save_session()
    flash('Ordine inviato: l\'azienda riceverà i dettagli e potrà rispondere', 'success')
    return redirect(url_for('profiles.view_profile', username=farmer.username))

@cart.route('/orders/accept/<int:order_id>', methods=['POST'])
@login_required
def accept_order(order_id):
    order = OrderRequest.query.get_or_404(order_id)
    if current_user.id != order.farmer_id:
        flash('Non autorizzato', 'danger')
        return redirect(url_for('profiles.view_profile', username=current_user.username))
    order.status = 'accepted'
    db.session.commit()
    # Send acceptance email to client
    if order.client_email:
        try:
            farmer = User.query.get(order.farmer_id)
            send_email(order.client_email, "Ordine accettato", f"""
                <h3>Il tuo ordine è stato accettato!</h3>
                <p><strong>Azienda:</strong> {farmer.company_name or farmer.username}</p>
                <p><strong>Totale:</strong> {order.total_price:.2f} €</p>
                <p>L'azienda ti contatterà a breve per i dettagli.</p>
            """)
        except Exception:
            pass
    flash('Ordine accettato', 'success')
    return redirect(request.referrer or url_for('profiles.my_orders'))

@cart.route('/orders/reject/<int:order_id>', methods=['POST'])
@login_required
def reject_order(order_id):
    order = OrderRequest.query.get_or_404(order_id)
    if current_user.id != order.farmer_id:
        flash('Non autorizzato', 'danger')
        return redirect(url_for('profiles.view_profile', username=current_user.username))
    order.status = 'rejected'
    db.session.commit()
    # Send rejection email to client
    if order.client_email:
        try:
            farmer = User.query.get(order.farmer_id)
            send_email(order.client_email, "Ordine non disponibile", f"""
                <h3>Ordine non accettato</h3>
                <p><strong>Azienda:</strong> {farmer.company_name or farmer.username}</p>
                <p>Ci dispiace, l'ordine non può essere evaso al momento. Prova a contattare direttamente l'azienda.</p>
            """)
        except Exception:
            pass
    flash('Ordine rifiutato', 'info')
    return redirect(request.referrer or url_for('profiles.my_orders'))
