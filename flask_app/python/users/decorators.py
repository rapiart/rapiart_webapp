from flask import flash, current_app, redirect, url_for, request, abort, jsonify, make_response, session

from flask_login import current_user
from flask_app.python.models import User
from flask_app.python.users.utils import customer_status, change_to_no_customer, change_to_customer, get_user

from functools import wraps
import requests

def get_logged_user(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        if 'access_token' in session.keys():
            user = get_user(access_token=session['access_token'])
            if not "status" in user.keys():
                session['current_user'] = user
            else:
                session['current_user'] = None 
        else:
            session['current_user'] = None 
        return f(*args, **kwargs)
    return funcao_decorada   

def token_required(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        if "acto" in request.cookies.keys() and "reto" in request.cookies.keys():
            if request.cookies["acto"]!="" and request.cookies["reto"]!="":
                data = requests.get(f'{current_app.config["API_DOMAIN"]}/auth/token-check',
                headers = {
                        'Authorization': f'Bearer {request.cookies["acto"]}',
                    },
                ).json()
                print(data)
                if "expired" in data["msg"]:
                    print("\n\nSeu token expirou")
                    data = requests.post(f'{current_app.config["API_DOMAIN"]}/auth/token-refresh',
                        headers = {
                                'Authorization': f'Bearer {request.cookies["reto"]}',
                        },
                    ).json()
                    if "access_token" in data.keys():                     
                        print("Atulizando...\n\n")
                        session['access_token'] = data["access_token"]
                        response = make_response(f(*args, **kwargs))
                        response.set_cookie(f'acto={data["access_token"]}', httponly = True)
                        return response
                    else:
                        session['access_token'] = ""
                        session['refresh_token'] = ""
                        session['current_user'] = None
                        response = make_response(redirect(url_for('users.login')))
                        response.set_cookie(f'acto=""', httponly = True)
                        response.set_cookie(f'reto=""', httponly = True)
                        return response   
                elif "Success" in data["status"]:
                    pass
                else:
                    return redirect(url_for('users.login'))                       
            else:
                return redirect(url_for('users.login'))
        else:
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    return funcao_decorada   

def customers_only(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            user_access = user.permission
            if (user_access == current_app.config['ACCESS_CONTROL']['admin'] or
                user_access == current_app.config['ACCESS_CONTROL']['guest']):
                pass
            elif user_access == current_app.config['ACCESS_CONTROL']['customer']:
                if user.subscription_id:
                    customer_info = customer_status(current_user.id)
                    if customer_info == "No customer" or customer_info == "No subscription":
                        change_to_no_customer(user.id)
                    elif customer_info['status'] == 'canceled':
                        change_to_no_customer(user.id)
                    else:
                        pass
                else:
                    return redirect(url_for('payments.subscribe'))
            else:
                if user.subscription_id:
                    customer_info = customer_status(current_user.id)
                    if customer_info != "No customer" or customer_info != "No subscription":
                        if customer_info['status'] == 'trialing' or customer_info['status'] == 'active':
                            change_to_customer(user.id)
                        elif customer_info['status'] == 'canceled':
                            pass
                    else:
                        pass
                else:
                    return redirect(url_for('payments.subscribe'))
            return f(*args, **kwargs)
    return funcao_decorada

def no_customers_only(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        user = User.query.filter_by(id=current_user.id).first()
        user_access = user.permission
        if (user_access == current_app.config['ACCESS_CONTROL']['admin'] or
            user_access == current_app.config['ACCESS_CONTROL']['guest']):
            pass
        elif user_access == current_app.config['ACCESS_CONTROL']['no_customer']:
            pass
        else:
            flash('Você não tem permissão para acessar essa página')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return funcao_decorada
