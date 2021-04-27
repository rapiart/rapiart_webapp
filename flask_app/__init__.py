from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
#from flask_talisman import Talisman

from cryptography.fernet import Fernet
import stripe


####### RESTART DB? #######
RESTART_DB = False
###########################

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()
jwt = JWTManager()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Por favor, faça login para acessar essa página'


def single_yes_or_no_question(question, default_no=True):
    choices = ' [y/N]: ' if default_no else ' [Y/n]: '
    default_answer = 'n' if default_no else 'y'
    reply = str(input(question + choices)).lower().strip() or default_answer
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return False if default_no else True


def create_app(config_class):
    app = Flask(__name__)

    print(f"STARTING CONFIG MODE: {config_class.MODE}")
    app.config.from_object(config_class)

    stripe.api_key = app.config['STRIPE_KEYS']['SECRET_KEY']
    app.config["cript"] = Fernet(app.config['CRIPTO_KEY'])

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

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

    # Talisman(
    #     app,
    #     content_security_policy=[]
    # )

    print("\nRestart DB set to:", RESTART_DB, '\n')
    ### Populando DB para os testes ###
    if RESTART_DB is True:
        if single_yes_or_no_question('Quer mesmo restaurar o banco de dados?'):
            from flask_app.python.artes_e_telas.utils import populate_db
            with app.app_context():
                populate_db()
            print("Banco de dados restaurado. \n")
        else:
            print("Banco de dados não restaurado. \n")
    #####################

    return app
