from flask import current_app
from flask_app import db, bcrypt
from flask_app.python.models import User, Modelo, Label, Atributo, Audio, Background, Fonte
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from lxml import etree
import cv2
import base64
import re
import numpy as np
from PIL import ImageFont
import glob2
import urllib
import requests
import subprocess
import uuid


def merge_transparent_images(background, foreground):
    alpha_background = background[:,:,3] / 255.0
    alpha_foreground = foreground[:,:,3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        background[:,:,color] = alpha_foreground * foreground[:,:,color] + \
            alpha_background * background[:,:,color] * (1 - alpha_foreground)

    # set adjusted alpha and denormalize back to 0-255
    background[:,:,3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255
    return background


def escape_texto(texto):
    return texto.translate(str.maketrans({"-":  r"\-",
              "]":  r"\]",
              "\\": r"\\",
              "^":  r"\^",
              "$":  r"\$",
              "*":  r"\*",
              ".":  r"\."}))


def add_texto_imagem(elemento, temp_file, posicao_trim, imagem=None):
    trim_largura, trim_altura = posicao_trim.split('+')[0].split('x')
    trim_x, trim_y = posicao_trim.split('+')[1:]
    trim_largura = int(trim_largura)
    trim_altura = int(trim_altura)
    trim_x = int(trim_x)
    trim_y = int(trim_y)
    imagem_elemento = np.zeros((elemento.max_altura, elemento.max_largura, 4))
    imagem_texto = cv2.cvtColor(cv2.imread(temp_file, cv2.IMREAD_UNCHANGED)[trim_y: trim_y+trim_altura, trim_x: trim_x+trim_largura, :], cv2.COLOR_BGR2RGBA)
    altura_texto = imagem_texto.shape[0]
    largura_texto = imagem_texto.shape[1]
    rescale = min(elemento.max_altura/altura_texto, elemento.max_largura/largura_texto)
    h_rescale, w_rescale = (int(rescale*altura_texto), int(rescale*largura_texto))
    imagem_texto = cv2.resize(imagem_texto, (w_rescale, h_rescale), interpolation=4)
    start_largura = int((elemento.max_largura - w_rescale)/2)
    start_altura = int((elemento.max_altura - h_rescale)/2)
    imagem_elemento[start_altura:start_altura+h_rescale, start_largura:start_largura+w_rescale] = imagem_texto
    x0 = elemento.x0_caixa
    y0 = elemento.y0_caixa
    os.system(f'rm -rf {temp_file}')
    if imagem is not None:
        imagem[y0:y0 + elemento.max_altura, x0: x0 + elemento.max_largura] = imagem_elemento
        return imagem
    else:
        return imagem_texto, (x0 + start_largura, y0 + start_altura)


def convert_hex_to_rgb(hex_color):
    hex_color = hex_color.split('#')[-1]
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_int(text):
    return int(text) if text.isdigit() else text


def sort_model_by_nome(dictionary):
    text = dictionary['nome']
    return [get_int(c) for c in re.split(r'(\d+)', text)]


def rot_matrix(a):
    return np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])


def generate_tela_image(tela_dict, modelo_dict, full_imagem_preview_path, watermark=False):
    svg_path = os.path.abspath(modelo_dict.get('svg'))

    ids_elementos = modelo_dict['atributos']

    dados_elementos = []
    for atributo in modelo_dict['atributos']:
        if atributo == 'imagem_produto':
            dados_elementos.append([tela_dict['imagem_produto'], tela_dict['imagem_produto_mask'], tela_dict['remover_fundo']])
        else:
            dados_elementos.append(tela_dict[atributo])

    assert len(ids_elementos) == len(dados_elementos)

    bkg = tela_dict['bkg_image']

    p = etree.XMLParser(huge_tree=True)

    root = etree.parse(svg_path, parser=p)

    root_propriedades = dict(root.getroot().attrib)
    largura = int(float(root_propriedades['viewBox'].split()[2]))
    altura = int(float(root_propriedades['viewBox'].split()[3]))
    shape = (largura, altura)

    gerar_imagem(root, ids_elementos, dados_elementos, bkg, shape, full_imagem_preview_path, watermark)


def generate_tela_animation(tela, modelo, full_animacao_path, fps=5, export='video', watermark=False):
    root = etree.parse(os.path.join(current_app.root_path, modelo['svg']), parser=etree.XMLParser(huge_tree=True))
    root_propriedades = dict(root.getroot().attrib)
    largura = int(float(root_propriedades['viewBox'].split()[2]))
    altura = int(float(root_propriedades['viewBox'].split()[3]))
    shape = (largura, altura)
    duracao = tela['duracao']

    dados_elementos = {}
    for atributo in modelo['atributos']:
        if tela.get(atributo):
            if atributo == 'imagem_produto':
                dados_elementos[atributo] = [tela['imagem_produto'], tela['imagem_produto_mask'], tela['remover_fundo']]
            else:
                dados_elementos[atributo] = tela[atributo]
        else:
            dados_elementos[atributo] = ''

    if tela.get('bkg_video'):
        fundo = tela['bkg_video']
    else:
        fundo = tela['bkg_image']

    cores = tela['cores']
    cores = cores.split(',')
    fontes = tela['fontes']
    fontes = fontes.split(',')

    gerar_animacao(root, dados_elementos, modelo, cores, fontes, fundo, shape, full_animacao_path, duration=duracao, export=export,  watermark=watermark, fps=fps)


def preprocess_tela(user_telas, user_artes_ids):

    preprocessed_telas = {}
    for arte_id in user_artes_ids:
        preprocessed_telas[arte_id] = []
        for tela in user_telas:
            if int(tela['arte_id']) == arte_id:
                preprocessed_telas[arte_id].append(tela)

    return preprocessed_telas


