from flask import current_app
from flask_app import mail
from flask_mail import Message

from google.cloud import secretmanager
import requests


def get_request_to_api(route, access_token=None, refresh_token=None):
    if access_token:
        data = requests.get(f'{current_app.config["API_DOMAIN"]}/{route}',
            headers = {'Authorization': f'Bearer {access_token}'},
        )
    elif refresh_token:
        data = requests.get(f'{current_app.config["API_DOMAIN"]}/{route}',
            headers = {'Authorization': f'Bearer {refresh_token}'},
        )
    else:
        data = requests.get(f'{current_app.config["API_DOMAIN"]}/{route}')
    return (data.json())


def post_request_to_api(route, access_token=None, refresh_token=None, json={}):
    if access_token:
        data = requests.post(f'{current_app.config["API_DOMAIN"]}/{route}',
            headers = {'Authorization': f'Bearer {access_token}'},
            json=json,
        )
    elif refresh_token:
        data = requests.post(f'{current_app.config["API_DOMAIN"]}/{route}',
            headers = {'Authorization': f'Bearer {refresh_token}'},
            json=json,
        )
    else:
        data = requests.post(f'{current_app.config["API_DOMAIN"]}/{route}',
            json=json,
        )
    return (data.json())


def send_email(email, title, message):
    msg = Message(
        title,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = message
    mail.send(msg)


def send_email_html(email, title, template):
    msg = Message(
        title,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.html = template
    mail.send(msg)


def access_secret_version(secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/rapiartapp/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')
