import os, random

from flask import Blueprint, render_template, request, redirect, url_for, Response
from .models import Obra, Foto
from . import db
from datetime import datetime

main = Blueprint('main', __name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Rota para a home "/"
@main.route('/')
def home():
    return render_template('home.html')

# Rota GET para o CRUD de obras e fotos
@main.route('/crud', methods=['GET'])
def obra_crud():
    obras = Obra.query.all()
    for obra in obras:
        obra.fotos = Foto.query.filter_by(obra_id=obra.id).all()  # Carregue as fotos associadas
    return render_template('obra_crud.html', obras=obras)


# Rota GET para exibir fotos e dados da obra
@main.route('/obra/<int:obra_id>', methods=['GET'])
def obra_view(obra_id):
    obra = Obra.query.get_or_404(obra_id)
    fotos = Foto.query.filter_by(obra_id=obra_id).all()
    return render_template('obra_view.html', obra=obra, fotos=fotos)

# Rota POST para criar/atualizar uma obra
@main.route('/obra', methods=['POST'])
def create_obra():
    nome = request.form['nome']
    
    # Convertendo a string de data para um objeto datetime
    data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
    
    # Verificando se a data prevista de término foi enviada e convertendo-a
    data_prevista_termino = request.form.get('data_prevista_termino')
    if data_prevista_termino:
        data_prevista_termino = datetime.strptime(data_prevista_termino, '%Y-%m-%d').date()
    else:
        data_prevista_termino = None
    
    administracao = request.form.get('tipo_de_obra')


    # Criando uma nova instância de Obra
    obra = Obra(nome=nome, data_inicio=data_inicio, 
                data_prevista_termino=data_prevista_termino,
                concluida=False, tipo_de_obra=administracao)
    
    # Salvando no banco de dados
    db.session.add(obra)
    db.session.commit()

    # Redirecionando para a visualização da obra criada
    return redirect(url_for('main.obra_crud'))


@main.route('/obra/edit/<int:obra_id>', methods=['GET', 'POST'])
def update_obra(obra_id):
    obra = Obra.query.get_or_404(obra_id)
    if request.method == 'POST':
        nome = request.form['nome']
        tipo_de_obra = int(request.form['tipo_de_obra'])
        data_inicio = datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date()
        data_prevista_termino = request.form.get('data_prevista_termino') or None
        if data_prevista_termino:
            data_prevista_termino = datetime.strptime(data_prevista_termino, '%Y-%m-%d').date()
        data_termino = request.form.get('data_termino') or None
        if data_termino:
            data_termino = datetime.strptime(data_termino, '%Y-%m-%d').date()
        concluida = request.form.get('concluida') == 'on'

        obra.nome = nome
        obra.tipo_de_obra = tipo_de_obra
        obra.data_inicio = data_inicio
        obra.data_prevista_termino = data_prevista_termino
        obra.data_termino = data_termino
        obra.concluida = concluida
        
        # Salvar novas fotos
        nova_foto = request.files.getlist('nova_foto')  # Permite múltiplos uploads
        for file in nova_foto:
            if file and allowed_file(file.filename):  # Verifique se o arquivo é válido
                foto = Foto(foto=file.read(), tipo=0, obra=obra)  # Ajuste o tipo conforme necessário
                db.session.add(foto)
        
        db.session.commit()
        return redirect(url_for('main.obra_crud'))
    
# Serve a foto
@main.route('/foto/<int:foto_id>')
def serve_foto(foto_id):
    foto = Foto.query.get_or_404(foto_id)  # Busca a foto pelo ID
    return Response(foto.foto, mimetype='image/jpeg')  # Ajuste o mimetype conforme necessário


#Rota para deletar foto
@main.route('/delete_foto/<int:foto_id>', methods=['POST'])
def delete_foto(foto_id):
    foto = Foto.query.get_or_404(foto_id)  # Busca a foto pelo ID
    obra_id = foto.obra_id  # Obtém o ID da obra associada

    # Remove a foto do banco de dados
    db.session.delete(foto)
    db.session.commit()

    # Redireciona para a página de gerenciamento de obras
    return redirect(url_for('main.obra_crud'))


# Rota POST para criar/atualizar fotos de obra
@main.route('/foto', methods=['POST'])
def create_foto():
    foto = request.files['foto'].read()
    tipo = request.form['tipo']
    obra_id = request.form['obra_id']

    nova_foto = Foto(foto=foto, tipo=tipo, obra_id=obra_id)
    db.session.add(nova_foto)
    db.session.commit()

    return redirect(url_for('main.obra_view', obra_id=obra_id))


# Rota para apresentação de slides
@main.route('/apresentacao')
def apresentacao():
    # Obtendo todas as fotos do banco de dados
    fotos = Foto.query.all()
    
    # Escolhendo um número fixo de fotos aleatórias
    numero_de_fotos = min(5, len(fotos)) 
    fotos_selecionadas = random.sample(fotos, numero_de_fotos) if fotos else []
    
    return render_template('apresentacao.html', fotos=fotos_selecionadas)