def populate_db():
    print("Dropando tabelas")
    db.drop_all()
    print("Criando tabelas")
    db.create_all()

    ############# Populando Usuarios #############
    print("Populando User")
    hashed_password = bcrypt.generate_password_hash('syncro!14').decode('utf-8')
    user1 = User(username='admin', email='admin@gmail.com', password=hashed_password, celular='1', cpf='1', permission=current_app.config['ACCESS_CONTROL']['admin'], customer_id='admin')

    hashed_password = bcrypt.generate_password_hash('syncro!14').decode('utf-8')
    user2 = User(username='guest', email='guest@gmail.com', password=hashed_password, celular='2', cpf='2', permission=current_app.config['ACCESS_CONTROL']['guest'], customer_id='guest')

    users = [user1, user2]

    ############# Populando Artes #############
    # art_id=1
    # artes = []
    for user in users:
    #     for i in range(1,3):
    #         arte = Arte(id=art_id, nome=f"Arte {i}")
    #         user.artes.append(arte)
    #         artes.append(arte)
    #         art_id=art_id+i
        db.session.add(user)

    ############# Populando Audios #############
    print("Populando Audios")
    caminhos = glob2.glob(os.path.join(current_app.root_path, 'static/audio/*.mp3'))
    sem_audio = Audio(nome='- Sem Musica -', caminho="")
    db.session.add(sem_audio)
    for caminho in caminhos:
        nome = caminho.split('.mp3')[0].split('/')[-1]
        audio = Audio(nome=nome, caminho=caminho.split(current_app.root_path)[-1].strip('/'))
        db.session.add(audio)

    ############# Populando Labels #############
    print("Populando Labels")
    label_produto = Label(nome='Produto')
    label_abertura_encerramento = Label(nome='Abertura/Encerramento')
    label_mensagem = Label(nome='Mensagem')
    label_apenas_fundo = Label(nome='Apenas Fundo')

    ############# Populando Atributos #############
    print("Populando Atributos")
    texto_nomeproduto = Atributo(nome='texto_nomeproduto')
    texto_preconormal = Atributo(nome='texto_preconormal')
    texto_precodesconto = Atributo(nome='texto_precodesconto')
    texto_porcentagemdesconto = Atributo(nome='texto_porcentagemdesconto')
    imagem_produto = Atributo(nome='imagem_produto')
    imagem_logo = Atributo(nome='imagem_logo')
    texto_site = Atributo(nome='texto_site')
    texto_nomeempresa = Atributo(nome='texto_nomeempresa')
    texto_telefone = Atributo(nome='texto_telefone')
    texto_email = Atributo(nome='texto_email')
    texto_endereco = Atributo(nome='texto_endereco')
    texto_mensagem = Atributo(nome='texto_mensagem')
    texto_facebook = Atributo(nome='texto_facebook')
    texto_instagram = Atributo(nome='texto_instagram')

    ############# Populando Fundos #############
    print("Populando Fundos")
    storage_path = current_app.config["STORAGE_APP"]

    bkg_type_dirs = glob2.glob(os.path.join(current_app.root_path, 'static/backgrounds_v2/videos/*'))
    for bkg_dir in bkg_type_dirs:
        bkg_type = bkg_dir.split('/')[-1]

        bkg_dirs = glob2.glob(os.path.join(bkg_dir, "*"))
        for bkg_dir in bkg_dirs:
            gif_path = os.path.join(storage_path, os.path.relpath(os.path.join(bkg_dir, os.path.basename(bkg_dir) + '.gif'), os.path.join(current_app.root_path, 'static')))
            png_path = os.path.join(storage_path, os.path.relpath(os.path.join(bkg_dir, os.path.basename(bkg_dir) + '.png'), os.path.join(current_app.root_path, 'static')))
            mp4_path = os.path.join(storage_path, os.path.relpath(os.path.join(bkg_dir, os.path.basename(bkg_dir) + '.mp4'), os.path.join(current_app.root_path, 'static')))

            bkg = Background(gif=gif_path, video=mp4_path, section=bkg_type, imagem=png_path, tipo='videos')

            db.session.add(bkg)

    bkg_type_dirs = glob2.glob(os.path.join(current_app.root_path, 'static/backgrounds_v2/imagens/*'))
    for bkg_dir in bkg_type_dirs:
        bkg_type = bkg_dir.split('/')[-1]

        images = glob2.glob(os.path.join(bkg_dir, "*"))
        for image in images:
            img_path = os.path.join(storage_path, os.path.relpath(image, os.path.join(current_app.root_path, 'static')))
            bkg = Background(gif=img_path, video=img_path, section=bkg_type, imagem=img_path, tipo='imagens')
            db.session.add(bkg)

    ############# Populando Fontes #############
    print("Populando Fontes")
    fontes_paths = glob2.glob(os.path.join(current_app.root_path, 'fonts/*'))
    fontes_nomes = [os.path.basename(fonte_path).split('.')[0] for fonte_path in fontes_paths]
    for fonte_path, fonte_nome in zip(fontes_paths, fontes_nomes):
        fonte = Fonte(nome=fonte_nome, caminho=os.path.relpath(fonte_path, current_app.root_path))
        db.session.add(fonte)

    ############# Populando Modelos #############
    print("Populando Modelos")
    json_arte0 = 'static/modelos/arte0/arte0.json'
    descricao_arte0 = 'Mostre uma imagem detalhada do seu produto.'

    json_arte1 = 'static/modelos/arte1/arte1.json'
    descricao_arte1 = 'Mostre o desconto aplicado ao produto.'

    json_arte2 = 'static/modelos/arte2/arte2.json'
    descricao_arte2 = 'Exiba seu logotipo e o endereço do seu site.'

    json_arte3 = 'static/modelos/arte3/arte3.json'
    descricao_arte3 = 'Seu produto e preço de forma descontraída.'

    json_arte4 = 'static/modelos/arte4/arte4.json'
    descricao_arte4 = 'Uma mensagem simples para o seu cliente.'

    json_arte5 = 'static/modelos/arte5/arte5.json'
    descricao_arte5 = 'Mostre seu produto com mensagem e informações de sua empresa.'

    json_arte6 = 'static/modelos/arte6/arte6.json'
    descricao_arte6 = 'Modelo com seu logotipo, endereço, telefone e email.'

    json_arte7 = 'static/modelos/arte7/arte7.json'
    descricao_arte7 = 'Uma mensagem elegante.'

    json_arte8 = 'static/modelos/arte8/arte8.json'
    descricao_arte8 = 'Abertura com logo e site em uma faixa transparente.'

    json_arte9 = 'static/modelos/arte9/arte9.json'
    descricao_arte9 = 'Exiba seu facebook, whatsapp e instagram.'

    json_arte10 = 'static/modelos/arte10/arte10.json'
    descricao_arte10 = 'Modelo clean. Contém nome, imagem e preço do produto.'

    json_arte11 = 'static/modelos/arte11/arte11.json'
    descricao_arte11 = 'Modelo Moderno com nome, imagem e preço do produto.'

    json_arte12 = 'static/modelos/arte12/arte12.json'
    descricao_arte12 = 'Modelo clean, mostra o desconto aplicado ao produto.'

    json_arte13 = 'static/modelos/arte13/arte13.json'
    descricao_arte13 = 'Tela sem modelo, apenas fundo.'

    json_arte14 = 'static/modelos/arte14/arte14.json'
    descricao_arte14 = 'Mostre seu produto com mensagem grande.'

    modelo_empty = Modelo(id=-1, nome='Sem modelo', descricao="", imagem='')
    modelo_empty.atributos.extend([])

    modelo0 = Modelo(nome='Modelo 0', descricao=descricao_arte0, json=json_arte0)
    modelo0.labels.extend([label_produto])
    modelo0.atributos.extend([imagem_produto])

    modelo1 = Modelo(nome='Modelo 1', descricao=descricao_arte1, json=json_arte1)
    modelo1.labels.extend([label_produto])
    modelo1.atributos.extend([texto_nomeproduto, texto_preconormal, texto_precodesconto, texto_porcentagemdesconto, imagem_produto, imagem_logo])

    modelo2 = Modelo(nome='Modelo 2', descricao=descricao_arte2, json=json_arte2)
    modelo2.labels.extend([label_abertura_encerramento])
    modelo2.atributos.extend([imagem_logo, texto_site])

    modelo3 = Modelo(nome='Modelo 3', descricao=descricao_arte3, json=json_arte3)
    modelo3.labels.extend([label_produto])
    modelo3.atributos.extend([texto_nomeproduto, texto_precodesconto, imagem_produto])

    modelo4 = Modelo(nome='Modelo 4', descricao=descricao_arte4, json=json_arte4)
    modelo4.labels.extend([label_mensagem])
    modelo4.atributos.extend([texto_mensagem])

    modelo5 = Modelo(nome='Modelo 5', descricao=descricao_arte5, json=json_arte5)
    modelo5.labels.extend([label_produto])
    modelo5.atributos.extend([texto_nomeproduto, texto_precodesconto, imagem_produto, texto_site, imagem_logo, texto_mensagem])

    modelo6 = Modelo(nome='Modelo 6', descricao=descricao_arte6, json=json_arte6)
    modelo6.labels.extend([label_abertura_encerramento])
    modelo6.atributos.extend([imagem_logo, texto_nomeempresa, texto_telefone, texto_email, texto_endereco])

    modelo7 = Modelo(nome='Modelo 7', descricao=descricao_arte7, json=json_arte7)
    modelo7.labels.extend([label_mensagem])
    modelo7.atributos.extend([texto_mensagem])

    modelo8 = Modelo(nome='Modelo 8', descricao=descricao_arte8, json=json_arte8)
    modelo8.labels.extend([label_abertura_encerramento])
    modelo8.atributos.extend([imagem_logo, texto_site])

    modelo9 = Modelo(nome='Modelo 9', descricao=descricao_arte9, json=json_arte9)
    modelo9.labels.extend([label_abertura_encerramento])
    modelo9.atributos.extend([imagem_logo, texto_site, texto_nomeempresa, texto_facebook, texto_instagram, texto_telefone])

    modelo10 = Modelo(nome='Modelo 10', descricao=descricao_arte10, json=json_arte10)
    modelo10.labels.extend([label_produto])
    modelo10.atributos.extend([texto_nomeproduto, texto_precodesconto, imagem_produto, imagem_logo])

    modelo11 = Modelo(nome='Modelo 11', descricao=descricao_arte11, json=json_arte11)
    modelo11.labels.extend([label_produto])
    modelo11.atributos.extend([texto_nomeproduto, texto_precodesconto, imagem_produto, imagem_logo])

    modelo12 = Modelo(nome='Modelo 12', descricao=descricao_arte12, json=json_arte12)
    modelo12.labels.extend([label_produto])
    modelo12.atributos.extend([texto_nomeproduto, texto_preconormal, texto_precodesconto, texto_porcentagemdesconto, imagem_produto])

    modelo13 = Modelo(nome='Apenas Fundo', descricao=descricao_arte13, json=json_arte13)
    modelo13.labels.extend([label_apenas_fundo])
    modelo13.atributos.extend([])

    modelo14 = Modelo(nome='Modelo 14', descricao=descricao_arte14, json=json_arte14)
    modelo14.labels.extend([label_produto])
    modelo14.atributos.extend([texto_nomeproduto, texto_precodesconto, imagem_produto, texto_site, imagem_logo, texto_mensagem])

    db.session.add(modelo_empty)
    db.session.add(modelo0)
    db.session.add(modelo1)
    db.session.add(modelo2)
    db.session.add(modelo3)
    db.session.add(modelo4)
    db.session.add(modelo5)
    db.session.add(modelo6)
    db.session.add(modelo7)
    db.session.add(modelo8)
    db.session.add(modelo9)
    db.session.add(modelo10)
    db.session.add(modelo11)
    db.session.add(modelo12)
    db.session.add(modelo13)
    db.session.add(modelo14)


    ############# Populando Telas #############
    # j=0
    # for tela_id, modelo_id in zip(range(1,3), {-1,1,2}):
    #     tela = Tela(id=tela_id, posicao=j, modelo_id=modelo_id, nome=f"Tela {i}", arte_id=random.choice(artes).id, nome_produto=f"Cebola {i}",
    #     imagem_preview=imagem1, preco_normal=f"R${i}00,00", preco_desconto=f"R${i}0,00")
    #     j+=1
    #     db.session.add(tela)

    # j=0
    # for tela_id, modelo_id in zip(range(3,5), {-1,1,2}):
    #     tela = Tela(id=tela_id, posicao=j, modelo_id=modelo_id, nome=f"Tela {i}", arte_id=random.choice(artes).id, nome_produto=f"Cebola {i}",
    #     imagem_preview=imagem2, preco_normal=f"R${i}00,00", preco_desconto=f"R${i}0,00")
    #     j+=1
    #     db.session.add(tela)

    # j=0
    # for tela_id, modelo_id in zip(range(5,6), {-1,1,2}):
    #     tela = Tela(id=tela_id, posicao=j, modelo_id=modelo_id, nome=f"Tela {i}", arte_id=random.choice(artes).id, nome_produto=f"Cebola {i}",
    #     imagem_preview=imagem3, preco_normal=f"R${i}00,00", preco_desconto=f"R${i}0,00")
    #     j+=1
    #     db.session.add(tela)

    # j=0
    # for tela_id, modelo_id in zip(range(6,10), {-1,1,2}):
    #     tela = Tela(id=tela_id, posicao=j, modelo_id=modelo_id, nome=f"Tela {i}", arte_id=random.choice(artes).id, nome_produto=f"Cebola {i}",
    #     imagem_preview=imagem4, preco_normal=f"R${i}00,00", preco_desconto=f"R${i}0,00")
    #     j+=1
    #     db.session.add(tela)
    print('Commitando DB')
    db.session.commit()
    print('Commitado!')


