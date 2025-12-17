import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import logging
from sqlalchemy import inspect, text
import cloudinary
import cloudinary.uploader

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///agri_km_zero.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

    # Aggiungi logging per debug
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .products import products as products_blueprint
    app.register_blueprint(products_blueprint)

    from .messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint)
    from .profiles import profiles as profiles_blueprint
    app.register_blueprint(profiles_blueprint)

    # Register custom filters
    from .template_filters import url_or_local
    app.jinja_env.filters['url_or_local'] = url_or_local

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('500.html'), 500

    try:
        with app.app_context():
            db.create_all()
            # Ensure schema columns exist for upgrades without migrations
            try:
                engine = db.engine
                insp = inspect(engine)
                # Use autocommit context for DDL (PostgreSQL)
                with engine.begin() as conn:
                    # User table columns
                    user_cols = {c['name'] if isinstance(c, dict) else c for c in insp.get_columns('user')}
                    additions_user = [
                        ('bio', 'TEXT'),
                        ('profile_photo', 'VARCHAR(300)'),
                        ('company_name', 'VARCHAR(200)'),
                        ('company_description', 'TEXT'),
                        ('company_logo', 'VARCHAR(300)'),
                        ('company_cover', 'VARCHAR(300)')
                    ]
                    for col_name, col_type in additions_user:
                        if col_name not in user_cols:
                            app.logger.info(f"Adding missing column user.{col_name}")
                            conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type}'))

                    # Product table columns
                    product_cols = {c['name'] if isinstance(c, dict) else c for c in insp.get_columns('product')}
                    additions_product = [
                        ('unit', 'VARCHAR(20)'),
                        ('image_path', 'VARCHAR(300)')
                    ]
                    for col_name, col_type in additions_product:
                        if col_name not in product_cols:
                            app.logger.info(f"Adding missing column product.{col_name}")
                            conn.execute(text(f'ALTER TABLE "product" ADD COLUMN {col_name} {col_type}'))
            except Exception as e:
                app.logger.warning(f"Schema ensure failed (may already be up-to-date): {e}")
            app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database: {e}")
        raise

    return app