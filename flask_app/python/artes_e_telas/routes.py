from flask import current_app, Blueprint, render_template, url_for, redirect, request, jsonify, session
from flask_login import current_user, login_required
from flask_app import db
from flask_app.python.models import User, Arte, Tela, Modelo, Audio, Background, BackgroundsUpload, Fonte
from flask_app.python.artes_e_telas.utils import generate_tela_animation, get_mask, get_discount, sort_model_by_nome
from flask_app.python.users.decorators import customers_only
from flask_app.python.users.utils import get_seed
from flask_app.python.main.routes import download_file
from flask_app.python.ecommerce.utils import woo_object

from sqlalchemy.orm.session import make_transient
from sqlalchemy import desc
import os
import uuid
import subprocess
import multiprocessing as mp
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import datetime
from google.cloud import storage
import pathlib
import shutil
import cv2
import random
import requests

artes_e_telas = Blueprint('artes_e_telas', __name__)


@artes_e_telas.route('/artes_finalizadas', methods=['GET'])
@login_required
@customers_only
def artes_finalizadas():
    user_id = current_user.id

    artes = Arte.query.filter_by(user_id=user_id).order_by(
        desc(Arte.data_ultima_edicao))
    artes = [arte.serialize for arte in artes]

    return render_template('artes_finalizadas.html', title='Galeria de Artes', artes_finalizadas=artes)


@artes_e_telas.route('/editar_tela', methods=['GET'])
@login_required
@customers_only
def editar_tela():
    user = User.query.filter(User.id == current_user.id).first()
    tela_id = int(request.args.get("tela_id"))
    tela = Tela.query.get(tela_id)
    if tela:
        arte = Arte.query.get(tela.arte_id)
        if arte:
            if arte.user_id == current_user.id:
                cores = current_app.config["CORES"]
                fontes = Fonte.query.all()
                fontes_nomes = [fonte.nome for fonte in fontes]

                modelos = Modelo.query.filter(
                    Modelo.id >= 0).order_by(Modelo.nome).all()
                modelos = [modelo.serialize for modelo in modelos]
                modelos.sort(key=sort_model_by_nome)

                if tela.modelo_id >= 0:
                    for i in range(len(modelos)):
                        if modelos[i]["id"] == tela.modelo_id:
                            if tela.cores:
                                modelos[i]["cores"] = tela.cores.split(',')
                            if tela.fontes:
                                modelos[i]["fontes"] = tela.fontes.split(',')
                            modelo = modelos[i]
                else:
                    modelo = {}

                if tela.fundo_id:
                    if tela.fundo_tipo=='uploads':
                        fundo = BackgroundsUpload.query.get(tela.fundo_id).serialize
                    else:
                        fundo = Background.query.get(tela.fundo_id).serialize
                else:
                    fundo = {}

                tela = tela.serialize
                arte = arte.serialize

                return render_template('editar_tela.html', title='Edição de Tela', cores=cores, fontes=fontes_nomes,  modelos=modelos, tela=tela, modelo=modelo, fundo=fundo, background_cfg=current_app.config["FUNDOS_CFG"], woo_active=user.woo_active)
    return render_template('errors/404.html', title='Erro 404')


@artes_e_telas.route('/get_woo_product', methods=['POST'])
def get_woo_product():
    if request.method == 'POST':
        data = request.get_json()

        produto_sku = str(data['sku'])
        user = User.query.filter(User.id == current_user.id).first()

        wcapi = woo_object(user)
        response = wcapi.get(f"products?sku={produto_sku}").json()

        if len(response) > 0:
            produto = response[0]

            data = {}
            data['nome_produto'] = produto['name']
            if produto.get('images'):
                image = produto['images'][0]['src']
                data['imagem_produto'] = image
            if produto['sale_price']:
                data['preco_desconto'] = produto['sale_price']
                data['preco_normal'] = produto['regular_price']
            else:
                data['preco_desconto'] = produto['regular_price']
                data['preco_normal'] = ''
        else:
            data = {}

        return jsonify(data)


@artes_e_telas.route('/add_arte', methods=['POST'])
def add_arte():
    if request.method == 'POST':
        data = request.get_json()

        art_name = str(data['art_name'])
        if art_name == "":
            art_name = "Sem nome"

        arte = Arte(nome=art_name, user_id=current_user.id,
                    data_ultima_edicao=datetime.now())
        db.session.add(arte)
        db.session.commit()

        arte_id = arte.id

        return jsonify({'arteId': arte_id})