class elemento_imagem:
    def __init__(self, root, id_elemento, caminho_imagem, caminho_mascara, remover_fundo=True):
        self.status = True
        self.root = root
        self.id_elemento = id_elemento
        self.caminho_imagem = caminho_imagem
        self.caminho_mascara = caminho_mascara
        self.remover_fundo = remover_fundo

        props = self.propriedades_elemento()

        if props is False:
            self.status = False
        else:
            self.x0_caixa = props['x0_caixa']
            self.y0_caixa = props['y0_caixa']
            self.cx_caixa = props['cx_caixa']
            self.cy_caixa = props['cy_caixa']
            self.max_largura = props['max_largura']
            self.max_altura = props['max_altura']
            self.rotacao = props['rotacao']
            self.alinhamento = props['alinhamento']

    def propriedades_elemento(self):

        root_propriedades = dict(self.root.getroot().attrib)
        largura = int(float(root_propriedades['viewBox'].split()[2]))
        altura = int(float(root_propriedades['viewBox'].split()[3]))

        elemento = self.root.xpath(f'//*[@id="caixa_{self.id_elemento}"]')
        if len(elemento) == 0:
            return False
        else:
            elemento = dict(elemento[0].attrib)
            cor_alinhamento = (re.search(r'fill:(.*?);', elemento['style']).group(1)).upper()
            if cor_alinhamento == '#008000':
                alinhamento = 'CC'
            elif cor_alinhamento == '#FFFF00':
                alinhamento = 'TL'
            max_x = float(elemento['width'])/largura
            max_y = float(elemento['height'])/altura
            x0 = float(elemento['x'])/largura
            y0 = float(elemento['y'])/altura
            centro_x = (float(elemento['x']) + float(elemento['width'])/2)/largura
            centro_y = (float(elemento['y']) + float(elemento['height'])/2)/altura
            if 'transform' in elemento.keys():
                rotation = int(float(re.search('rotate\((.*?)\)', elemento['transform']).group(1)))
            else:
                rotation = 0
            prop = {'x0_caixa': x0, 'y0_caixa': y0, 'cx_caixa': centro_x, 'cy_caixa': centro_y,
                    'max_largura': max_x, 'max_altura': max_y, 'rotacao': rotation, 'alinhamento': alinhamento}
            return prop


