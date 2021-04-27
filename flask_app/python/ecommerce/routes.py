from flask import Blueprint, current_app, request
from flask_login import current_user
from flask_app import db
from flask_app.python.ecommerce.utils import woo_check_data, woo_object

ecommerce = Blueprint('ecommerce', __name__)


@ecommerce.route('/check_key', methods=["GET", "POST"])
def check_key():
    if request.method == 'POST':
        post = request.get_json()

        if post['platform'] == 'woocommerce':
            response = woo_check_data(post)
            return (response)


@ecommerce.route('/save_key', methods=["GET", "POST"])
def save_key():
    if request.method == 'POST':
        post = request.get_json()

        if post['platform'] == 'woocommerce':
            response = woo_check_data(post)
            if response['status'] == 'success':
                current_user.woo_secret = current_app.config["cript"].encrypt(post['secret'].encode('utf-8')).decode('utf-8')
                current_user.woo_key = post['key']
                current_user.woo_store_url = post['store_url']
                current_user.woo_active = True
                db.session.commit()
                return(response)
            else:
                current_user.woo_active = False
                db.session.commit()
                return(response)


@ecommerce.route('/get_key', methods=["GET", "POST"])
def get_key():
    if request.method == 'POST':
        post = request.get_json()

        if post['platform'] == 'woocommerce' and current_user.woo_active == True:
            return({
                'secret': current_app.config["cript"].decrypt(current_user.woo_secret.encode('utf-8')).decode('utf-8'),
                'key': current_user.woo_key,
                'store_url': current_user.woo_store_url
            })
        else:
            return({'status': 'error', 'error_number': 1001, 'error': 'Nenhuma plataforma encontrada'})