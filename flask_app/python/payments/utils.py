from flask import current_app
from flask_app import db
from flask_app.python.models import User
from flask_app.python.users.utils import customer_status, is_customer_by_sub_id, change_to_no_customer

import stripe


def get_product_info(stripe_id, prod_id):
    price_json = stripe.Price.retrieve(stripe_id)
    prod_json = stripe.Product.retrieve(prod_id)

    product_info = {
        'price': price_json['unit_amount']/100,
        'type': price_json['type'],
        'price_status': price_json['active'],
        'product_status': prod_json['active'],
        #'artes_number': prod_json['metadata']['artes'],
        #'telas_number': prod_json['metadata']['telas'],
        'trial_period': prod_json['metadata']['trial_period'],
        'name': prod_json['name'],
        'description': prod_json['description'],
        'prod_id': prod_id,
        'stripe_id': stripe_id
    }
    return(product_info)


def checkout_done(session):
    status = is_customer_by_sub_id(session['subscription'])
    if status == 'active' or status == 'trialing':
        user = User.query.filter_by(id=int(session['metadata']['user_id'])).first()
        user.permission = current_app.config['ACCESS_CONTROL']['customer']
        user.customer_id = session['customer']
        user.subscription_id = session['subscription']

        #subscription = stripe.Subscription.retrieve(session['subscription'])
        #user.artes_restantes = stripe.Product.retrieve(subscription['plan']['product'])['metadata']['artes']
        #user.telas_restantes = stripe.Product.retrieve(subscription['plan']['product'])['metadata']['telas']

        db.session.commit()


def deleted_subscription_webhook_signal(session):
    customer = User.query.filter_by(subscription_id=session['id']).first()
    if customer:
        change_to_no_customer(user_id=customer.id)


def cancel_subscription_at_stripe(id):
    user = User.query.filter_by(id=id).first()
    if user.subscription_id is None:
        return(None)
    else:
        stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=True
        )
        customer_info = customer_status(id)
        if customer_info['cancel_at_period_end'] is True:
            return(customer_info)
        else:
            return(False)


def reactivate_subscription_at_stripe(id):
    user = User.query.filter_by(id=id).first()
    if user.subscription_id is None:
        return(None)
    else:
        stripe.Subscription.modify(
            user.subscription_id,
            cancel_at_period_end=False
        )
        customer_info = customer_status(id)
        if customer_info['cancel_at_period_end'] is False:
            return(customer_info)
        else:
            return(False)


def update_subscription_webhook_signal(session):
    subscription = stripe.Subscription.retrieve(session['id'])
    if subscription['status'] == 'active' or subscription['status'] == 'trialing':
        user = User.query.filter_by(customer_id=session['customer']).first()
        #user.artes_restantes = stripe.Product.retrieve(subscription['plan']['product'])['metadata']['artes']
        #user.telas_restantes = stripe.Product.retrieve(subscription['plan']['product'])['metadata']['telas']
        db.session.commit()
