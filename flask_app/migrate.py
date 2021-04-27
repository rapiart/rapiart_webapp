from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

from cryptography.fernet import Fernet
import stripe

####### RESTART DB? #######
RESTART_DB = False
###########################

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, faça login para acessar essa página'

def create_app(config_class):
    app = Flask(__name__)

    from flask_app.python.main.utils import access_secret_version
    DATABASE_PASS = access_secret_version('database_password')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgres+psycopg2://postgres:{DATABASE_PASS}@130.211.229.204/rapiart_database"

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from flask_app.python.main.routes import main
    from flask_app.python.users.routes import users
    from flask_app.python.ecommerce.routes import ecommerce
    from flask_app.python.artes_e_telas.routes import artes_e_telas
    from flask_app.python.payments.routes import payments
    from flask_app.python.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(ecommerce)
    app.register_blueprint(artes_e_telas)
    app.register_blueprint(payments)
    app.register_blueprint(errors)

    from flask_app.python.users.routes import facebook_blueprint
    app.register_blueprint(facebook_blueprint)

    return app
