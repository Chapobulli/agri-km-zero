from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Message, User
from .forms import MessageForm
from sqlalchemy import or_, and_

messages = Blueprint('messages', __name__)

@messages.route('/messages')
@login_required
def inbox():
    """Mostra tutte le conversazioni dell'utente"""
    # Get all users with whom current_user has exchanged messages
    conversations_query = db.session.query(User).join(
        Message,
        or_(
            and_(Message.sender_id == User.id, Message.recipient_id == current_user.id),
            and_(Message.recipient_id == User.id, Message.sender_id == current_user.id)
        )
    ).filter(User.id != current_user.id).distinct()
    
    conversation_users = conversations_query.all()
    
    # For each user, get the last message and unread count
    conversations = []
    for user in conversation_users:
        last_message = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.recipient_id == user.id),
                and_(Message.sender_id == user.id, Message.recipient_id == current_user.id)
            )
        ).order_by(Message.timestamp.desc()).first()
        
        unread_count = Message.query.filter_by(
            sender_id=user.id,
            recipient_id=current_user.id,
            read=False
        ).count()
        
        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Sort by last message timestamp
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else 0, reverse=True)
    
    return render_template('inbox.html', conversations=conversations)

@messages.route('/conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    """Mostra conversazione con un utente specifico"""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('⚠ Non puoi inviare messaggi a te stesso', 'warning')
        return redirect(url_for('messages.inbox'))
    
    # Mark all messages from other_user as read
    Message.query.filter_by(
        sender_id=other_user.id,
        recipient_id=current_user.id,
        read=False
    ).update({'read': True})
    db.session.commit()
    
    # Get all messages between the two users
    conversation_messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == other_user.id),
            and_(Message.sender_id == other_user.id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            recipient_id=other_user.id
        )
        db.session.add(message)
        db.session.commit()
        flash('✓ Messaggio inviato', 'success')
        return redirect(url_for('messages.conversation', user_id=other_user.id))
    
    return render_template('conversation.html', other_user=other_user, messages=conversation_messages, form=form)

@messages.route('/send_message/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    """Redirect to conversation"""
    return redirect(url_for('messages.conversation', user_id=user_id))