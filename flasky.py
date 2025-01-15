import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



# Configuração do Flask e do SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'centralizakey'


# Definição dos modelos (Tarefa e Subtarefa)
class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(500))
    subtarefas = db.relationship('Subtarefa', backref='tarefa')

class Subtarefa(db.Model):
    __tablename__ = 'subtarefas'
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_nome = db.Column(db.String(64), unique=True)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefas.id'))

#Criação de usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)


# Aqui começa a definição de rotas
@app.route('/')
def index():
    usuario = session.get('usuario')
    return render_template('index.html', usuario=usuario)


@app.route('/visualizar_tarefa', methods=['GET'])
def visualizar_tarefa():
    tarefas = Tarefa.query.all()
    return render_template('visualizar_tarefa.html', tarefas=tarefas)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        
        # Verifica se todos os campos estão preenchidos
        if nome and descricao and data_inicio and data_fim:
            try:
                # Converte as strings de data para objetos datetime
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                
                if data_fim < data_inicio:
                    flash('Erro: A data de término não pode ser anterior à data de início!', 'error')
                else:
                # Cria a nova tarefa
                    nova_tarefa = Tarefa(
                        nome=nome,
                        descricao=descricao,
                        data_inicio=data_inicio,
                        data_fim=data_fim
                    )
                    db.session.add(nova_tarefa)
                    db.session.commit()
                    flash('Tarefa adicionada com sucesso!', 'success')
                    return redirect(url_for('visualizar_tarefa'))
            except Exception as e:
                    db.session.rollback()  # Caso haja algum erro
                    flash(f'Erro ao adicionar tarefa: {str(e)}', 'error')
        else:
            flash('Por favor, preencha todos os campos.', 'error')

    return render_template('adicionar_tarefa.html')

@app.route("/pomodoro")
def home():
    return render_template("pomodoro.html")

@app.route('/calendario')
def calendario():
    return render_template('calendario.html')

@app.route('/tarefas')
def get_tarefas():
    tarefas = Tarefa.query.all()  # Busca todas as tarefas
    resultado = [
        {
            "id": tarefa.id,
            "title": tarefa.nome,
            "start": tarefa.data_inicio.isoformat(),  # Formato ISO para o FullCalendar
            "end": tarefa.data_fim.isoformat(),
            "description": tarefa.descricao
        }
        for tarefa in tarefas
    ]
    return jsonify(resultado)

#Rota para criação de conta, login e logout
@app.route('/criar_conta', methods=['GET', 'POST'])
def criar_conta():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        if nome and senha:
            senha_hash = generate_password_hash(senha)
            novo_usuario = Usuario(nome=nome, senha=senha_hash)
            try:
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Conta criada com sucesso!', 'success')
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash('Erro: Nome de usuário já está em uso.', 'error')
        else:
            flash('Por favor, preencha todos os campos.', 'error')
    return render_template('criar_conta.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario'] = usuario.nome
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('index'))

# Inicialização do Banco de Dados e Execução do Servidor
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)