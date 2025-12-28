from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Review, User, OrderRequest

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/submit-review/<int:farmer_id>', methods=['POST'])
@login_required
def submit_review(farmer_id):
    """Ricevi una recensione per un'azienda agricola (solo utenti autenticati)"""
    try:
        rating_str = request.form.get('rating', '').strip()
        
        # Validate rating
        if not rating_str:
            return jsonify({'success': False, 'message': 'Seleziona un punteggio con le stelle'}), 400
        
        try:
            rating = int(rating_str)
        except ValueError:
            return jsonify({'success': False, 'message': 'Valutazione non valida'}), 400
        
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Valutazione deve essere tra 1 e 5 stelle'}), 400
        
        comment = request.form.get('comment', '').strip()
        order_id_str = request.form.get('order_id')
        
        # Verifica che l'azienda esista
        farmer = User.query.get(farmer_id)
        if not farmer or not farmer.is_farmer:
            return jsonify({'success': False, 'message': 'Azienda non trovata'}), 404
        
        # Valida che sia fornito un order_id
        if not order_id_str:
            return jsonify({'success': False, 'message': 'ID ordine mancante'}), 400
        
        try:
            order_id = int(order_id_str)
        except ValueError:
            return jsonify({'success': False, 'message': 'ID ordine non valido'}), 400
        
        # Verifica che l'ordine esista e appartenga all'utente corrente
        order = OrderRequest.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Ordine non trovato'}), 404
        
        if order.client_id != current_user.id:
            return jsonify({'success': False, 'message': 'Non sei autorizzato a recensire questo ordine'}), 403
        
        # Verifica che l'ordine sia completato
        if order.status != 'completed':
            return jsonify({'success': False, 'message': 'Puoi recensire solo ordini completati'}), 400
        
        # Verifica che l'ordine non sia già stato recensito
        if order.reviewed:
            return jsonify({'success': False, 'message': 'Hai già recensito questo ordine'}), 400
        
        # Crea la recensione
        review = Review(
            farmer_id=farmer_id,
            client_id=current_user.id,
            client_name=current_user.username,
            order_id=order_id,
            rating=rating,
            comment=comment if comment else None
        )
        
        # Contrassegna l'ordine come recensito
        order.reviewed = True
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Grazie per la tua recensione!',
            'rating': rating
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Errore: {str(e)}'}), 500

@reviews_bp.route('/farmer/<int:farmer_id>/reviews')
def get_farmer_reviews(farmer_id):
    """Ottieni tutte le recensioni di un'azienda"""
    reviews = Review.query.filter_by(farmer_id=farmer_id).order_by(Review.created_at.desc()).all()
    
    # Calcola media stelle
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    reviews_data = [{
        'id': r.id,
        'client_name': r.client_name,
        'rating': r.rating,
        'comment': r.comment,
        'created_at': r.created_at.strftime('%d/%m/%Y')
    } for r in reviews]
    
    return jsonify({
        'reviews': reviews_data,
        'total': len(reviews),
        'avg_rating': round(avg_rating, 1)
    })
