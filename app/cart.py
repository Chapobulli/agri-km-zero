from flask import Blueprint, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from . import db
from .models import Product, Message, User, OrderRequest
from .email_utils import send_email
from urllib.parse import quote
import json

cart = Blueprint('cart', __name__)

def _get_cart():
    return session.setdefault('cart', {})

def _save_session():
    session.modified = True


def _profile_url_for_farmer(farmer):
    if farmer.is_farmer:
        slug = farmer.company_slug or farmer.compute_company_slug()
        return url_for('profiles.view_company', slug=slug)
    return url_for('profiles.view_profile', username=farmer.username)

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
    return redirect(_profile_url_for_farmer(farmer))

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
    return redirect(_profile_url_for_farmer(farmer))

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
    return redirect(_profile_url_for_farmer(farmer))


@cart.route('/cart/whatsapp/<int:farmer_id>', methods=['GET', 'POST'])
def whatsapp_order(farmer_id):
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id))
    farmer = User.query.get_or_404(farmer_id)
    if not farmer_cart:
        flash('Il carrello è vuoto', 'warning')
        return redirect(_profile_url_for_farmer(farmer))
    if not farmer.phone:
        flash('Questo venditore non ha ancora aggiunto un numero WhatsApp', 'warning')
        return redirect(_profile_url_for_farmer(farmer))
    # Prefer data from submitted form (guests) and fallback to logged user data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone_client = request.form.get('phone', '').strip()
    delivery = request.form.get('delivery', 'off') in ['on', 'true', '1']
    address = request.form.get('address', '').strip()

    lines = [f"Ordine per {farmer.company_name or farmer.username}"]
    total = 0.0
    for _, item in farmer_cart.items():
        subtotal = float(item['price']) * int(item['qty'])
        total += subtotal
        lines.append(f"- {item['name']} x{item['qty']} {item['unit']} → {subtotal:.2f} €")
    lines.append(f"Totale: {total:.2f} €")
    if getattr(current_user, 'is_authenticated', False):
        lines.append(f"Cliente: {current_user.display_name or current_user.username}")
        if current_user.email:
            lines.append(f"Email: {current_user.email}")
        if current_user.address:
            lines.append(f"Indirizzo: {current_user.address}")
        if current_user.phone:
            lines.append(f"Telefono: {current_user.phone}")
    else:
        lines.append(f"Cliente: {name or 'ospite'}")
        if email:
            lines.append(f"Email: {email}")
        if phone_client:
            lines.append(f"Telefono: {phone_client}")
        if delivery and address:
            lines.append(f"Consegna: {address}")
    # Sanitize phone (strip spaces/+)
    phone_digits = ''.join(ch for ch in farmer.phone if ch.isdigit() or ch == '+')
    if phone_digits.startswith('00'):
        phone_digits = phone_digits[2:]
    if phone_digits.startswith('+'):
        phone_digits = phone_digits[1:]
    whatsapp_text = quote("\n".join(lines))
    return redirect(f"https://wa.me/{phone_digits}?text={whatsapp_text}")

@cart.route('/orders/create/<int:farmer_id>', methods=['POST'])
def create_order(farmer_id):
    # Allow guests to place orders: collect contact info
    c = _get_cart()
    farmer_cart = c.get(str(farmer_id))
    if not farmer_cart:
        flash('Il carrello è vuoto', 'warning')
        farmer = User.query.get_or_404(farmer_id)
        return redirect(_profile_url_for_farmer(farmer))
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
    is_auth = hasattr(current_user, 'is_authenticated') and current_user.is_authenticated
    order = OrderRequest(
        farmer_id=farmer_id,
        client_id=current_user.id if is_auth else None,
        client_name=name or (current_user.display_name or current_user.username if is_auth else None),
        client_email=email,
        client_phone=phone,
        delivery_address=address if delivery else None,
        delivery_requested=delivery,
        items_json=json.dumps(farmer_cart),
        total_price=total,
        status='pending'
    )
    db.session.add(order)
    # Retry logic for intermittent SSL errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.session.commit()
            break
        except Exception as e:
            db.session.rollback()
            if attempt == max_retries - 1:
                flash('Errore temporaneo nel salvare l\'ordine. Riprova tra poco.', 'danger')
                farmer = User.query.get_or_404(farmer_id)
                return redirect(url_for('profiles.view_profile', username=farmer.username))
            import time
            time.sleep(0.5 * (attempt + 1))

    # If l'utente è registrato, invia anche un messaggio privato al venditore
    if order.client_id:
        try:
            lines = [f"Nuovo ordine da {order.client_name or 'Cliente'}"]
            for _, item in farmer_cart.items():
                lines.append(f"- {item['name']} x{item['qty']} {item['unit']}")
            lines.append(f"Totale: {order.total_price:.2f} €")
            if order.delivery_requested and order.delivery_address:
                lines.append(f"Consegna: {order.delivery_address}")
            if order.client_phone:
                lines.append(f"Telefono: {order.client_phone}")
            if order.client_email:
                lines.append(f"Email: {order.client_email}")
            msg = Message(content="\n".join(lines), sender_id=order.client_id, recipient_id=farmer_id)
            db.session.add(msg)
            db.session.commit()
        except Exception:
            db.session.rollback()
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
            client_items = []
            for _, item in farmer_cart.items():
                client_items.append(f"<li><strong>{item['name']}</strong> x{item['qty']} {item['unit']} — {float(item['price'])*int(item['qty']):.2f} €</li>")
            send_email(order.client_email, "Conferma ordine inviato", f"""
                <h3>Ordine inviato a {farmer.company_name or farmer.username}</h3>
                <p><strong>Dettaglio ordine:</strong></p>
                <ul>{''.join(client_items)}</ul>
                <p><strong>Totale:</strong> {order.total_price:.2f} €</p>
                {'<p><strong>Consegna richiesta a:</strong> ' + (order.delivery_address or '') + '</p>' if order.delivery_requested else '<p><strong>Ritiro presso azienda</strong></p>'}
                <p>Riceverai conferma dall'azienda appena l'ordine verrà accettato.</p>
            """)
    except Exception:
        pass
    # Clear cart after creating order
    c.pop(str(farmer_id), None)
    _save_session()
    flash('Ordine inviato: l\'azienda riceverà i dettagli e ti contatterà', 'success')
    if is_auth:
        return redirect(url_for('profiles.my_client_orders'))
    return redirect(_profile_url_for_farmer(farmer))

