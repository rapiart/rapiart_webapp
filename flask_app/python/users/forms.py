from flask import session
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app import bcrypt
from flask_app.python.models import User
from flask_app.python.main.utils import post_request_to_api



class RegistrationForm(FlaskForm):
    username = StringField("Nome completo",
        validators=[DataRequired(), Length(min=2, max=60)])
    cpf = StringField("CPF",
        validators=[DataRequired(), Length(min=14, max=14)])
    email = StringField("Email",
        validators=[DataRequired(), Email()])
    celular = StringField("Celular",
        validators=[DataRequired(), Length(min=14, max=15)])
    password = PasswordField("Senha",
        validators=[DataRequired()])
    confirm_password = PasswordField("Confirmar Senha",
        validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrar")

    def validate_cpf(self, cpf):
        json = {"cpf": cpf.data}
        data = post_request_to_api('is-avaible', json=json)
        if data["status"] == "Error":
            raise ValidationError("Esse CPF já foi usado.")

    def validate_email(self, email):
        json = {"email": email.data}
        data = post_request_to_api('is-avaible', json=json)
        if data["status"] == "Error":
            raise ValidationError("Esse email já foi usado.")


class LoginForm(FlaskForm):
    email = StringField("Email",
        validators=[DataRequired(), Email()])
    password = PasswordField("Senha",
        validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")


class UpdateAccountForm(FlaskForm):
    username = StringField("Nome completo",
        validators=[DataRequired(), Length(min=2, max=40)])
    cpf = StringField("CPF",
        validators=[DataRequired(), Length(min=14, max=14)])
    celular = StringField("Celular",
        validators=[DataRequired(), Length(min=14, max=15)])
    email = StringField("Email",
        validators=[DataRequired(), Email(message="Email inválido")])
    submit = SubmitField("Salvar dados")

    def validate_cpf(self, cpf):
        if cpf.data != session['current_user']['cpf']:
            json = {"cpf": cpf.data}
            data = post_request_to_api('is-avaible', json=json)
            if data["status"] == "Error":
                raise ValidationError("Esse CPF já foi usado.")

    def validate_email(self, email):
        if email.data != session['current_user']['email']:
            json = {"email": email.data}
            data = post_request_to_api('is-avaible', json=json)
            if data["status"] == "Error":
                raise ValidationError("Esse email já foi usado.")
                

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Senha Atual",
        validators=[DataRequired()])
    new_password = PasswordField("Nova Senha",
        validators=[DataRequired()])
    confirm_new_password = PasswordField("Confirmar Nova Senha",
        validators=[DataRequired(), EqualTo("new_password", message="Erro na confirmação. Os campos com a nova senha estão diferentes")])
    submit2 = SubmitField("Alterar Senha")


class RequestResetForm(FlaskForm):
    email = StringField("Email",
        validators=[DataRequired(), Email()])
    submit = SubmitField("Recuperar senha")

    def validate_email(self, email):
        json = {"email": email.data}
        data = post_request_to_api('is-avaible', json=json)
        if data["status"] == "Success":
            raise ValidationError("Esse email não está cadastrado em nenhuma conta.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Senha",
        validators=[DataRequired()])
    confirm_password = PasswordField("Confirmar Senha",
        validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Resetar senha")
