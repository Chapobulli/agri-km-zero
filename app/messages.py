from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import db
from .models import Message, User
from .forms import MessageForm

messages = Blueprint('messages', __name__)

@messages.route('/messages')
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).all()
    return render_template('inbox.html', messages=messages)

@messages.route('/send_message/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    recipient = User.query.get_or_404(user_id)
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(content=form.content.data, sender_id=current_user.id, recipient_id=user_id)
        db.session.add(message)
        db.session.commit()
        flash('Messaggio inviato!')
        return redirect(url_for('messages.inbox'))
    return render_template('send_message.html', form=form, recipient=recipient)