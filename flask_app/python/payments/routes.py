from flask import Blueprint, current_app, jsonify, render_template, url_for, redirect, request
from flask_login import current_user, login_required
from flask_app.python.users.utils import customer_status
from flask_app.python.users.decorators import customers_only, no_customers_only
from flask_app.python.main.utils import send_email_html
from flask_app.python.payments.utils import (
    checkout_done, deleted_subscription_webhook_signal,
    cancel_subscription_at_stripe, reactivate_subscription_at_stripe,
    get_product_info, update_subscription_webhook_signal
)
import stripe

payments = Blueprint('payments', __name__)


@payments.route("/subscribe")
@login_required
@no_customers_only
def subscribe():
    prods_info = []
    for plano in current_app.config['PLANS_DICT']:
        prods_info.append(
            get_product_info(
                prod_id=current_app.config['PLANS_DICT']['prod_id'],
                stripe_id=current_app.config['PLANS_DICT']['stripe_id']
                )
            )
    customer_info = customer_status(current_user.id)
    return render_template("subscribe.html", title='Assinar plano', prods_info=prods_info, customer_info=customer_info)


@payments.route("/cancel_subscription")
@login_required
@customers_only
def cancel_subscription():
    customer_info = customer_status(current_user.id)
    return render_template("cancel_subscription.html", title='Cancelar assinatura', customer_info=customer_info)


@payments.route("/cancel_subscription_action", methods=['GET', 'POST'])
@login_required
@customers_only
def cancel_subscription_action():
    if request.method == 'GET':
        customer_info = cancel_subscription_at_stripe(current_user.id)
        send_email_html(
            email=current_user.email,
            title='Assinatura Cancelada',
            template=render_template(
                'email_cancelsub.html',
                title="Cancelar Assinatura",
                customer_info=customer_info
            )
        )
    return redirect(url_for("users.account", _anchor="assinatura"))


@payments.route("/reactivate_subscription", methods=['GET', 'POST'])
@login_required
@customers_only
def reactivate_subscription():
    if request.method == 'GET':
        customer_info = reactivate_subscription_at_stripe(current_user.id)
        send_email_html(
            email=current_user.email,
            title='Assinatura Reativada',
            template=render_template(
                'email_reactivesub.html',
                title="Reativar Assinatura",
                customer_info=customer_info
            )
        )
    return redirect(url_for("users.account", _anchor="assinatura"))


@payments.route("/config")
@login_required
def get_publishable_key():
    stripe_config = {
        "publicKey": current_app.config['STRIPE_KEYS']['PUBLISHABLE_KEY'],
        "prod_id": current_app.config['PLANS_DICT']['prod_id'],
        "stripe_id": current_app.config['PLANS_DICT']['stripe_id']
    }
    return jsonify(stripe_config)


@payments.route('/customer-portal', methods=['GET', 'POST'])
@login_required
def customer_portal():
    session = stripe.billing_portal.Session.create(
        customer=current_user.customer_id,
        return_url=url_for('users.account', _external=True),
    )
    return redirect(session.url)


@payments.route("/create-checkout-session", methods=['GET', 'POST'])
@login_required
def create_checkout_session():
    price_id = request.args.get('price_id')
    prod_id = request.args.get('prod_id')

    product = stripe.Product.retrieve(prod_id)
    customer_info = customer_status(current_user.id)
    if customer_info=="No customer":
        customer_id = None
    else:
        customer_id = current_user.customer_id
    
    subscription_id = current_user.subscription_id
    if (subscription_id == None) or (subscription_id == "No subscription"):
        subscription_data = {'trial_period_days': product['metadata']['trial_period']}
    else:
        subscription_data = {}

    try:
        print('creating checkout')
        checkout_session = stripe.checkout.Session.create(
            success_url=url_for('payments.payment_done', _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for('payments.subscribe', _external=True),
            payment_method_types=["card"],
            customer=customer_id,
            mode="subscription",
            allow_promotion_codes=True,
            subscription_data=subscription_data,
            line_items=[
                {
                "description": product['description'],
                "price": price_id,
                "quantity": '1'
                }
            ],
            metadata={
                'user_id': current_user.id
            }
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        print('Error:', e)
        return jsonify(error=str(e)), 403


@payments.route("/payment_done")
@login_required
def payment_done():
    try:
        session_id = request.args.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        checkout_done(session)
        customer_info = customer_status(current_user.id)
        if customer_info is None:
            return redirect(url_for('payments.subscribe'))

        send_email_html(
            email=current_user.email,
            title='Assinatura Confirmada',
            template=render_template(
                'email_checkout.html',
                title="Checkout",
                customer_info=customer_info
            )
        )
        return render_template('payment_done.html', title='Pagamento confirmado', customer_info=customer_info)
    except:
        return redirect(url_for('users.account'))


### WEBHOOK
@payments.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, current_app.config['STRIPE_KEYS']['ENDPOINT_KEY'])

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        checkout_done(session)

    if event["type"] == "customer.subscription.deleted":
        session = event["data"]["object"]
        deleted_subscription_webhook_signal(session)

    if event["type"] == "customer.subscription.updated":
        session = event["data"]["object"]
        update_subscription_webhook_signal(session)

    print(event["type"])
    return "Success", 200
