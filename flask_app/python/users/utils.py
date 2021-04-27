from flask import current_app, session, jsonify, make_response
from flask_app import db
from flask_app.python.models import User
from flask_app.python.main.utils import get_request_to_api, post_request_to_api

import stripe
from datetime import datetime
import random


def get_user(access_token):
        return get_request_to_api("user-info", access_token=access_token)

def get_seed():
    if session.get('seed') is None:
        session['seed'] = random.randint(0, 100)
    return session['seed']


def set_cookie_and_session(response, access_token=None, refresh_token=None):
    response = make_response(response)
    if access_token:
        session['access_token'] = access_token
        response.set_cookie(f'acto={access_token}', httponly = True)
    if refresh_token:
        session['refresh_token'] = refresh_token
        response.set_cookie(f'reto={refresh_token}', httponly = True)
    return response


def change_to_no_customer(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.permission = current_app.config['ACCESS_CONTROL']['no_customer']
    db.session.commit()


def change_to_customer(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.permission = current_app.config['ACCESS_CONTROL']['customer']
    db.session.commit()


def is_customer_by_sub_id(sub_id):
    status = stripe.Subscription.retrieve(sub_id)['status']
    return(status)


def is_customer_by_customer_id(customer_id):
    try:
        return stripe.Customer.retrieve(customer_id)
    except Exception as e:
        # if 'No such customer' in str(e):
        erro = {
            'error': 'No such customer',
            'customer_id': 'customer_id'
        }
        return(erro)


def customer_status(customer):
    check_customer = is_customer_by_customer_id(customer["customer_id"])
    if customer is None:
        return("No customer")
    elif ("deleted" in check_customer.keys()) or ('error' in check_customer.keys()):
        status = "No customer"
        if customer["customer_id"] != status:
            print("Undefined customer <"+customer.customer_id +
                  ">, changing id to <"+status+">")
        return(status)
    elif customer.subscription_id is None or customer.subscription_id == "No subscription":
        return("No subscription")
    else:
        stripe.api_key = current_app.config['STRIPE_KEYS']['SECRET_KEY']
        try:
            subscription = stripe.Subscription.retrieve(
                customer.subscription_id)
            subscription_info = {
                'status': subscription['status'],
                'start_date': datetime.fromtimestamp(int(subscription['start_date'])).strftime('%d/%m/%Y'),
                'current_period_start': datetime.fromtimestamp(int(subscription['current_period_start'])).strftime('%d/%m/%Y'),
                'current_period_end': datetime.fromtimestamp(int(subscription['current_period_end'])).strftime('%d/%m/%Y'),
                'customer': subscription['customer'],
                'subscription': customer.subscription_id,
                'plan': stripe.Product.retrieve(subscription['plan']['product'])['name'],
                'amount': subscription['items']['data'][0]['plan']['amount']/100,
                'cancel_at_period_end': subscription['cancel_at_period_end']
            }

            return(subscription_info)
        except Exception as e:
            return("No subscription")
