import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


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
    descricao = db.Column(db.String(500))
    subtarefas = db.relationship('Subtarefa', backref='tarefa')

class Subtarefa(db.Model):
    __tablename__ = 'subtarefas'
    sub_id = db.Column(db.Integer, primary_key=True)
    sub_nome = db.Column(db.String(64), unique=True)
    tarefa_id = db.Column(db.Integer, db.ForeignKey('tarefas.id'))


# Aqui começa a definição de rotas
@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/visualizar_tarefa', methods=['GET'])
def visualizar_tarefa():
    tarefas = Tarefa.query.all()
    return render_template('visualizar_tarefa.html', tarefas=tarefas)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
def adicionar_tarefa():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        # Verifica se os campos estão preenchidos
        if nome and descricao:
            try:
                # Tenta criar uma nova tarefa
                nova_tarefa = Tarefa(nome=nome, descricao=descricao)
                db.session.add(nova_tarefa)
                db.session.commit()
                flash('Tarefa adicionada com sucesso!', 'success')
            except IntegrityError:
                # Captura o erro de integridade (nome duplicado)
                db.session.rollback()  # Reverte qualquer alteração no banco
                flash('Erro: Nome da tarefa já existe!', 'error')
            return redirect(url_for('visualizar_tarefa'))
        else:
            flash('Por favor, preencha todos os campos.', 'error')
    return render_template('adicionar_tarefa.html')


@app.route("/pomodoro")
def home():
    return render_template("pomodoro.html")

# Inicialização do Banco de Dados e Execução do Servidor
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)