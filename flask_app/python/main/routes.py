from flask import current_app, Blueprint, render_template, send_from_directory, jsonify, request, session, abort

from flask_jwt_extended import jwt_required
from flask_jwt_extended import unset_jwt_cookies

from flask_login import current_user
from flask_app.python.users.utils import customer_status, get_user
from flask_app.python.main.utils import send_email_html, post_request_to_api
from flask_app.python.users.decorators import token_required, get_logged_user

from google.cloud import storage

import os
import pathlib
import requests

main = Blueprint('main', __name__)


#@main.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(current_app.root_path, 'static/imgs/views'),
#                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@main.route('/', methods=['GET', 'POST'])
@get_logged_user
def index():
    return render_template('index.html', title='Crie posts de maneira rápida e prática', current_user = session['current_user'])


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        dic = {'name': '', 'email': '', 'subject': '', 'message': ''}
        for d in data:
            if d['name'] == 'Name':
                dic['name'] = d['value']
            elif d['name'] == 'Email':
                dic['email'] = d['value']
            elif d['name'] == 'Subject':
                dic['subject'] = d['value']
            elif d['name'] == 'message':
                dic['message'] = d['value']
        for email in [current_app.config['MAIL_USERNAME'], dic['email']]:
            send_email_html(
                email=email,
                title="Ticket: " + dic["subject"],
                template=render_template(
                    'email_contact_form.html',
                    title="Contact Form",
                    form_contact=dic
                )
            )
    return (jsonify(data))


@main.route('/email_test')
def email_test():
    customer_info = customer_status(current_user.id)
    return render_template('email_reactivesub.html', title='Registro', customer_info=customer_info)


@main.route('/storage/<path:varargs>', methods=['GET'])
def download_file(varargs):
    path = pathlib.Path(varargs)
    if path.parts[0] == 'storage':
        path = pathlib.Path(*path.parts[1:])
    user_storage = path.parts[0]
    aux = user_storage.split('user_')
    if len(aux) == 2:
        user_id = int(aux[-1])
        if current_user.id == user_id:
            path_str = '/'.join(path.parts)
            storage_path = f'storage/{path_str}'
            filename = os.path.basename(storage_path)
            local_path = os.path.join(current_app.root_path, storage_path)
            local_dirname = os.path.dirname(local_path)
            if os.path.isfile(local_path) is False:
                os.makedirs(local_dirname, exist_ok=True)
                storage_client = storage.Client(project='rapiartapp')
                bucket = storage_client.get_bucket('rapiart_bucket')
                blob = bucket.blob(storage_path)
                blob.download_to_filename(local_path)
            return send_from_directory(local_dirname, filename, as_attachment=True)
    return render_template('errors/404.html', title='Erro 404')

@main.route('/layout_test')
def layout_test():
    #customer_info = customer_status(current_user.id)
    return render_template('layout_test.html', title='layout_test')#, customer_info=customer_info)

@main.route('/test')
def test():
    #customer_info = customer_status(current_user.id)
    return render_template('test.html', title='Test')#, customer_info=customer_info)

@main.route('/politica_de_privacidade')
def politica_de_privacidade():
    return render_template('terms_privacidade.html', title='Política de privacidade')

@main.route('/termos_de_servico')
def termos_de_servico():
    return render_template('terms_service.html', title='Termos de serviço')

@main.route('/get_token')
def jwt_test():
    data = post_request_to_api('auth/login', json = {
            "email": "gabriel2@gmail.com",
            "password": "cebola2" 
        }
    )
    if data["status"]=="Success":
        response = jsonify(data)
        response.set_cookie(f'acto={data["access_token"]}', httponly = True)
        response.set_cookie(f'reto={data["refresh_token"]}', httponly = True)
        session['access_token'] = data["access_token"]
        session['refresh_token'] = data["refresh_token"]
        return (response)
    else:
        response = jsonify(data)
        response.set_cookie(f'acto=""', httponly = True)
        response.set_cookie(f'reto=""', httponly = True)
        session.pop('access_token', None)
        session.pop('refresh_token', None)
        return (response)
    return jsonify(data), 302

@main.route('/protected')
@token_required
def protected():
    logged_user = get_user(access_token=session['access_token'])
    return jsonify(logged_user)


@main.route('/reset_pass_token')
def reset_pass_token():
    json = {
        "email": "gabrie@gmail.com"
    }
    response = post_request_to_api('auth/reset-password-request', json=json)
    return jsonify(response)


@main.route('/reset_pass')
def reset_pass():
    json = {
        "reset_password_token": "eyJhbGciOiJIUzUxMiIsImlhdCI6MTYxOTQ1MzQ3MCwiZXhwIjoxNjE5NDU1MjcwfQ.eyJ1c2VyX2lkIjo0fQ.M0mu9LzueYgfzJksCokJcsETp7dXtx8I7SBN2Q7jplrOtKKr2lNQkBuEdaC3aTCTkdi610D2yuayW2Ix7HJO3w",
        "new_password": "cebola"
    }
    response = post_request_to_api('auth/reset-password', json=json)
    return jsonify(response)

@main.route('/register_new_user')
def register_new_user():
    json = {
        "email": "mariana2@gmail.com",
        "password": "1234",
        "name": "Mariana Pontes"
    }
    data = post_request_to_api('auth/register', json=json)
    if 'access_token' in data.keys():
        response = jsonify(data)
        response.set_cookie(f'acto={data["access_token"]}', httponly = True)
        response.set_cookie(f'reto={data["refresh_token"]}', httponly = True)
        session['access_token'] = data["access_token"]
        session['refresh_token'] = data["refresh_token"]
        return response
    return jsonify(response)


@main.route('/change_pass')
def change_pass():
    json = {
        "old_password": "cebola",
        "password": "cebola2"
    }
    response = post_request_to_api('auth/change-password', access_token=session['access_token'], json=json)
    return jsonify(response)