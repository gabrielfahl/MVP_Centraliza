from flasky import db, Tarefa, Subtarefa, app
from datetime import datetime  # Importando o datetime para converter as strings

with app.app_context():
    # Convertendo as strings para o tipo de data
    data_inicio = datetime.strptime("2025-01-10", "%Y-%m-%d").date()
    data_fim = datetime.strptime("2025-01-10", "%Y-%m-%d").date()

    # Criando uma nova tarefa
    nova_tarefa = Tarefa(
        nome="Estudar Flask com SQLAlchemy",
        descricao="Testar integração com calendário",
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    # Adicionando a tarefa ao banco de dados e confirmando a transação
    db.session.add(nova_tarefa)
    db.session.commit()
    print("Banco de dados populado com sucesso!")