@cart.route('/orders/accept/<int:order_id>', methods=['POST'])
@login_required
def accept_order(order_id):
    order = OrderRequest.query.get_or_404(order_id)
    if current_user.id != order.farmer_id:
        flash('Non autorizzato', 'danger')
        return redirect(url_for('profiles.view_profile', username=current_user.username))
    order.status = 'accepted'
    db.session.commit()
    # Send in-app message if client is registered
    if order.client_id:
        try:
            msg = Message(
                content=f"Il tuo ordine #{order.id} è stato accettato! L'azienda ti contatterà a breve per i dettagli.",
                sender_id=current_user.id,
                recipient_id=order.client_id
            )
            db.session.add(msg)
            db.session.commit()
        except Exception:
            pass
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
    # Send in-app message if client is registered
    if order.client_id:
        try:
            msg = Message(
                content=f"Il tuo ordine #{order.id} non può essere evaso al momento. Contatta l'azienda per maggiori informazioni.",
                sender_id=current_user.id,
                recipient_id=order.client_id
            )
            db.session.add(msg)
            db.session.commit()
        except Exception:
            pass
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


@cart.route('/orders/bulk', methods=['POST'])
@login_required
def bulk_update_orders():
    if not current_user.is_farmer:
        flash('Solo gli agricoltori possono gestire gli ordini', 'warning')
        return redirect(url_for('main.index'))

    order_ids = request.form.getlist('order_ids')
    action = request.form.get('action')

    if not order_ids:
        flash('Seleziona almeno un ordine', 'warning')
        return redirect(request.referrer or url_for('profiles.my_orders'))

    valid_actions = {'accept': 'accepted', 'reject': 'rejected'}
    if action not in valid_actions:
        flash('Azione non valida', 'danger')
        return redirect(request.referrer or url_for('profiles.my_orders'))

    orders = OrderRequest.query.filter(
        OrderRequest.id.in_(order_ids),
        OrderRequest.farmer_id == current_user.id,
        OrderRequest.status == 'pending'
    ).all()

    for order in orders:
        order.status = valid_actions[action]
        if order.client_email:
            try:
                status_subject = "Ordine accettato" if action == 'accept' else "Ordine non accettato"
                status_body = "Il tuo ordine è stato accettato!" if action == 'accept' else "L'ordine non può essere evaso al momento."
                send_email(order.client_email, status_subject, f"""
                    <h3>{status_body}</h3>
                    <p><strong>Azienda:</strong> {current_user.company_name or current_user.username}</p>
                    <p><strong>Totale:</strong> {order.total_price:.2f} €</p>
                """)
            except Exception:
                pass
    db.session.commit()
    flash(f"Aggiornati {len(orders)} ordini", 'success')
    return redirect(request.referrer or url_for('profiles.my_orders'))


@cart.route('/orders/reply/<int:order_id>', methods=['POST'])
@login_required
def reply_order(order_id):
    order = OrderRequest.query.get_or_404(order_id)
    if current_user.id != order.farmer_id:
        flash('Non autorizzato', 'danger')
        return redirect(url_for('main.index'))

    message_text = (request.form.get('message') or '').strip()
    if not message_text:
        flash('Il messaggio non può essere vuoto', 'warning')
        return redirect(request.referrer or url_for('profiles.my_orders'))

    # Prefer in-app messages se il cliente è registrato, altrimenti email
    if order.client_id:
        msg = Message(
            content=f"Risposta ordine #{order.id}: {message_text}",
            sender_id=current_user.id,
            recipient_id=order.client_id
        )
        db.session.add(msg)
        db.session.commit()
        flash('Risposta inviata al cliente', 'success')
    elif order.client_email:
        try:
            send_email(order.client_email, f"Risposta al tuo ordine #{order.id}", f"""
                <p><strong>{current_user.company_name or current_user.username}</strong> ha risposto al tuo ordine:</p>
                <blockquote>{message_text}</blockquote>
            """)
            flash('Risposta inviata via email al cliente', 'success')
        except Exception:
            flash('Impossibile inviare il messaggio', 'danger')
    else:
        flash('Mancano i contatti del cliente', 'warning')

    return redirect(request.referrer or url_for('profiles.my_orders'))