@artes_e_telas.route('/get_fundos', methods=['POST'])
def get_fundos():
    if request.method == 'POST':
        data = request.get_json()

        file_type = data['file_type']
        tab_id = data['tab_id']
        pagina = data['pagina']

        per_page = 12
        if file_type == 'videos':
            if tab_id == "todos":
                fundos = Background.query.filter(
                    Background.tipo == 'videos').order_by(Background.id).all()
                num_fundos = len(fundos)
                random_fundos_order = list(range(num_fundos))
                random.Random(get_seed()).shuffle(random_fundos_order)
                pagina_posicoes = random_fundos_order[(
                    pagina - 1)*per_page: pagina*per_page]
                fundos = [fundos[i] for i in pagina_posicoes]
                paginas_total = num_fundos//per_page + \
                    1 if (num_fundos % per_page) else num_fundos//per_page
            else:
                paginacao = Background.query.filter(
                    Background.section == tab_id, Background.tipo == 'videos').paginate(pagina, per_page, error_out=False)
                paginas_total = paginacao.pages
                fundos = paginacao.items
        elif file_type == 'imagens':
            if tab_id == "todos":
                fundos = Background.query.filter(
                    Background.tipo == 'imagens').order_by(Background.id).all()
                num_fundos = len(fundos)
                random_fundos_order = list(range(num_fundos))
                random.Random(get_seed()).shuffle(random_fundos_order)
                pagina_posicoes = random_fundos_order[(
                    pagina - 1)*per_page: pagina*per_page]
                fundos = [fundos[i] for i in pagina_posicoes]
                paginas_total = num_fundos//per_page + \
                    1 if (num_fundos % per_page) else num_fundos//per_page
            else:
                paginacao = Background.query.filter(
                    Background.section == tab_id, Background.tipo == 'imagens').paginate(pagina, per_page, error_out=False)
                paginas_total = paginacao.pages
                fundos = paginacao.items
        elif file_type == 'uploads':
            paginacao = BackgroundsUpload.query.filter(
                    BackgroundsUpload.user_id == current_user.id).paginate(pagina, per_page, error_out=False)
            paginas_total = paginacao.pages
            fundos = paginacao.items

        fundos = [fundo.serialize for fundo in fundos]

        return jsonify({'fundos': fundos, 'paginasTotal': paginas_total, 'paginaAtual': pagina})

@artes_e_telas.route('/fundo_upload', methods=['POST'])
def fundo_upload():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')

        fundo_upload_image_path = f'storage/user_{current_user.id}/fundo_{str(uuid.uuid4())}.png'
        full_fundo_upload_image_path = os.path.join(
            current_app.root_path, fundo_upload_image_path)
        os.makedirs(os.path.dirname(
            full_fundo_upload_image_path), exist_ok=True)

        f = request.files.get('uploadedImage')
        fundo_upload_bytes = f.read()
        fundo_upload = Image.open(BytesIO(fundo_upload_bytes))
        fundo_upload = fundo_upload.resize((800, 800), Image.ANTIALIAS)
        fundo_upload.save(full_fundo_upload_image_path)

        new_blob = bucket.blob(fundo_upload_image_path)
        new_blob.upload_from_filename(full_fundo_upload_image_path)
        
        bkg = BackgroundsUpload(
            user_id=current_user.id,
            gif=fundo_upload_image_path,
            video=fundo_upload_image_path,
            imagem=fundo_upload_image_path,
            section='imagens',
            tipo='uploads',
        )
        db.session.add(bkg)
        db.session.commit()

        return jsonify({'status': 'success'})

@artes_e_telas.route('/rascunhos', methods=['GET'])
@login_required
@customers_only
def rascunhos():
    arte_id = request.args['arteId']

    if arte_id:
        arte = Arte.query.filter(Arte.id == arte_id).first()

        if arte:
            telas = Tela.query.filter_by(
                arte_id=arte_id).order_by(Tela.posicao).all()
            audios = Audio.query.all()
            arte = arte.serialize
            telas = [tela.serialize for tela in telas]
            audios = [audio.serialize for audio in audios]

            return render_template('rascunhos.html', title='Edição de Arte', arte=arte, telas=telas, audios=audios)

    return render_template('errors/404.html', title='Erro 404')


