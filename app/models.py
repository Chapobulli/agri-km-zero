from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import re

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_farmer = db.Column(db.Boolean, default=False)
    premium = db.Column(db.Boolean, default=False)  # for freemium
    display_name = db.Column(db.String(150))  # Nome visualizzato pubblicamente
    # Location fields
    province = db.Column(db.String(100))  # Provincia (es. Oristano)
    city = db.Column(db.String(100))  # Comune (es. Cabras)
    address = db.Column(db.String(300))  # Indirizzo specifico
    latitude = db.Column(db.Float)  # Keep for map display
    longitude = db.Column(db.Float)  # Keep for map display
    delivery = db.Column(db.Boolean, default=False)  # if farmer offers delivery
    # Profile fields (client)
    bio = db.Column(db.Text)
    profile_photo = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    # Company page fields (farmer)
    company_name = db.Column(db.String(200))
    company_description = db.Column(db.Text)
    company_logo = db.Column(db.String(300))
    company_cover = db.Column(db.String(300))
    company_slug = db.Column(db.String(200))
    # Email verification and password reset
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    reset_token = db.Column(db.String(100))

    products = db.relationship('Product', backref='farmer', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        return self.reset_token

    def compute_company_slug(self):
        base = self.company_name or self.username or f"user-{self.id}"
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', base).strip('-').lower()
        return slug or f"azienda-{self.id}"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    unit = db.Column(db.String(20))  # 'kg', 'pezzo', 'cassetta'
    image_path = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)

class OrderRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    client_name = db.Column(db.String(150))
    client_email = db.Column(db.String(150))
    client_phone = db.Column(db.String(50))
    delivery_address = db.Column(db.String(300))
    delivery_requested = db.Column(db.Boolean, default=False)
    items_json = db.Column(db.Text, nullable=False)  # JSON of items in cart
    total_price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending|accepted|rejected
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())