class elemento_texto:
    def __init__(self, root, id_elemento, texto_elemento):
        self.status = True
        self.root = root
        self.id_elemento = id_elemento
        self.texto = texto_elemento

        resposta = self.extrai_fonte_do_elemento()
        if resposta is not False:
            nome_fonte, cor_fonte, tamanho_fonte_original = resposta

            props = self.propriedades_elemento()
            caminho_fonte_texto = self.busca_caminho_fonte(nome_fonte)
            regex = re.compile('[^a-zA-Z]')
            melhor_nome_fonte = regex.sub('', caminho_fonte_texto.split('/')[-1].split('.')[0]).lower()
            fonts = TextClip.list('font')
            index = [idx for idx, font_name in enumerate(fonts) if (melhor_nome_fonte in regex.sub('', font_name).lower())][0]
            melhor_nome_fonte = fonts[index]

            self.tamanho_fonte_original = tamanho_fonte_original
            self.cor_fonte = cor_fonte
            self.x0_caixa = props['x0_caixa']
            self.y0_caixa = props['y0_caixa']
            self.cx_caixa = props['cx_caixa']
            self.cy_caixa = props['cy_caixa']
            self.max_largura = props['max_largura']
            self.max_altura = props['max_altura']
            self.rotacao = props['rotacao']
            self.alinhamento = props['alinhamento']
            self.nome_fonte = melhor_nome_fonte
            self.caminho_fonte = caminho_fonte_texto

            self.atualizar_informacoes()
        else:
            self.status = False

    def atualizar_informacoes(self):
        tamanho_fonte, dimensoes_texto = self.melhor_tamanho_fonte()

        self.largura_texto, self.altura_texto = dimensoes_texto

        self.tamanho_fonte = tamanho_fonte
        self.dimensoes_texto = dimensoes_texto

        if self.alinhamento == "CC":
            posicao_x = int(self.cx_caixa - self.largura_texto/2)
            posicao_y = int(self.y0_caixa)
        elif self.alinhamento == "TL":
            posicao_x = int(self.x0_caixa)
            posicao_y = int(self.y0_caixa)

        self.posicao_x = posicao_x
        self.posicao_y = posicao_y

    def propriedades_elemento(self):
        elemento = self.root.xpath(f'//*[@id="caixa_{self.id_elemento}"]')
        if len(elemento) == 0:
            return False
        else:
            elemento = dict(elemento[0].attrib)
            cor_alinhamento = (re.search(r'fill:(.*?);', elemento['style']).group(1)).upper()
            if cor_alinhamento == '#008000':
                alinhamento = 'CC'
            elif cor_alinhamento == '#FFFF00':
                alinhamento = 'TL'
            max_x = round(float(elemento['width']))
            max_y = round(float(elemento['height']))
            x0 = round(float(elemento['x']))
            y0 = round(float(elemento['y']))
            centro_x = round(float(elemento['x']) + float(elemento['width'])/2)
            centro_y = round(float(elemento['y']) + float(elemento['height'])/2)
            if 'transform' in elemento.keys():
                rotation = int(float(re.search('rotate\((.*?)\)', elemento['transform']).group(1)))
            else:
                rotation = 0
            prop = {'x0_caixa': x0, 'y0_caixa': y0, 'cx_caixa': centro_x, 'cy_caixa': centro_y,
                    'max_largura': max_x, 'max_altura': max_y, 'rotacao': rotation, 'alinhamento': alinhamento}
            return prop

    def extrai_fonte_do_elemento(self):
        elemento = self.root.xpath(f'//*[@id="{self.id_elemento}"]')
        if len(elemento) == 0:
            return False
        else:
            sub_elementos = [elem for elem in elemento[0].findall('*') if 'style' in dict(elem.attrib)]
            if len(sub_elementos) == 0:
                sub_elementos = elemento

            if len(sub_elementos) > 0:
                sub_elemento = dict(sub_elementos[0].attrib)
                nome_fonte_regex = re.search(r'font-family:(.*?);', sub_elemento['style'])
                if nome_fonte_regex is None:
                    nome_fonte_regex = re.search(r'font-family:(.*?);', dict(elemento[0].attrib)['style'])
                nome_fonte = nome_fonte_regex.group(1)

                cor_fonte_regex = re.search(r'fill:(.*?);', sub_elemento['style'])
                if cor_fonte_regex is None:
                    cor_fonte_regex = re.search(r'fill:(.*?);', dict(elemento[0].attrib)['style'])
                if cor_fonte_regex:
                    cor_fonte = cor_fonte_regex.group(1)
                else:
                    cor_fonte = '#ffff00'
                tamanho_fonte = round(float(re.search(r'font-size:(.*?)px;', dict(elemento[0].attrib)['style']).group(1)))
                return nome_fonte, cor_fonte, tamanho_fonte

    def busca_caminho_fonte(self, nome_fonte):
        search_string = os.path.join('/usr/local/share/fonts/', '*' + '*'.join(re.split(' |-|_', re.sub('[^A-Za-z0-9]+', '*', nome_fonte))) + '*')
        caminho_fonte_texto = glob2.glob(search_string, case_sensitive=False)
        if len(caminho_fonte_texto) == 0:
            return False
        else:
            return caminho_fonte_texto[0]

    def melhor_tamanho_fonte(self):
        """
        Encontra o melhor tamanho da fonte baseado em um comprimento maximo.
        """
        dimensoes_texto = (0, 0)
        tamanho_fonte_largura = 0
        while dimensoes_texto[0] < self.max_largura:
            tamanho_fonte_largura += 1
            dimensoes_texto = ImageFont.truetype(self.caminho_fonte, tamanho_fonte_largura).getsize(self.texto)
        tamanho_fonte_largura = tamanho_fonte_largura - 1

        dimensoes_texto = 0
        tamanho_fonte_altura = 0
        while dimensoes_texto < self.max_altura:
            tamanho_fonte_altura += 1
            font = ImageFont.truetype(self.caminho_fonte, tamanho_fonte_altura)
            ascent, descent = font.getmetrics()
            (width, baseline), (offset_x, offset_y) = font.font.getsize(self.texto)
            dimensoes_texto = ascent - offset_y
        tamanho_fonte_altura = tamanho_fonte_altura - 1

        melhor_tamanho = min(tamanho_fonte_largura, tamanho_fonte_altura)
        dimensoes_texto = ImageFont.truetype(self.caminho_fonte, melhor_tamanho).getsize(self.texto)
        return melhor_tamanho, dimensoes_texto

    def substitui_texto_do_elemento(self):
        root_elemento = self.root.xpath(f'//*[@id="{self.id_elemento}"]')
        if len(root_elemento) == 0:
            return False
        else:
            root_elemento[0].attrib['x'] = str.encode(str(self.posicao_x))
            root_elemento[0].attrib['style'] = re.sub(r'font-size:(.*?)px;', f'font-size:{self.tamanho_fonte}px;', root_elemento[0].attrib['style'])
            span_elemento = [elem for elem in root_elemento[0].findall('*') if 'style' in dict(elem.attrib)]
            if len(span_elemento) > 0:
                span_elemento[0].attrib['x'] = str.encode(str(self.posicao_x))
                span_elemento[0].text = self.texto
                return

    def clip_do_elemento_texto(self):
        txt_clip = (TextClip(self.texto,
            fontsize=self.tamanho_fonte,
            color=self.cor_fonte,
            stroke_width=0,
            font=self.nome_fonte,
            kerning=0,
            print_cmd=False)).set_position((self.posicao_x, self.posicao_y))
        return txt_clip


