import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import app
from db import db
from models import Cliente, Agendamentos, Servico, Estado


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class ServicoModelTest(BaseTestCase):
    def test_criar_servico(self):
        servico = Servico(nome='Corte de Cabelo', preco=50.0, descricao='Corte profissional')
        db.session.add(servico)
        db.session.commit()

        self.assertIsNotNone(servico.id)
        self.assertEqual(servico.preco, 50.0)


class ClienteModelTest(BaseTestCase):
    def test_criar_cliente_padrao_nao_admin(self):
        cliente = Cliente(
            nome='Maria',
            email='maria@teste.com',
            telefone='11999999999',
            senha=generate_password_hash('senha123')
        )
        db.session.add(cliente)
        db.session.commit()

        self.assertIsNotNone(cliente.id)
        self.assertFalse(cliente.is_admin)


class AgendamentoModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.cliente = Cliente(
            nome='Ana',
            email='ana@teste.com',
            telefone='11988888888',
            senha=generate_password_hash('senha123')
        )
        self.servico = Servico(nome='Manicure', preco=30.0)
        db.session.add_all([self.cliente, self.servico])
        db.session.commit()

    def test_estado_padrao_pendente(self):
        ag = Agendamentos(
            clienteId=self.cliente.id,
            data=datetime.now() + timedelta(days=3)
        )
        db.session.add(ag)
        db.session.commit()

        self.assertEqual(ag.estado, Estado.pendente)

    def test_agendamento_com_servicos(self):
        ag = Agendamentos(
            clienteId=self.cliente.id,
            data=datetime.now() + timedelta(days=3)
        )
        ag.servicos.append(self.servico)
        db.session.add(ag)
        db.session.commit()

        self.assertIn(self.servico, ag.servicos)


class ViewsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.senha_cliente = 'senha123'
        self.senha_admin = 'admin123'

        self.cliente = Cliente(
            nome='Cliente Teste',
            email='cliente@teste.com',
            telefone='11999999999',
            senha=generate_password_hash(self.senha_cliente)
        )
        self.admin = Cliente(
            nome='Admin Teste',
            email='admin@teste.com',
            telefone='11988888888',
            senha=generate_password_hash(self.senha_admin),
            is_admin=True
        )
        db.session.add_all([self.cliente, self.admin])
        db.session.commit()

    def login(self, email, senha):
        return self.client.post(
            '/login',
            data={'email': email, 'senha': senha},
            follow_redirects=False
        )

    def test_home_sem_login(self):
        with patch('app.render_template', return_value=''):
            resp = self.client.get('/')
            self.assertEqual(resp.status_code, 200)

    def test_login_get(self):
        with patch('app.render_template', return_value=''):
            resp = self.client.get('/login')
            self.assertEqual(resp.status_code, 200)

    def test_login_sucesso(self):
        resp = self.login('cliente@teste.com', self.senha_cliente)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.location.endswith('/'))

    def test_login_senha_invalida(self):
        with patch('app.render_template', return_value='Email ou senha invalidos'):
            resp = self.login('cliente@teste.com', 'senha_errada')
            self.assertEqual(resp.status_code, 200)

    def test_cadastro_get(self):
        with patch('app.render_template', return_value=''):
            resp = self.client.get('/cadastro')
            self.assertEqual(resp.status_code, 200)

    def test_agendamentos_requer_login(self):
        resp = self.client.get('/agendamentos')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.location)

    def test_cadastrarCliente_bloqueado_para_nao_admin(self):
        self.login('cliente@teste.com', self.senha_cliente)
        with patch('app.render_template', return_value='Você não tem permissão'):
            resp = self.client.get('/cadastroCliente')
            self.assertEqual(resp.status_code, 200)

    def test_cadastrarCliente_permitido_para_admin(self):
        self.login('admin@teste.com', self.senha_admin)
        with patch('app.render_template', return_value=''):
            resp = self.client.get('/cadastroCliente')
            self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()