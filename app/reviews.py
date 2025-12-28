from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Review, User, OrderRequest

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/submit-review/<int:farmer_id>', methods=['POST'])
def submit_review(farmer_id):
    """Ricevi una recensione per un'azienda agricola"""
    try:
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()
        order_id = request.form.get('order_id')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Valutazione non valida'}), 400
        
        # Verifica che l'azienda esista
        farmer = User.query.get(farmer_id)
        if not farmer or not farmer.is_farmer:
            return jsonify({'success': False, 'message': 'Azienda non trovata'}), 404
        
        # Crea la recensione
        review = Review(
            farmer_id=farmer_id,
            client_id=current_user.id if current_user.is_authenticated else None,
            client_name=current_user.username if current_user.is_authenticated else request.form.get('client_name', 'Anonimo'),
            order_id=int(order_id) if order_id else None,
            rating=rating,
            comment=comment if comment else None
        )
        
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
