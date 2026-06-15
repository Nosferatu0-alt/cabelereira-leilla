import pytest
from app import app as flask_app
from db import db as _db
from models import Cliente, Servico, Agendamentos, Estado
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    with flask_app.app_context():
        _db.create_all()
        _seed()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# ── helpers ───────────────────────────────────────────────────────────────────

def login(client, email, senha):
    return client.post('/login', data={'email': email, 'senha': senha},
                       follow_redirects=True)

def login_admin(client):
    return login(client, 'leila@adm.com', 'admin123')

def login_cliente(client):
    return login(client, 'cliente@teste.com', 'senha123')

def criar_agendamento(app, dias=3):
    with app.app_context():
        servico = Servico.query.first()
        cliente = Cliente.query.filter_by(is_admin=False).first()
        ag = Agendamentos(clienteId=cliente.id,
                          data=datetime.now() + timedelta(days=dias))
        ag.servicos.append(servico)
        _db.session.add(ag)
        _db.session.commit()
        return ag.id

def _amanha():
    return (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')

def _seed():
    _db.session.add_all([
        Cliente(nome='Leila', email='leila@adm.com', telefone='11999999999',
                senha=generate_password_hash('admin123'), is_admin=True),
        Cliente(nome='Maria', email='cliente@teste.com', telefone='11888888888',
                senha=generate_password_hash('senha123'), is_admin=False),
        Servico(nome='Corte', preco=50.0, descricao='Corte simples'),
    ])
    _db.session.commit()


# ── auth ──────────────────────────────────────────────────────────────────────

def test_login_valido(client):
    assert login(client, 'cliente@teste.com', 'senha123').status_code == 200

def test_login_senha_errada(client):
    assert login(client, 'cliente@teste.com', 'errada').status_code == 401

def test_login_email_inexistente(client):
    assert login(client, 'naoexiste@x.com', 'qualquer').status_code == 401

def test_logout(client):
    login_cliente(client)
    assert client.get('/logout', follow_redirects=True).status_code == 200

def test_cadastro_novo_cliente(client):
    r = client.post('/cadastro', data={
        'nome': 'João', 'email': 'joao@teste.com',
        'telefone': '11777777777', 'senha': 'senha456'
    }, follow_redirects=True)
    assert r.status_code == 200

def test_area_protegida_sem_login(client):
    r = client.get('/agendamentos', follow_redirects=True)
    assert b'login' in r.data.lower() or r.status_code == 200


# ── agendamentos ──────────────────────────────────────────────────────────────

def test_criar_agendamento(client, app):
    login_cliente(client)
    with app.app_context():
        servico_id = Servico.query.first().id
    r = client.post('/agendamentos', data={
        'dataHora': _amanha(), 'servicos': [str(servico_id)]
    }, follow_redirects=True)
    assert r.status_code == 200

def test_agendamento_data_passada(client, app):
    login_cliente(client)
    with app.app_context():
        servico_id = Servico.query.first().id
    r = client.post('/agendamentos', data={
        'dataHora': '2020-01-01T10:00', 'servicos': [str(servico_id)]
    })
    assert r.status_code == 400

def test_agendamento_sem_servico(client):
    login_cliente(client)
    r = client.post('/agendamentos', data={'dataHora': _amanha(), 'servicos': []})
    assert r.status_code == 400

def test_cancelar_agendamento_admin(client, app):
    login_admin(client)
    ag_id = criar_agendamento(app)
    client.get(f'/cancelarAgendamento/{ag_id}', follow_redirects=True)
    with app.app_context():
        assert Agendamentos.query.get(ag_id).estado == Estado.cancelado

def test_cliente_nao_cancela_com_menos_de_2_dias(client, app):
    login_cliente(client)
    ag_id = criar_agendamento(app, dias=0)
    assert client.get(f'/cancelarAgendamento/{ag_id}').status_code == 403


# teste admin

def test_confirmar_agendamento_admin(client, app):
    login_admin(client)
    ag_id = criar_agendamento(app)
    client.get(f'/confirmarAgendamento/{ag_id}', follow_redirects=True)
    with app.app_context():
        assert Agendamentos.query.get(ag_id).is_confirmed is True

def test_confirmar_agendamento_cliente_bloqueado(client, app):
    login_cliente(client)
    ag_id = criar_agendamento(app)
    assert client.get(f'/confirmarAgendamento/{ag_id}').status_code == 403

def test_excluir_agendamento_admin(client, app):
    login_admin(client)
    ag_id = criar_agendamento(app)
    client.get(f'/excluirAgendamento/{ag_id}', follow_redirects=True)
    with app.app_context():
        assert Agendamentos.query.get(ag_id) is None

def test_excluir_agendamento_cliente_bloqueado(client, app):
    login_cliente(client)
    ag_id = criar_agendamento(app)
    assert client.get(f'/excluirAgendamento/{ag_id}').status_code == 403

def test_desempenho_cliente_bloqueado(client):
    login_cliente(client)
    assert client.get('/desempenho').status_code == 403

def test_listar_agendamentos_cliente_bloqueado(client):
    login_cliente(client)
    assert client.get('/listarAgendamentos').status_code == 403
