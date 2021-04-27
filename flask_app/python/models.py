from flask import current_app
from flask_app import db, login_manager
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import json
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)#, nullable=False)
    cpf = db.Column(db.String(20), unique=True)#, nullable=False)
    celular = db.Column(db.String(20), unique=False)#, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)#, nullable=False)
    permission = db.Column(db.Integer, nullable=True)#, nullable=False)
    artes = db.relationship('Arte', backref='usuario', lazy=True, cascade="all, delete-orphan")
    backgroundsupload = db.relationship('BackgroundsUpload', backref='usuario', lazy=True, cascade="all, delete-orphan")
    customer_id = db.Column(db.String(120), unique=True, nullable=True)#, nullable=False)
    subscription_id = db.Column(db.String(120), unique=True, nullable=True)

    imagem_logo_arte = db.Column(db.String(120), unique=False, nullable=True)
    texto_email_arte = db.Column(db.String(120), unique=False, nullable=True)
    texto_telefone_arte = db.Column(db.String(120), unique=False, nullable=True)
    texto_site_arte = db.Column(db.String(120), unique=False, nullable=True)
    texto_endereco_arte = db.Column(db.String(240), unique=False, nullable=True)
    texto_nome_empresa_arte = db.Column(db.String(240), unique=False, nullable=True)
    texto_facebook_arte = db.Column(db.String(120), unique=False, nullable=True)
    texto_instagram_arte = db.Column(db.String(120), unique=False, nullable=True)

    woo_secret = db.Column(db.String(480), unique=False, nullable=True)
    woo_key = db.Column(db.String(120), unique=False, nullable=True)
    woo_store_url = db.Column(db.String(120), unique=False, nullable=True)
    woo_active = db.Column(db.Boolean, default=False, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'cpf': self.cpf,
            'celular': self.celular,
            'email': self.email,
            'permission': self.permission,
            'customer_id': self.customer_id,
            'subscription_id': self.subscription_id,
            'texto_email_arte': self.texto_email_arte,
            'texto_telefone_arte': self.texto_telefone_arte,
            'texto_site_arte': self.texto_site_arte,
            'imagem_logo_arte': self.imagem_logo_arte,
            'texto_endereco_arte': self.texto_endereco_arte,
            'texto_nome_empresa_arte': self.texto_nome_empresa_arte,
            'texto_facebook_arte': self.texto_facebook_arte,
            'texto_instagram_arte': self.texto_instagram_arte,
        }

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User: {self.username}>'

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

class BackgroundsUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    gif = db.Column(db.String(120), unique=False, nullable=True)
    video = db.Column(db.String(120), unique=False, nullable=True)
    imagem = db.Column(db.String(120), unique=False, nullable=False)
    section = db.Column(db.String(120), unique=False, nullable=False)
    tipo = db.Column(db.String(120), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'gif': self.gif,
            'video': self.video,
            'imagem': self.imagem,
            'section': self.section,
            'tipo': self.tipo,
        }


class Arte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    telas = db.relationship('Tela', backref='arte', lazy=True, cascade="all, delete-orphan")
    audio_id = db.Column(db.Integer, db.ForeignKey('audio.id'), default=1)
    animacao = db.Column(db.String(120), unique=False, nullable=True)
    data_ultima_edicao = db.Column(db.DateTime, nullable=True)
    animacao_gif = db.Column(db.String(120), unique=False, nullable=True)
    concluida = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'user_id': self.user_id,
            'animacao': self.animacao,
            'animacao_gif': self.animacao_gif,
            'data_ultima_edicao': self.data_ultima_edicao.strftime("%d/%m/%Y %H:%M:%S"),
            'telas_url':  [tela.serialize['imagem_preview'] for tela in self.telas if tela.preview_gerado == True],
            'num_telas': len(self.telas),
            'concluida': self.concluida,
            'audio_id': self.audio_id,
        }

    def __repr__(self):
        return f'<Arte: {self.nome}>'


