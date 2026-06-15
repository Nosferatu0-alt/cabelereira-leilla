# Cabeleira Leila - Sistema de Agendamento

Sistema web para gerenciamento de agendamentos de um salão de beleza, desenvolvido com Flask.

---

## Funcionalidades

### Cliente
- Cadastro e login de clientes
- Agendamento de serviços
- Edição e cancelamento de agendamentos (até 2 dias antes)
- Sugestão de unificação de agendamentos na mesma semana

### Operacional (Administrador)
- Listagem de todos os agendamentos
- Alteração de agendamentos de qualquer cliente
- Confirmação de agendamentos
- Gerenciamento de status (pendente, finalizado, cancelado)
- Cancelamento e exclusão de agendamentos

### Gerencial (Administrador)
- Dashboard com visão geral dos agendamentos
- Acompanhamento por cliente

---

## Tecnologias

- Python 3.13
- Flask 3.1.0
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.1.0
- SQLite
- Werkzeug 3.1.3

---

## Como rodar o projeto

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/cabelereira-leila.git
cd cabelereira-leila
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Rode o sistema**
```bash
python app.py
```

**5. Acesse no navegador**
```
http://127.0.0.1:5000
```

---

## Acesso Administrador (padrão)

| Campo | Valor |
|-------|-------|
| Email | cabelereiraLeila@adm.com |
| Senha | admin123 |

---

## Estrutura do Projeto

```
cabelereira-leila/
├── app.py                  # Rotas e lógica principal
├── models.py               # Modelos do banco de dados
├── db.py                   # Configuração do SQLAlchemy
├── requirements.txt        # Dependências
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── cliente/
    │   ├── login.html
    │   ├── dashboard.html
    │   ├── novo_agendamento.html
    │   ├── alterar_agendamento.html
    │   ├── detalhe_agendamento.html
    │   └── historico.html
    ├── gerencial/
    │   ├── painel.html
    │   ├── cadastroCliente.html
    │   └── cadastroServico.html
    └── operacional/
        ├── painel.html
        ├── listar_agendamentos.html
        ├── detalhe_agendamento.html
        └── alterar_agendamento.html
```

---

## Serviços cadastrados por padrão

- Corte de Cabelo — R$ 50,00
- Manicure — R$ 30,00
- Pedicure — R$ 40,00
- Escova — R$ 60,00
- Design de Sobrancelhas — R$ 20,00
- Maquiagem — R$ 80,00