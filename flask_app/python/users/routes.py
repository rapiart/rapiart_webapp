from flask import Blueprint, current_app, render_template, url_for, flash, redirect, request, jsonify, session, make_response

from flask_app.python.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, ChangePasswordForm
from flask_app.python.users.utils import  set_cookie_and_session
from flask_app.python.users.decorators import get_logged_user, token_required
from flask_app.python.main.utils import send_email_html, post_request_to_api, get_request_to_api

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

import random
import stripe
import requests

users = Blueprint('users', __name__)


@users.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template('register.html', title="Registrar", form=form)
    else:
        if form.validate_on_submit():
            json = {
                "email": form.email.data.lower(),
                "password": form.password.data,
                "name": form.username.data,
                "celular": form.celular.data,
                "cpf": form.cpf.data
            }
            data = post_request_to_api('auth/register', json=json)
            print(data)
            if data["status"] == "Success":
                response = set_cookie_and_session(
                    response=redirect(url_for('main.index')),
                    access_token=data["access_token"],
                    refresh_token=data["refres_token"],
                )
                flash('Sua conta foi criada com sucesso!', "success")
                return jsonify(response)
            else:
                return jsonify(data)
        return render_template('register.html', title="Registrar", form=form)

@users.route('/')
@users.route('/login', methods=["GET", "POST"])
@get_logged_user
def login():
    if session["current_user"]:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        data = requests.post(f'{current_app.config["API_DOMAIN"]}/auth/login',
            json = {
                "email": form.email.data.lower(),
                "password": form.password.data
            }
        ).json()
        if data["status"] == "Success":
            response = set_cookie_and_session(
                response=redirect(url_for('main.index')),
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
            )
            return response
        else:
            flash("Erro ao entrar. Verifique seu email e password", "danger")
    return render_template('login.html', title="Entrar", form=form, current_user=session['current_user'])


@users.route("/login-index", methods=['POST'])
def login_index():
    posts = request.get_json()
    for post in posts:
        if post['name'] == 'email':
            user_email = post['value'].lower()
        if post['name'] == 'password':
            password = post['value']
    json = {
        "email": user_email,
        "password": password,
    }
    data = post_request_to_api('auth/login', json=json)
    print(data)
    if data["status"] == "Success":
        response = set_cookie_and_session(
            response=data,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )
        return response
    else:
        return jsonify(data)


@users.route('/user_login_status', methods=['GET', 'POST'])
@get_logged_user
def user_login_status():
    if session['current_user']:
        return jsonify(session['current_user'])
    else:
        return jsonify({'status': 'None'})


@users.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie(f'acto=""', httponly = True)
    response.set_cookie(f'reto=""', httponly = True)
    return response


@users.route('/register-index', methods=["POST"])
def register_index():
    posts = request.get_json()
    for post in posts:
        if post['name'] == 'name':
            user_name = post['value']
        if post['name'] == 'email':
            user_email = post['value'].lower()
        if post['name'] == 'password':
            user_password = post['value']
    json = {
        "email": user_email,
        "password": user_password,
        "name": user_name,
    }
    data = post_request_to_api('auth/register', json=json)
    if data["status"] == "Success":
        response = set_cookie_and_session(
            response=data,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
        )
        flash('Sua conta foi criada com sucesso!', "success")
        return response
    else:
        return jsonify(data)


@users.route('/account', methods=["GET", "POST"])
@token_required
@get_logged_user
def account():
    current_user = session['current_user']
    if current_user:
        form = UpdateAccountForm(request.form)
        form2 = ChangePasswordForm(request.form)
        # Update dados form
        if form.submit.data and form.validate_on_submit():
            json = {
                "name": form.username.data,
                "celular": form.celular.data,
                "cpf": form.cpf.data
            }
            data = post_request_to_api('user-info', access_token=session["access_token"], json=json)
            if data["status"] == "Success":
                flash('Sua conta foi atualizada com sucesso.', 'success')
                return redirect(url_for('users.account'))
        # Update password form
        elif form2.submit2.data and form2.validate_on_submit():
            if form2.new_password.data == form2.confirm_new_password.data:
                json = {
                    "old_password": form2.old_password.data,
                    "password": form2.new_password.data
                }
                data = post_request_to_api('auth/change-password', access_token=session['access_token'], json=json)
                if data["status"] == "Success":
                    flash('Sua senha foi alterada com sucesso.', 'success')
                    return redirect(url_for('users.account'))
                else:
                    flash('Sua atual incorreta. Corrija e tente novamente', 'info')
                    return redirect(url_for('users.account'))
            else:
                flash('Confirmação de senha incorreta.', 'info')
                return redirect(url_for('users.account'))
        else:
            form.username.data = current_user["username"]
            form.email.data = current_user["email"]
            form.cpf.data = current_user["cpf"]
            form.celular.data = current_user["celular"]

        customer_info = get_request_to_api('customer', access_token=session["access_token"])
        print(customer_info)

        return render_template('account.html', title='Perfil de usuário', form=form, form2=form2, customer_info=customer_info, current_user=current_user)
    flash('Faça login para acessar essa página', 'info')
    return redirect(url_for('users.account'))


@users.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        json = {"email": form.email.data.lower()}
        data = post_request_to_api('auth/reset-password-request', json=json)
        if data["status"] == "Success":
            json = {
                "email": form.email.data.lower(),
                "token": data["reset_token"],
                "reset_url": url_for('users.reset_token', token=data["reset_token"], _external=True)
            }
            data = post_request_to_api('email/reset-password-request', json=json)
            flash('Um email com instruções para resetar sua senha foi enviado', 'info')
            return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Resetar Senha", form=form, current_user=session["current_user"])


@users.route('/reset_password-index', methods=["POST"])
def reset_request_index():
    posts = request.get_json()
    for post in posts:
        if post['name'] == 'email':
            user_email = post['value'].lower()
    json = {"email": user_email}
    data = post_request_to_api('auth/reset-password-request', json=json)
    if data["status"] == "Success":
        json = {
            "email": user_email,
            "token": data["reset_token"],
            "reset_url": url_for('users.reset_token', token=data["reset_token"], _external=True)
        }
        data = post_request_to_api('email/reset-password-request', json=json)
        return jsonify({'response': 'success'})
    return jsonify({'response': 'email_error'})


@users.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    json = {"token": token}
    data = post_request_to_api('/auth/check-reset-token', json=json)
    if data["status"] == "Error":
        flash("Esse link de recuperação de senha é inválido ou já experiou.", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        json = {
            "reset_password_token": token,
            "new_password": form.password.data
        }
        data2 = post_request_to_api('auth/reset-password', json=json)
        if data2["status"] == "Success":
            flash('Sua senha foi alterada com sucesso!', "success")
            return redirect(url_for("users.login"))
    return render_template('reset_token.html', title="Resetar Senha", form=form, current_user=session["current_user"])