class Tela(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=True)
    posicao = db.Column(db.Integer, unique=False, nullable=True)
    arte_id = db.Column(db.Integer, db.ForeignKey('arte.id'), nullable=True)
    preview_gerado = db.Column(db.Boolean, default=False, nullable=True)
    editada = db.Column(db.Boolean, default=True, nullable=True)
    duracao = db.Column(db.Integer, unique=False, nullable=True, default=8)
    imagem_preview = db.Column(db.String(120), unique=False, nullable=True)
    imagem_produto = db.Column(db.String(120), unique=False, nullable=True)
    imagem_produto_mask = db.Column(db.String(120), unique=False, nullable=True)
    animacao = db.Column(db.String(120), unique=False, nullable=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo.id'), unique=False, nullable=True)
    cores = db.Column(db.String(240), unique=False, nullable=True)
    fontes = db.Column(db.String(240), unique=False, nullable=True)
    fundo_id = db.Column(db.Integer, unique=False, nullable=True)
    fundo_tipo = db.Column(db.String(120), unique=False, nullable=True)
    texto_nomeproduto = db.Column(db.String(120), unique=False, nullable=True)
    texto_preconormal = db.Column(db.String(120), unique=False, nullable=True)
    texto_precodesconto = db.Column(db.String(120), unique=False, nullable=True)
    texto_porcentagemdesconto = db.Column(db.String(120), unique=False, nullable=True)
    texto_mensagem = db.Column(db.String(480), unique=False, nullable=True)
    texto_email = db.Column(db.String(120), unique=False, nullable=True)
    texto_telefone = db.Column(db.String(120), unique=False, nullable=True)
    texto_site = db.Column(db.String(120), unique=False, nullable=True)
    texto_endereco = db.Column(db.String(240), unique=False, nullable=True)
    texto_nomeempresa = db.Column(db.String(240), unique=False, nullable=True)
    texto_facebook = db.Column(db.String(120), unique=False, nullable=True)
    texto_instagram = db.Column(db.String(120), unique=False, nullable=True)
    remover_fundo = db.Column(db.Boolean, default=True, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'posicao': self.posicao,
            'arte_id': self.arte_id,
            'modelo_id': self.modelo_id,
            'cores': self.cores,
            'fontes': self.fontes,
            'fundo_id': self.fundo_id,
            'fundo_tipo': self.fundo_tipo,
            'editada': self.editada,
            'duracao': self.duracao,
            'texto_nomeproduto': self.texto_nomeproduto,
            'texto_preconormal': self.texto_preconormal,
            'texto_precodesconto': self.texto_precodesconto,
            'texto_porcentagemdesconto': self.texto_porcentagemdesconto,
            'imagem_preview': self.imagem_preview,
            'imagem_produto': self.imagem_produto,
            'imagem_produto_mask': self.imagem_produto_mask,
            'imagem_logo': self.arte.usuario.imagem_logo_arte,
            'animacao': self.animacao,
            'preview_gerado': self.preview_gerado,
            'texto_mensagem': self.texto_mensagem,
            'texto_email': self.texto_email,
            'texto_telefone': self.texto_telefone,
            'texto_site': self.texto_site,
            'texto_endereco': self.texto_endereco,
            'texto_nomeempresa': self.texto_nomeempresa,
            'texto_facebook': self.texto_facebook,
            'texto_instagram': self.texto_instagram,
            'remover_fundo': self.remover_fundo,
        }

    def __repr__(self):
        return f'<Tela: {self.nome}>'


labels = db.Table('labels',
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True),
    db.Column('modelo_id', db.Integer, db.ForeignKey('modelo.id'), primary_key=True),
)

atributos = db.Table('atributos',
    db.Column('atributo_id', db.Integer, db.ForeignKey('atributo.id'), primary_key=True),
    db.Column('modelo_id', db.Integer, db.ForeignKey('modelo.id'), primary_key=True)
)


class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=True)
    descricao = db.Column(db.String(120), unique=False, nullable=True)
    imagem = db.Column(db.String(120), unique=False, nullable=True)
    labels = db.relationship('Label', secondary=labels, backref=db.backref('modelos', lazy='dynamic'))
    atributos = db.relationship('Atributo', secondary=atributos, backref=db.backref('modelos', lazy='dynamic'))
    json = db.Column(db.String(120), unique=False, nullable=True)

    @property
    def serialize(self):
        with open(os.path.join(current_app.root_path, self.json)) as json_file:
            data = json.load(json_file)
        return {**data,
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'imagem': self.imagem,
            'labels': [label.serialize for label in self.labels],
            'atributos': [atributo.serialize for atributo in self.atributos],
        }

    def __repr__(self):
        return f'<Modelo: {self.nome}>'


class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(120), unique=False, nullable=False)
    gif = db.Column(db.String(120), unique=False, nullable=True)
    video = db.Column(db.String(120), unique=False, nullable=True)
    imagem = db.Column(db.String(120), unique=False, nullable=False)
    tipo = db.Column(db.String(120), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'section': self.section,
            'gif': self.gif,
            'video': self.video,
            'imagem': self.imagem,
            'tipo': self.tipo,
        }

    def __repr__(self):
        return f'<Background: {self.id}>'


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)

    @property
    def serialize(self):
        return self.nome

    def __repr__(self):
        return f'<Label: {self.nome}>'


class Atributo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)

    @property
    def serialize(self):
        return self.nome

    def __repr__(self):
        return f'<Atributo: {self.nome}>'


class Audio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=False, nullable=False)
    caminho = db.Column(db.String(120), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'caminho': self.caminho,
        }


class Fonte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=False, nullable=False)
    caminho = db.Column(db.String(120), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'caminho': self.caminho,
        }
