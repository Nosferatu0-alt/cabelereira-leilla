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
- Desempenho semanal das últimas 4 semanas

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
\`\`\`bash
git clone https://github.com/seu-usuario/cabelereira-leila.git
cd cabelereira-leila
\`\`\`

**2. Crie e ative o ambiente virtual**
\`\`\`bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
\`\`\`

**3. Instale as dependências**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**4. Rode o sistema**
\`\`\`bash
python app.py
\`\`\`

As tabelas do banco de dados são criadas automaticamente na primeira execução, junto com o usuário administrador e os serviços padrão.

**5. Acesse no navegador**
\`\`\`
http://127.0.0.1:5000
\`\`\`

---

## Testes

**1. Instale as dependências de teste**
\`\`\`bash
pip install pytest pytest-flask
\`\`\`

**2. Rode todos os testes**
\`\`\`bash
pytest tests.py
\`\`\`

**3. Rode com detalhes (verbose)**
\`\`\`bash
pytest tests.py -v
\`\`\`

**4. Rode com cobertura de código**
\`\`\`bash
pip install pytest-cov
pytest tests.py --cov=app --cov-report=term-missing
\`\`\`

O banco usado nos testes é em memória (SQLite), separado do banco de desenvolvimento.

---

## Acesso Administrador (padrão)

| Campo | Valor |
|-------|-------|
| Email | cabelereiraLeila@adm.com |
| Senha | admin123 |

---

## Estrutura do Projeto

\`\`\`
cabelereira-leilla/
├── app.py
├── models.py
├── db.py
├── requirements.txt
├── tests.py
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── cliente/
    ├── gerencial/
    │   └── desempenho.html
    └── operacional/
\`\`\`

---

## Serviços cadastrados por padrão

| Serviço | Preço |
|---------|-------|
| Corte de Cabelo | R$ 50,00 |
| Manicure | R$ 30,00 |
| Pedicure | R$ 40,00 |
| Escova | R$ 60,00 |
| Design de Sobrancelhas | R$ 20,00 |
| Maquiagem | R$ 80,00 |
