# Cabeleireira Leila - Sistema de Agendamento

Sistema web para gerenciamento de agendamentos de um salão de beleza, desenvolvido com Flask.

---

## Funcionalidades

### Cliente
- Cadastro e login de clientes;
- Agendamento de serviços;
- Edição e cancelamento de agendamentos (até 2 dias antes da data marcada);
- Sugestão de unificação de agendamentos na mesma semana.

### Operacional (Administrador)
- Listagem de todos os agendamentos;
- Alteração de agendamentos de qualquer cliente;
- Confirmação de agendamentos;
- Gerenciamento de status (`Pendente`, `Finalizado` e `Cancelado`);
- Cancelamento e exclusão de agendamentos.

### Gerencial (Administrador)
- Dashboard com visão geral dos agendamentos;
- Acompanhamento por cliente;
- Desempenho semanal das últimas quatro semanas.

---

## Tecnologias Utilizadas

- Python 3.13
- Flask 3.1.0
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.1.0
- SQLite
- Werkzeug 3.1.3

---

## Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/cabelereira-leila.git
cd cabelereira-leila
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python app.py
```

As tabelas do banco de dados são criadas automaticamente na primeira execução, juntamente com o usuário administrador e os serviços padrão.

### 5. Acesse o sistema

```text
http://127.0.0.1:5000
```

---

## Testes

### Instalar as dependências de teste

```bash
pip install pytest pytest-flask pytest-cov
```

### Executar todos os testes

```bash
pytest tests.py
```

### Executar os testes em modo detalhado

```bash
pytest tests.py -v
```

### Gerar relatório de cobertura

```bash
pytest tests.py --cov=app --cov-report=term-missing
```

Os testes utilizam um banco de dados SQLite em memória, separado do ambiente de desenvolvimento.

---

## Acesso do Administrador

| Campo | Valor |
|--------|--------|
| E-mail | cabelereiraLeila@adm.com |
| Senha | admin123 |

---

## Estrutura do Projeto

```text
cabelereira-leila/
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
```

---

## Serviços Cadastrados por Padrão

| Serviço | Preço |
|----------|--------|
| Corte de Cabelo | R$ 50,00 |
| Manicure | R$ 30,00 |
| Pedicure | R$ 40,00 |
| Escova | R$ 60,00 |
| Design de Sobrancelhas | R$ 20,00 |
| Maquiagem | R$ 80,00 |

---