def url_para_numpy(imagem_url):
    req = urllib.request.urlopen(imagem_url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    imagem = cv2.cvtColor(cv2.imdecode(arr, -1), cv2.COLOR_BGR2RGB)
    return imagem


def vortex(screenpos, i, nletters):
    d = lambda t: 1.0/(0.3+t**10)  # damping
    a = i*np.pi / nletters  # angle of the movement
    v = rot_matrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos+400*d(t)*rot_matrix(0.5*d(t)*a).dot(v)


def cascade(screenpos, i, nletters):
    v = np.array([0, -1])
    d = lambda t: -500 if t < 0 else abs(np.sinc(t)/(1+t**4))
    return lambda t: screenpos+v*1500*d(t-0.01*i)


def arrive(screenpos, i, nletters):
    v = np.array([-1, 0])
    d = lambda t: max(0, 3-3*t)
    return lambda t: screenpos-1500*v*d(t-0.01*i)


def vortexout(screenpos, i, nletters):
    d = lambda t : max(0, t)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rot_matrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos+1000*d(t-0.01*i)*rot_matrix(-0.02*d(t)*a).dot(v)


def moveLetters(letters, funcpos):
    return [letter.set_pos(funcpos(letter.screenpos, i, len(letters))) for i, letter in enumerate(letters)]


def get_mask(img):
    string = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    inference_dict = {
        "instances": [
            {'img': string}
            ]}

    response = requests.post('https://u2net-biokhhlwmq-uc.a.run.app/predict', json=inference_dict)

    nparr = np.fromstring(base64.b64decode(response.json()['predictions'][0]), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    return img


def processa_mascara(obj_imagem, shape_frame):

    h_frame, w_frame = shape_frame

    imagem_produto = np.zeros((*shape_frame, 3), dtype=np.uint8)
    mascara_produto = np.zeros((*shape_frame, 3), dtype=np.uint8)

    imagem = cv2.imread(obj_imagem.caminho_imagem, cv2.IMREAD_UNCHANGED)
    mascara = None
    if obj_imagem.remover_fundo is True:
        if imagem.shape[-1] == 4 and len(np.unique(imagem[..., -1])) > 1:
            mascara = imagem[..., -1]
            imagem = imagem[..., :-1]
        else:
            if obj_imagem.caminho_mascara:
                mascara = cv2.imread(obj_imagem.caminho_mascara, cv2.IMREAD_GRAYSCALE)
                _, mascara_binary = cv2.threshold(mascara, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                if (int(cv2.__version__[0]) > 3):
                    contours, hierarchy = cv2.findContours(mascara_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                else:
                    im2, contours, hierarchy = cv2.findContours(mascara_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)

                mascara = mascara[y:y+h, x:x+w]
                imagem = imagem[y:y+h, x:x+w]

    if mascara is None:
        mascara = (np.ones_like(imagem[..., 0])*255).astype(np.uint8)

    imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

    h_pos_corte, w_pos_corte = imagem.shape[:2]

    rescale = min((obj_imagem.max_altura*h_frame)/h_pos_corte, (obj_imagem.max_largura*w_frame)/w_pos_corte)

    h_rescale, w_rescale = (int(rescale*h_pos_corte), int(rescale*w_pos_corte))
    imagem_rescale = cv2.resize(imagem, (w_rescale, h_rescale), interpolation=4)
    mascara_rescale = cv2.resize(mascara, (w_rescale, h_rescale), interpolation=4)

    if len(mascara_rescale.shape) == 2:
        mascara_rescale = np.repeat(mascara_rescale[..., None], 3, axis=-1)

    start_pos_imagem = (int((obj_imagem.cy_caixa*h_frame)-h_rescale/2), int((obj_imagem.cx_caixa*w_frame) - w_rescale/2))
    fim_pos_imagem = (int(start_pos_imagem[0] + h_rescale), int(start_pos_imagem[1] + w_rescale))

    imagem_produto[start_pos_imagem[0]:fim_pos_imagem[0], start_pos_imagem[1]:fim_pos_imagem[1]] = imagem_rescale
    mascara_produto[start_pos_imagem[0]:fim_pos_imagem[0], start_pos_imagem[1]:fim_pos_imagem[1]] = mascara_rescale

    return imagem_produto, mascara_produto


def gerar_imagem(root, ids_elementos, dados_elementos, caminho_background, shape, output, watermark=True):
    
    ids_elementos_texto = [id_elemento for id_elemento in ids_elementos if id_elemento.startswith('texto')]
    dados_elementos_texto = [dado_elemento for id_elemento, dado_elemento in zip(ids_elementos, dados_elementos) if id_elemento.startswith('texto')]

    ids_elementos_imagem = [id_elemento for id_elemento in ids_elementos if id_elemento.startswith('imagem')]
    dados_elementos_imagem = [dado_elemento for id_elemento, dado_elemento in zip(ids_elementos, dados_elementos) if id_elemento.startswith('imagem')]

    for id_elemento, dado_elemento in zip(ids_elementos_texto, dados_elementos_texto):
        id_elemento_split = id_elemento.split('_')
        
        obj_elemento_texto = elemento_texto(root, id_elemento, dado_elemento)
        if obj_elemento_texto.status == True:
            obj_elemento_texto.substitui_texto_do_elemento()


    with open(caminho_background, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    root_elemento = root.xpath(f'//*[@id="fundo"]')
    root_elemento[0].attrib['{http://www.w3.org/1999/xlink}href'] = 'data:image/png;base64,' + encoded_string.decode("utf-8")
            
    codigo_svg = etree.tostring(root)
    file = open("temp.svg", 'wb') 
    file.write(codigo_svg) 
    file.close()
    os.system(f'inkscape temp.svg -o {output}')
    os.system(f'rm temp.svg')
    
    if len(ids_elementos_imagem) > 0:
        for id_elemento, dado_elemento in zip(ids_elementos_imagem, dados_elementos_imagem):
            frame = cv2.resize(cv2.cvtColor(cv2.imread(output), cv2.COLOR_BGR2RGB), shape)
            id_elemento_split = id_elemento.split('_')

            if id_elemento_split[1] == 'produto':
                caminho_imagem = dado_elemento[0]
                caminho_mascara = dado_elemento[1]
                remover_fundo = dado_elemento[2]
                if caminho_imagem is None or caminho_mascara is None:
                    continue
                caminho_imagem = os.path.join(current_app.root_path, caminho_imagem)
                caminho_mascara = os.path.join(current_app.root_path, caminho_mascara)
                obj_imagem = elemento_imagem(root, id_elemento, caminho_imagem, caminho_mascara, remover_fundo)

            elif id_elemento_split[1] == 'logo':
                caminho_imagem = dado_elemento
                if caminho_imagem is None:
                    continue
                caminho_imagem = os.path.join(current_app.root_path, caminho_imagem)
                obj_imagem = elemento_imagem(root, id_elemento, caminho_imagem, None)

            if obj_imagem.status == True:
                imagem_produto, mascara_produto = processa_mascara(obj_imagem, shape)

                alpha = mascara_produto[..., 0] / 255.0
                result = np.zeros_like(frame)
                result[:, :, 0] = (1. - alpha) * frame[:, :, 0] + alpha * imagem_produto[:, :, 0]
                result[:, :, 1] = (1. - alpha) * frame[:, :, 1] + alpha * imagem_produto[:, :, 1]
                result[:, :, 2] = (1. - alpha) * frame[:, :, 2] + alpha * imagem_produto[:, :, 2]
                cv2.imwrite(output, cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    
    if watermark == True:
        caminho_watermark = os.path.join(current_app.root_path, 'static/imgs/watermark.png')
        subprocess.run(["composite", "-dissolve", "15%", "-tile", caminho_watermark, output, output])
                

def gerar_animacao(root, dados_elementos, modelo, cores, fontes, caminho_background, shape, output, export, fps=10, duration=7, watermark=True, razao_sombra = 0.06):
    imagemagick_sobra = 1.3
    if watermark == True:
        caminho_watermark = os.path.join(current_app.root_path, 'static/imgs/watermark.png')
        clip_watermark = ImageClip(caminho_watermark).resize(shape).set_duration(duration).set_opacity(.15)

    if caminho_background.lower().endswith(('.mp4', '.avi')):
        clip_background = VideoFileClip(caminho_background).resize(shape).set_duration(duration)
    elif caminho_background.lower().endswith(('.jpg', '.jpeg', '.png')):
        clip_background = ImageClip(caminho_background).resize(shape).set_duration(duration)
    clips = []
    arte_num = modelo['arte_num']
    for camada in modelo['camadas']:
        camada_level = camada['level']
        if camada['tipo'] == 'objeto':
            img_path = f'static/modelos/arte{arte_num}/camada{camada_level}/arte{arte_num}_camada{camada_level}.png'
            img_path = os.path.join(current_app.root_path, img_path)
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            classe_cor_camada = camada.get('cor')
            if classe_cor_camada is not None:
                cor = cores[int(classe_cor_camada)]
                r, g, b = convert_hex_to_rgb(cor)
                img[..., 0] = r
                img[..., 1] = g
                img[..., 2] = b
            clip = ImageClip(img)
            clip.screenpos = np.array((0, 0))
            clips.append(clip)
        if camada['tipo'] == 'texto':
            classe_cor_camada = camada.get('cor')
            classe_fonte_camada = camada.get('fonte')
            cor = cores[int(classe_cor_camada)]
            nome_fonte_arquivo = fontes[int(classe_fonte_camada)]
            regex = re.compile('[^a-zA-Z]')
            nome_fonte_sistema = regex.sub('', nome_fonte_arquivo.split('/')[-1].split('.')[0]).lower()
            fonts = TextClip.list('font')
            index = [idx for idx, font_name in enumerate(fonts) if (nome_fonte_sistema in regex.sub('', font_name).lower())][0]
            nome_fonte_sistema = fonts[index]
            imagem_textos = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)
            imagem_sombras = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)
            for elemento_dict in camada['elementos']:
                dado_elemento = dados_elementos[elemento_dict['id_elemento']]
                if dado_elemento:
                    id_elemento_split = elemento_dict['id_elemento'].split('_')
                    elemento = elemento_texto(root, elemento_dict['id_elemento'], dado_elemento)
                    elemento.cor_fonte = cor
                    elemento.caminho_fonte = elemento.busca_caminho_fonte(nome_fonte_arquivo)
                    elemento.nome_fonte = nome_fonte_sistema
                    elemento.atualizar_informacoes()
                    texto_tratado = escape_texto(elemento.texto)
                    largura = int(imagemagick_sobra*elemento.max_largura)
                    altura = int(imagemagick_sobra*elemento.max_altura)
                    if id_elemento_split[1] == 'mensagem':
                        gravity = 'center'
                        comando_fonte = f'''convert -background transparent -size {largura}x{altura} -fill "{elemento.cor_fonte}" -gravity center -font {elemento.nome_fonte} caption:"{texto_tratado}" -format "%[caption:pointsize]\n" info:'''
                        tamanho_fonte = int(float(subprocess.check_output(comando_fonte, shell=True).decode().rstrip()))
                        tamanho_fonte = tamanho_fonte - razao_sombra*tamanho_fonte
                        sombra_offset = int(razao_sombra*tamanho_fonte)
                        
                        temp_file = str(uuid.uuid4()) + '.png'
                        comando = f'''convert -background transparent -size {largura}x -fill "{elemento.cor_fonte}" -stroke transparent -strokewidth {sombra_offset} -pointsize {tamanho_fonte} -gravity center -font {elemento.nome_fonte} caption:"{texto_tratado}" {temp_file}'''
                        os.system(comando)
                        
                        temp_file_sombra = str(uuid.uuid4()) + '.png'
                        # comando_sombra = f'''convert -background transparent -size {elemento.max_largura}x{elemento.max_altura}! -gravity northwest -splice {sombra_offset}x{sombra_offset} -fill "{elemento.cor_fonte}" -gravity {gravity} -font {elemento.nome_fonte} caption:"{texto_tratado}" -crop {elemento.max_largura}x{elemento.max_altura}+0+0 +repage {temp_file_sombra}'''
                        comando_sombra = f'''convert -background transparent -size {largura}x -fill transparent -stroke black -strokewidth {sombra_offset} -pointsize {tamanho_fonte} -gravity {gravity} -font {elemento.nome_fonte} caption:"{texto_tratado}" {temp_file_sombra}'''
                        os.system(comando_sombra)
                        
                        comando_trim = f'''convert {temp_file_sombra} -format "%@" info:'''
                        posicao_trim = subprocess.check_output(comando_trim, shell=True).decode().rstrip()

                        imagem_texto, (start_largura, start_altura) = add_texto_imagem(elemento, temp_file, posicao_trim)
                        imagem_sombra, _ = add_texto_imagem(elemento, temp_file_sombra, posicao_trim)
                        
                    else:
                        if elemento.alinhamento == "CC":
                            gravity = 'center'
                        elif elemento.alinhamento == "TL":
                            gravity = 'northwest'
                            
                        comando_fonte = f'''convert -background transparent -size {largura}x{altura} -fill "{elemento.cor_fonte}" -gravity {gravity} -font {elemento.nome_fonte} label:"{texto_tratado}" -format "%[label:pointsize]\n" info:'''
                        tamanho_fonte = int(float(subprocess.check_output(comando_fonte, shell=True).decode().rstrip()))
                        tamanho_fonte = tamanho_fonte - razao_sombra*tamanho_fonte
                        sombra_offset = int(razao_sombra*tamanho_fonte)
                            
                        temp_file = str(uuid.uuid4()) + '.png'
                        comando = f'''convert -background transparent -size {largura}x{altura} -fill "{elemento.cor_fonte}" -stroke transparent -strokewidth {sombra_offset} -pointsize {tamanho_fonte} -gravity {gravity} -font {elemento.nome_fonte} label:"{texto_tratado}" {temp_file}'''
                        os.system(comando)
                        
                        temp_file_sombra = str(uuid.uuid4()) + '.png'
                        # comando_sombra = f'''convert -background transparent -size {elemento.max_largura}x{elemento.max_altura}! -gravity northwest -splice {sombra_offset}x{sombra_offset} -fill "{elemento.cor_fonte}" -gravity {gravity} -font {elemento.nome_fonte} label:"{texto_tratado}" -crop {elemento.max_largura}x{elemento.max_altura}+0+0 +repage {temp_file_sombra}'''
                        comando_sombra = f'''convert -background transparent -size {largura}x{altura} -fill transparent -stroke black -strokewidth {sombra_offset} -pointsize {tamanho_fonte} -gravity {gravity} -font {elemento.nome_fonte} label:"{texto_tratado}" {temp_file_sombra}'''
                        os.system(comando_sombra)

                        comando_trim = f'''convert {temp_file_sombra} -format "%@" info:'''
                        posicao_trim = subprocess.check_output(comando_trim, shell=True).decode().rstrip()

                        imagem_texto, (start_largura, start_altura) = add_texto_imagem(elemento, temp_file, posicao_trim)
                        imagem_sombra, _ = add_texto_imagem(elemento, temp_file_sombra, posicao_trim)
                    
                    imagem_elemento = merge_transparent_images(imagem_sombra, imagem_texto)
                    clip = ImageClip(imagem_elemento)
                    clip = clip.set_position((start_largura, start_altura))
                    clip.screenpos = np.array((start_largura, start_altura))
                    clips.append(clip)

        if camada['tipo'] == 'imagem':
            for elemento_dict in camada['elementos']:
                id_elemento = elemento_dict['id_elemento']
                id_elemento_split = id_elemento.split('_')
                dado_elemento = dados_elementos[id_elemento]
                if dado_elemento == '':
                    continue
                if id_elemento_split[1] == 'produto':
                    caminho_imagem = dado_elemento[0]
                    caminho_mascara = dado_elemento[1]
                    remover_fundo = dado_elemento[2]
                    if caminho_imagem is None or caminho_mascara is None:
                        continue
                    caminho_imagem = os.path.join(current_app.root_path, caminho_imagem)
                    caminho_mascara = os.path.join(current_app.root_path, caminho_mascara)

                    obj_imagem = elemento_imagem(root, id_elemento, caminho_imagem, caminho_mascara, remover_fundo)

                elif id_elemento_split[1] == 'logo':
                    caminho_imagem_logo = dado_elemento
                    if caminho_imagem_logo is None:
                        continue
                    obj_imagem = elemento_imagem(root, id_elemento, caminho_imagem_logo, None)

                if obj_imagem.status == True:
                    imagem_produto, mascara_produto = processa_mascara(obj_imagem, shape)
                    mascara_produto = (mascara_produto).astype(np.uint8)
                    mask_clip = ImageClip(mascara_produto, ismask=True)
                    clip_imagem = (ImageClip(imagem_produto).set_duration(clip_background.duration).set_mask(mask_clip))
                    clip_imagem = clip_imagem.set_position((obj_imagem.x0_caixa, obj_imagem.y0_caixa))
                    clip_imagem.screenpos = np.array((obj_imagem.x0_caixa, obj_imagem.y0_caixa))
                    clips.append(clip_imagem)

    clips = moveLetters(clips, vortex)
    clips = [clip_background, *clips]

    if watermark == True:
        clips.append(clip_watermark)
        
    final_clip = CompositeVideoClip(clips=clips, size=shape[:2])
    final_clip.duration = clip_background.duration
    
    if export == 'imagem':
        final_clip.save_frame(output, duration/2)
    if export == 'video':
        final_clip.write_videofile(output, fps=fps, codec='libx264', preset='ultrafast')

def price_str_to_float(price):
    res = re.sub("[^0-9|^,|^.]", "", price).replace(',', '.').split('.')
    if len(res[-1]) <= 2 and len(res[-1]) > 0 and len(res) > 1:
        value = int(''.join(res[:-1])) + int(''.join(res[-1]))/(10**len(res[-1]))
    else:
        value = int(''.join(res))
    return value

def get_discount(higher, lower):
    higher = price_str_to_float(higher)
    lower = price_str_to_float(lower)
    return '%i%%'%(((higher - lower)/higher)*100)