@artes_e_telas.route('/excluir_tela', methods=['POST'])
def excluir_tela():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')

        data = request.get_json()

        tela_id = int(data['telaId'])
        arte_id = int(data['arteId'])

        tela = db.session.query(Tela).get(tela_id)
        tela_imagem = tela.imagem_preview
        tela_imagem_produto = tela.imagem_produto
        tela_imagem_produto_mask = tela.imagem_produto_mask
        tela_animacao = tela.animacao

        Tela.query.filter_by(id=tela_id).delete()

        user_telas = Tela.query.filter_by(arte_id=arte_id).all()
        posicoes = [tela.posicao for tela in user_telas]
        argsort_posicoes = np.argsort(posicoes)

        for i, idx in enumerate(argsort_posicoes):
            user_telas[idx].posicao = i
            db.session.add(user_telas[idx])
        db.session.commit()

        if tela_imagem:
            if pathlib.Path(tela_imagem).parts[0] == 'storage':
                path = os.path.join(current_app.root_path,
                                    tela_imagem.strip("/"))
                os.remove(path) if os.path.exists(path) else None
                blob = bucket.blob(tela_imagem)
                blob.delete()

        if tela_imagem_produto:
            if pathlib.Path(tela_imagem_produto).parts[0] == 'storage':
                path = os.path.join(current_app.root_path, tela_imagem_produto)
                os.remove(path) if os.path.exists(path) else None
                blob = bucket.blob(tela_imagem_produto)
                blob.delete()

        if tela_imagem_produto_mask:
            if pathlib.Path(tela_imagem_produto_mask).parts[0] == 'storage':
                path = os.path.join(current_app.root_path,
                                    tela_imagem_produto_mask)
                os.remove(path) if os.path.exists(path) else None
                blob = bucket.blob(tela_imagem_produto_mask)
                blob.delete()

        if tela_animacao:
            if pathlib.Path(tela_animacao).parts[0] == 'storage':
                path = os.path.join(current_app.root_path, tela_animacao)
                os.remove(path) if os.path.exists(path) else None
                blob = bucket.blob(tela_animacao)
                blob.delete()

        telas = Tela.query.filter_by(
            arte_id=arte_id).order_by(Tela.posicao).all()
        telas = [tela.serialize for tela in telas]

        return jsonify({'telas': telas})


@artes_e_telas.route('/novo_nome_arte_finalizada', methods=['POST'])
def novo_nome_arte_finalizada():
    if request.method == 'POST':

        user_id = current_user.id

        data = request.get_json()
        arte_id = int(data['arteId'])
        novo_nome = data['novoNome']

        arte = db.session.query(Arte).get(arte_id)
        arte.nome = novo_nome
        db.session.commit()

        artes = Arte.query.filter_by(user_id=user_id).order_by(
            desc(Arte.data_ultima_edicao))
        artes = [arte.serialize for arte in artes]

        return jsonify({'artes': artes})


@artes_e_telas.route('/novo_nome_rascunho', methods=['POST'])
def novo_nome_rascunho():
    if request.method == 'POST':

        data = request.get_json()
        arte_id = int(data['arteId'])
        novo_nome = data['novoNome']

        arte = db.session.query(Arte).get(arte_id)
        arte.nome = novo_nome
        db.session.commit()

        telas = Tela.query.filter_by(
            arte_id=arte_id).order_by(Tela.posicao).all()

        arte = arte.serialize
        telas = [tela.serialize for tela in telas]

        return jsonify({'arte': arte, 'telas': telas})


@artes_e_telas.route('/escolher_fundo', methods=['POST'])
def escolher_fundo():
    if request.method == 'POST':
        data = request.get_json()

        tela_id = int(data['telaId'])
        fundo_id = int(data['fundoId'])
        fundo_tipo = data['fundoTipo']

        tela = db.session.query(Tela).get(tela_id)
        if fundo_id == -1:
            tela.fundo_id = None
            tela.fundo_tipo = None
            tela.imagem_preview = current_app.config["SEM_MODELO_PATH"]
            tela.preview_gerado = False
        else:
            tela.fundo_id = fundo_id
            tela.fundo_tipo = fundo_tipo
        db.session.commit()

        tela = tela.serialize

        return jsonify({'tela': tela})


@artes_e_telas.route('/escolher_modelo', methods=['POST'])
def escolher_modelo():
    if request.method == 'POST':

        data = request.get_json()

        tela_id = int(data['telaId'])
        modelo_id = int(data['modeloId'])

        modelo = db.session.query(Modelo).get(modelo_id)
        tela = db.session.query(Tela).get(tela_id)
        tela.modelo_id = modelo_id
        if modelo_id == -1:
            tela.nome = modelo.nome
            tela.imagem_preview = current_app.config["SEM_MODELO_PATH"]
            tela.preview_gerado = False
        else:
            tela.nome = modelo.labels[0].serialize

        db.session.commit()

        tela = tela.serialize
        return jsonify({'tela': tela})


@artes_e_telas.route('/remove_arte', methods=['POST'])
def remove_arte():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')

        data = request.get_json()
        arte_id = int(data['arteId'])
        user_id = current_user.id

        arte = Arte.query.filter(Arte.id == arte_id).first()

        db.session.delete(arte)
        db.session.commit()

        storage_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/'

        full_local_path = os.path.join(current_app.root_path, storage_path)
        if os.path.exists(full_local_path):
            shutil.rmtree(full_local_path)

        blobs = bucket.list_blobs(prefix=storage_path)
        for blob in blobs:
            blob.delete()

        artes = Arte.query.filter_by(user_id=user_id).order_by(
            desc(Arte.data_ultima_edicao))
        artes = [arte.serialize for arte in artes]

        return jsonify({'artes': artes})


@artes_e_telas.route('/criar_tela', methods=['POST'])
def criar_tela():
    if request.method == 'POST':

        data = request.get_json()
        arte_id = int(data['arteId'])
        user = User.query.filter(User.id == current_user.id).first()

        last_tela = Tela.query.filter(Tela.arte_id == arte_id).order_by(
            Tela.posicao.desc()).first()
        if last_tela is None:
            max_position = -1
        else:
            max_position = last_tela.posicao

        nova_tela = Tela(nome="Tela não salva", modelo_id=-1, posicao=max_position+1,
                         arte_id=arte_id, imagem_preview=current_app.config["SEM_MODELO_PATH"])

        nova_tela.texto_email = user.texto_email_arte
        nova_tela.texto_telefone = user.texto_telefone_arte
        nova_tela.texto_site = user.texto_site_arte
        nova_tela.texto_endereco = user.texto_endereco_arte
        nova_tela.texto_nome_empresa = user.texto_nome_empresa_arte
        nova_tela.texto_facebook = user.texto_facebook_arte
        nova_tela.texto_instagram = user.texto_instagram_arte

        db.session.add(nova_tela)
        db.session.commit()

        telas = Tela.query.filter_by(
            arte_id=arte_id).order_by(Tela.posicao).all()
        telas = [tela.serialize for tela in telas]

        return jsonify({'telas': telas})


@artes_e_telas.route('/copiar_tela', methods=['POST'])
def copiar_tela():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')
        data = request.get_json()

        tela_id = int(data['telaId'])
        arte_id = int(data['arteId'])

        tela = Tela.query.get(tela_id)
        db.session.expunge(tela)
        make_transient(tela)
        tela.id = None

        db.session.add(tela)
        db.session.commit()

        if tela.imagem_preview and pathlib.Path(tela.imagem_preview).parts[0] == 'storage':
            new_imagem_preview = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/preview_{str(uuid.uuid4())}.png'
            blob = bucket.blob(tela.imagem_preview)
            blob_copy = bucket.copy_blob(blob, bucket, new_imagem_preview)
            download_file(new_imagem_preview)
            tela.imagem_preview = new_imagem_preview

        if tela.imagem_produto_mask:
            new_imagem_produto_mask = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/mask_{str(uuid.uuid4())}.png'
            blob = bucket.blob(tela.imagem_produto_mask)
            blob_copy = bucket.copy_blob(blob, bucket, new_imagem_produto_mask)
            download_file(new_imagem_produto_mask)
            tela.imagem_produto_mask = new_imagem_produto_mask

        if tela.imagem_produto:
            new_imagem_produto = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/produto_{str(uuid.uuid4())}.png'
            blob = bucket.blob(tela.imagem_produto)
            blob_copy = bucket.copy_blob(blob, bucket, new_imagem_produto)
            download_file(new_imagem_produto)
            tela.imagem_produto = new_imagem_produto

        if tela.animacao:
            new_tela_animation_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/preview_{str(uuid.uuid4())}.mp4'
            blob = bucket.blob(tela.animacao)
            blob_copy = bucket.copy_blob(blob, bucket, new_tela_animation_path)
            download_file(new_tela_animation_path)
            tela.animacao = new_tela_animation_path

        db.session.add(tela)

        user_telas = Tela.query.filter_by(arte_id=arte_id).all()
        posicoes = [tela.posicao for tela in user_telas]

        argsort_posicoes = np.argsort(posicoes)

        for i, idx in enumerate(argsort_posicoes):
            user_telas[idx].posicao = i
            db.session.add(user_telas[idx])

        db.session.commit()

        telas = Tela.query.filter_by(
            arte_id=arte_id).order_by(Tela.posicao).all()
        telas = [tela.serialize for tela in telas]

        return jsonify({'telas': telas})


@artes_e_telas.route('/mover_tela', methods=['POST'])
def mover_tela():
    if request.method == 'POST':
        data = request.get_json()

        tela_id = int(data['telaId'])
        arte_id = int(data['arteId'])
        direction = data['direction']
        quantity = Tela.query.filter_by(arte_id=arte_id).count()

        tela = db.session.query(Tela).get(tela_id)
        position = tela.posicao

        if direction == 'right' and position < quantity-1:
            tela_direita = db.session.query(Tela).filter_by(
                arte_id=arte_id, posicao=position+1).first()
            tela.posicao = position + 1
            tela_direita.posicao = position
        elif direction == 'left' and position > 0:
            tela_esquerda = db.session.query(Tela).filter_by(
                arte_id=arte_id, posicao=position-1).first()
            tela.posicao = position - 1
            tela_esquerda.posicao = position

        db.session.commit()

        user_telas = Tela.query.filter_by(
            arte_id=arte_id).order_by(Tela.posicao).all()
        user_telas = [user_tela.serialize for user_tela in user_telas]
        return jsonify(user_telas)


@artes_e_telas.route('/generate_animation', methods=['POST'])
def generate_animation():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')

        fps = 20

        data = request.get_json()
        arte_id = int(data['arteId'])
        audio_id = int(data['audioId'])

        user = User.query.filter(User.id == current_user.id).first()

        arte = Arte.query.filter(Arte.id == arte_id).first()
        telas = Tela.query.filter_by(arte_id=arte_id).all()

        old_gif = arte.animacao_gif
        old_animacao = arte.animacao

        arte_animacao_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/preview_{str(uuid.uuid4())}.mp4'
        full_arte_animacao_path = os.path.join(
            current_app.root_path, arte_animacao_path)
        telas_duracao_total = 0
        if len(telas) > 1:
            processos = []
            full_telas_animation_path = []
            telas_animation_path = []
            for tela in telas:
                telas_duracao_total += tela.duracao
                if tela.editada is True:
                    tela_dict = tela.serialize

                    if user.imagem_logo_arte:
                        tela_dict['imagem_logo'] = os.path.join(
                            current_app.root_path, user.imagem_logo_arte)

                    if tela.fundo_tipo=='uploads':
                        fundo = BackgroundsUpload.query.get(tela.fundo_id)
                        tela_dict['bkg_video'] = os.path.join(current_app.root_path, fundo.video)
                    else:
                        fundo = Background.query.get(tela.fundo_id)
                        tela_dict['bkg_video'] = os.path.join(os.path.join(
                            current_app.root_path, 'static'), os.path.relpath(fundo.video, current_app.config["STORAGE_APP"]))

                    modelo_dict = Modelo.query.get(tela.modelo_id).serialize
                    if tela_dict.get('imagem_produto'):
                        download_file(tela.imagem_produto)
                    if tela_dict.get('imagem_produto_mask'):
                        download_file(tela.imagem_produto_mask)
                    if tela_dict.get('imagem_logo'):
                        download_file(tela_dict.get('imagem_logo'))
                    tela_animation_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/preview_{str(uuid.uuid4())}.mp4'
                    full_tela_animation_path = os.path.join(
                        current_app.root_path, tela_animation_path)

                    p = mp.Process(target=generate_tela_animation, args=[
                                   tela_dict, modelo_dict, full_tela_animation_path, fps])
                    p.start()
                    processos.append(p)
                else:
                    tela_animation_path = tela.animacao
                    download_file(tela_animation_path)

                full_tela_animation_path = os.path.join(
                    current_app.root_path, tela_animation_path)
                full_telas_animation_path.append(full_tela_animation_path)
                telas_animation_path.append(tela_animation_path)

            for p in processos:
                p.join()

            posicoes = []
            for tela, tela_animation_path in zip(telas, telas_animation_path):
                posicoes.append(tela.posicao)
                if tela.editada is True:
                    tela.animacao = tela_animation_path
                    full_tela_animation_path = os.path.join(
                        current_app.root_path, tela_animation_path)
                    new_blob = bucket.blob(tela_animation_path)
                    new_blob.upload_from_filename(full_tela_animation_path)
                    tela.editada = False

            sort_idx = np.argsort(posicoes)

            telas = np.array(telas)[sort_idx]
            full_telas_animation_path = np.array(
                full_telas_animation_path)[sort_idx]
            telas_animation_path = np.array(telas_animation_path)[sort_idx]
            ffmpeg_command = ['ffmpeg']
            ffmpeg_command.extend(
                sum([['-i', i] for i in full_telas_animation_path], []))
            filter_command = ''
            first = 0
            second = 1
            offset = telas[0].duracao - 1
            for tela in telas[1:]:
                out = f'{first}{second}'
                filter_command += f'[{first}][{second}]xfade=transition=fade:duration=1:offset={offset}[{out}];'
                first = out
                second += 1
                offset = offset + tela.duracao - 1

            ffmpeg_command.append('-filter_complex')
            ffmpeg_command.append(filter_command.split(f'[{out}]')[0])
            ffmpeg_command.extend(
                ['-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(fps)])
            ffmpeg_command.append(full_arte_animacao_path)

            resp = subprocess.check_output(ffmpeg_command)

        elif len(telas) == 1:
            tela = telas[0]
            telas_duracao_total = tela.duracao
            if tela.editada is True:
                tela.editada = False
                tela_dict = tela.serialize
                if user.imagem_logo_arte:
                    tela_dict['imagem_logo'] = os.path.join(
                        current_app.root_path, user.imagem_logo_arte)
                modelo_dict = Modelo.query.get(tela.modelo_id).serialize

                if tela.fundo_tipo=='uploads':
                    fundo = BackgroundsUpload.query.get(tela.fundo_id)
                    tela_dict['bkg_video'] = os.path.join(current_app.root_path, fundo.video)
                else:
                    fundo = Background.query.get(tela.fundo_id)
                    tela_dict['bkg_video'] = os.path.join(os.path.join(
                        current_app.root_path, 'static'), os.path.relpath(fundo.video, current_app.config["STORAGE_APP"]))

                tela_animation_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela.id}/preview_{str(uuid.uuid4())}.mp4'
                full_tela_animation_path = os.path.join(
                    current_app.root_path, tela_animation_path)
                tela.animacao = tela_animation_path
                generate_tela_animation(
                    tela_dict, modelo_dict, full_tela_animation_path, fps=fps)
                new_blob = bucket.blob(tela_animation_path)
                new_blob.upload_from_filename(full_tela_animation_path)
            else:
                tela_animation_path = tela.animacao
                full_tela_animation_path = os.path.join(
                    current_app.root_path, tela_animation_path)
                download_file(tela_animation_path)

            shutil.copyfile(full_tela_animation_path, full_arte_animacao_path)

        if audio_id > 1:
            audio_fade_out_start_time = telas_duracao_total - len(telas)
            arte.audio_id = audio_id
            audio = Audio.query.get(audio_id)
            audio_src = audio.caminho
            temp_path = full_arte_animacao_path.split('.mp4')[0]
            temp_path += '_temp.mp4'
            os.rename(full_arte_animacao_path, temp_path)
            full_audio_src = os.path.join(current_app.root_path, audio_src)
            audio_command = ['ffmpeg', '-i', temp_path, '-stream_loop', '-1', '-i', full_audio_src, '-af', f"apad,afade=type=out:start_time={audio_fade_out_start_time}:duration=1", '-shortest', '-map', '0:v:0',
                             '-map', '1:a:0', '-y', full_arte_animacao_path]

            resp = subprocess.check_output(audio_command)
            os.remove(temp_path)

        gif_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/gif_{str(uuid.uuid4())}.gif'
        full_gif_path = os.path.join(current_app.root_path, gif_path)

        ffmpeg_command = ['ffmpeg']
        ffmpeg_command.extend(['-i', full_arte_animacao_path, '-vf',
                               "fps=10,scale=200:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                               "-loop", '0', '-y', full_gif_path])
        resp = subprocess.check_output(ffmpeg_command)

        arte.data_ultima_edicao = datetime.now()
        arte.animacao_gif = gif_path
        arte.animacao = arte_animacao_path
        arte.concluida = True
        db.session.commit()

        new_blob = bucket.blob(arte_animacao_path)
        new_blob.upload_from_filename(full_arte_animacao_path)

        new_blob = bucket.blob(gif_path)
        new_blob.upload_from_filename(full_gif_path)

        if old_gif:
            if pathlib.Path(old_gif).parts[0] == 'storage':
                new_blob = bucket.blob(old_gif)
                new_blob.delete()

        if old_animacao:
            if pathlib.Path(old_animacao).parts[0] == 'storage':
                new_blob = bucket.blob(old_animacao)
                new_blob.delete()

        return jsonify({'animacao_src': arte_animacao_path})


@artes_e_telas.route('/parse_data', methods=['POST'])
def parse():
    if request.method == 'POST':
        storage_client = storage.Client(project='rapiartapp')
        bucket = storage_client.get_bucket('rapiart_bucket')

        tela_id = request.form.get('telaId')
        image_produto_loaded = request.form.get('isImgProdLoaded')
        image_woocommerce = request.form.get('wooImported')
        image_logo_loaded = request.form.get('isImgLogoLoaded')
        nome_produto = request.form.get('nome-produto')
        preco_normal = request.form.get('preco-normal')
        preco_desconto = request.form.get('preco-desconto')
        site = request.form.get('website')
        mensagem = request.form.get('mensagem')
        duracao = int(request.form.get('duracao'))
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')
        nome_empresa = request.form.get('nome-empresa')
        facebook = request.form.get('facebook')
        instagram = request.form.get('instagram')
        remover_fundo = bool(request.form.get('check-remove-fundo'))
        cores = request.form.get('cores')
        fontes = request.form.get('fontes')

        user = db.session.query(User).get(current_user.id)
        tela = db.session.query(Tela).get(tela_id)
        arte_id = tela.arte_id
        modelo = db.session.query(Modelo).get(tela.modelo_id)
        if tela.fundo_tipo == 'uploads':
            fundo = BackgroundsUpload.query.get(tela.fundo_id)
        else:
            fundo = Background.query.get(tela.fundo_id)

        if preco_normal and preco_desconto:
            porcentagem_desconto = get_discount(preco_normal, preco_desconto)
        else:
            porcentagem_desconto = ""

        old_preview = tela.imagem_preview

        if image_logo_loaded == 'true':
            old_logo = user.imagem_logo_arte

            user_imagem_logo_path = f'storage/user_{current_user.id}/logo_{str(uuid.uuid4())}.png'
            full_user_imagem_logo_path = os.path.join(
                current_app.root_path, user_imagem_logo_path)
            os.makedirs(os.path.dirname(
                full_user_imagem_logo_path), exist_ok=True)

            f = request.files.get('imgLogoFile')
            imagem_logo_bytes = f.read()
            image_logo = Image.open(BytesIO(imagem_logo_bytes))
            image_logo.save(full_user_imagem_logo_path)
            new_blob = bucket.blob(user_imagem_logo_path)
            new_blob.upload_from_filename(full_user_imagem_logo_path)
            user.imagem_logo_arte = user_imagem_logo_path

            if old_logo:
                new_blob = bucket.blob(old_logo)
                new_blob.delete()

        elif (user.imagem_logo_arte):
            imagem_logo_path = user.imagem_logo_arte
            download_file(imagem_logo_path)

        if image_produto_loaded == 'true':
            old_produto = tela.imagem_produto
            old_mask = tela.imagem_produto_mask

            imagem_produto_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela_id}/produto_{str(uuid.uuid4())}.png'
            mask_produto_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela_id}/mask_{str(uuid.uuid4())}.png'
            full_imagem_produto_path = os.path.join(
                current_app.root_path, imagem_produto_path)
            full_mask_produto_path = os.path.join(
                current_app.root_path, mask_produto_path)
            os.makedirs(os.path.dirname(
                full_imagem_produto_path), exist_ok=True)

            if image_woocommerce == 'true':
                url = request.form.get('imgProdFile')
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'}
                r = requests.get(url, headers=headers)
                image = Image.open(BytesIO(r.content))
            else:
                f = request.files.get('imgProdFile')
                imagem_produto_bytes = f.read()
                image = Image.open(BytesIO(imagem_produto_bytes))

            image.save(full_imagem_produto_path)
            image = np.array(image)
            if image.shape[-1] == 4 and len(np.unique(image[..., -1])) > 1:
                mask = image[..., -1]
            else:
                mask = get_mask(image)
            cv2.imwrite(full_mask_produto_path, mask)

            new_blob = bucket.blob(imagem_produto_path)
            new_blob.upload_from_filename(full_imagem_produto_path)
            tela.imagem_produto = imagem_produto_path

            new_blob = bucket.blob(mask_produto_path)
            new_blob.upload_from_filename(full_mask_produto_path)
            tela.imagem_produto_mask = mask_produto_path

            if old_produto:
                new_blob = bucket.blob(old_produto)
                new_blob.delete()

            if old_mask:
                new_blob = bucket.blob(old_mask)
                new_blob.delete()

        elif (tela.imagem_produto):
            imagem_produto_path = tela.imagem_produto
            download_file(tela.imagem_produto)
            mask_produto_path = tela.imagem_produto_mask
            download_file(tela.imagem_produto_mask)
            full_imagem_produto_path = os.path.join(
                current_app.root_path, imagem_produto_path)
            full_mask_produto_path = os.path.join(
                current_app.root_path, mask_produto_path)

        user.texto_email_arte = email
        user.texto_telefone_arte = telefone
        user.texto_site_arte = site
        user.texto_endereco_arte = endereco
        user.texto_nomeempresa_arte = nome_empresa
        user.texto_facebook_arte = facebook
        user.texto_instagram_arte = instagram

        tela.texto_nomeproduto = nome_produto
        tela.texto_preconormal = preco_normal
        tela.texto_precodesconto = preco_desconto
        tela.texto_porcentagemdesconto = porcentagem_desconto
        tela.texto_mensagem = mensagem
        tela.duracao = duracao
        tela.texto_email = email
        tela.texto_telefone = telefone
        tela.texto_site = site
        tela.texto_endereco = endereco
        tela.texto_nomeempresa = nome_empresa
        tela.texto_facebook = facebook
        tela.texto_instagram = instagram
        tela.remover_fundo = remover_fundo
        tela.preview_gerado = True
        tela.editada = True
        tela.cores = cores
        tela.fontes = fontes

        modelo_dict = modelo.serialize
        tela_dict = tela.serialize

        if user.imagem_logo_arte:
            tela_dict['imagem_logo'] = os.path.join(
                current_app.root_path, user.imagem_logo_arte)
        if site:
            tela_dict['texto_site'] = site
        if telefone:
            tela_dict['texto_telefone'] = telefone
        if nome_empresa:
            tela_dict['texto_nome_empresa'] = nome_empresa
        if endereco:
            tela_dict['texto_endereco'] = endereco

        if tela.fundo_tipo == 'uploads':
            tela_dict['bkg_image'] = os.path.join(current_app.root_path, fundo.imagem)
        else:
            tela_dict['bkg_image'] = os.path.join(os.path.join(
                current_app.root_path, 'static'), os.path.relpath(fundo.imagem, current_app.config["STORAGE_APP"]))
                
        imagem_preview_path = f'storage/user_{current_user.id}/rascunho_{arte_id}/tela_{tela_id}/preview_{str(uuid.uuid4())}.png'
        full_imagem_preview_path = os.path.join(
            current_app.root_path, imagem_preview_path)
        os.makedirs(os.path.dirname(full_imagem_preview_path), exist_ok=True)

        generate_tela_animation(tela_dict, modelo_dict,
                                full_imagem_preview_path, export='imagem')

        tela.imagem_preview = imagem_preview_path
        db.session.commit()

        new_blob = bucket.blob(imagem_preview_path)
        new_blob.upload_from_filename(full_imagem_preview_path)

        if pathlib.Path(old_preview).parts[0] == 'storage':
            new_blob = bucket.blob(old_preview)
            new_blob.delete()

        tela = tela.serialize

        return jsonify({'tela': tela})
    else:
        return redirect(url_for('main.index'))
