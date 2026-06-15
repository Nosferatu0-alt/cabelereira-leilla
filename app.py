from collections import defaultdict
from flask import Flask, url_for, render_template, request, redirect, abort
from db import db
from models import Cliente, Agendamentos, Servico, Estado
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "m04H4H4"
lm = LoginManager(app)
lm.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabeleleila.db'
db.init_app(app)


@lm.user_loader
def load_user(id):
    return db.session.query(Cliente).filter_by(id=id).first()

@app.route('/')
def home():
    if not current_user.is_authenticated:
        return render_template('cliente/dashboard.html',
                               agendamentos_proximos=[],
                               agendamentos_cancelados=[],
                               semanas_com_multiplos={})

    if current_user.is_admin:
        agendamentos = Agendamentos.query.order_by(Agendamentos.data.asc()).all()
        return render_template('cliente/dashboard.html',
                               agendamentos_proximos=agendamentos,
                               agendamentos_cancelados=[],
                               semanas_com_multiplos={})

    agendamentos = (Agendamentos.query
                    .filter(Agendamentos.clienteId == current_user.id,
                            Agendamentos.estado != Estado.cancelado)
                    .order_by(Agendamentos.data.asc())
                    .all())

    agendamentos_cancelados = (Agendamentos.query
                               .filter(Agendamentos.clienteId == current_user.id,
                                       Agendamentos.estado == Estado.cancelado)
                               .order_by(Agendamentos.data.desc())
                               .all())

    agendamentosPendente = (Agendamentos.query
                            .filter(Agendamentos.clienteId == current_user.id,
                                    Agendamentos.estado == Estado.pendente)
                            .order_by(Agendamentos.data.asc())
                            .all())

    agendamentos_por_semana = defaultdict(list)
    for ag in agendamentosPendente:
        ano, semana, _ = ag.data.isocalendar()
        agendamentos_por_semana[(ano, semana)].append({
            'id': ag.id,
            'data': ag.data,
            'dia_semana': ag.data.strftime('%A'),
            'servicos': ag.servicos
        })

    semanas_com_multiplos = {
        semana: ags
        for semana, ags in agendamentos_por_semana.items()
        if len(ags) > 1
    }

    return render_template('cliente/dashboard.html',
                           agendamentos_proximos=agendamentos,
                           agendamentos_cancelados=agendamentos_cancelados,
                           semanas_com_multiplos=semanas_com_multiplos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        cliente = db.session.query(Cliente).filter_by(email=email).first()
        if not cliente or not check_password_hash(cliente.senha, senha):
            return "Email ou senha inválidos", 401
        login_user(cliente)
        return redirect(url_for('home'))
    return render_template('cliente/login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        novoCliente = Cliente(
            nome=request.form['nome'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            senha=generate_password_hash(request.form['senha'])
        )
        db.session.add(novoCliente)
        db.session.commit()
        login_user(novoCliente)
        return redirect(url_for('home'))
    return render_template('gerencial/cadastroCliente.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/agendamentos', methods=['GET', 'POST'])
@login_required
def agendamentos():
    if request.method == 'POST':
        dataHora = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')
        servicos_ids = request.form.getlist('servicos')

        if dataHora < datetime.now() or not servicos_ids:
            return "Não é possível marcar uma data passada ou sem serviço selecionado!", 400

        if current_user.is_admin:
            clienteInput = request.form.get('cliente')
            cliente = Cliente.query.get_or_404(clienteInput)
            novoAgendamento = Agendamentos(clienteId=cliente.id, data=dataHora, is_confirmed=True)
        else:
            novoAgendamento = Agendamentos(clienteId=current_user.id, data=dataHora)

        for servico_id in servicos_ids:
            servico = Servico.query.get(servico_id)
            if servico:
                novoAgendamento.servicos.append(servico)

        db.session.add(novoAgendamento)
        db.session.commit()
        return redirect(url_for('home'))

    todosClientes = Cliente.query.filter_by(is_admin=False).all()
    todosServicos = Servico.query.all()
    return render_template('cliente/novo_agendamento.html',
                           servicos=todosServicos,
                           clientes=todosClientes)


@app.route('/editarAgendamento/<int:id>', methods=['GET', 'POST'])
@login_required
def editarAgendamento(id):
    agendamento = Agendamentos.query.get_or_404(id)
    todosServicos = Servico.query.all()

    if not current_user.is_admin:
        distancia = (agendamento.data - datetime.now()).days
        if abs(distancia) < 2:
            return ("Infelizmente, edições só podem ser feitas até dois dias antes do agendamento. "
                    "Ligue para a Leila em 55555555 para alterações."), 403

    if request.method == 'POST':
        nova_data = datetime.strptime(request.form.get('dataHora'), '%Y-%m-%dT%H:%M')
        novoServicos_ids = request.form.getlist('servicos')

        if nova_data < datetime.now() or not novoServicos_ids:
            return "Não é possível marcar uma data passada ou sem serviço selecionado!", 400

        agendamento.data = nova_data
        agendamento.estado = Estado[request.form.get('estado')]

        idsAtuais = {s.id for s in agendamento.servicos}
        novos_ids = set(map(int, novoServicos_ids))

        for servico_id in idsAtuais - novos_ids:
            servico = Servico.query.get(servico_id)
            if servico:
                agendamento.servicos.remove(servico)

        for servico_id in novos_ids - idsAtuais:
            servico = Servico.query.get(servico_id)
            if servico:
                agendamento.servicos.append(servico)

        try:
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar: {e}", 500

    return render_template('cliente/alterar_agendamento.html',
                           agendamento=agendamento,
                           servicos=todosServicos,
                           estados=Estado,
                           todos_servicos=todosServicos)


@app.route('/cancelarAgendamento/<int:id>')
@login_required
def cancelarAgendamento(id):
    agendamento = Agendamentos.query.get_or_404(id)

    if not current_user.is_admin:
        distancia = (agendamento.data - datetime.now()).days
        if abs(distancia) < 2:
            return ("Infelizmente, cancelamentos só podem ser feitos até dois dias antes do agendamento. "
                    "Ligue para a Leila em 55555555 para alterações."), 403

    agendamento.estado = Estado.cancelado
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/confirmarAgendamento/<int:id>')
@login_required
def confirmarAgendamento(id):
    if not current_user.is_admin:
        abort(403)
    agendamento = Agendamentos.query.get_or_404(id)
    agendamento.is_confirmed = True
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/excluirAgendamento/<int:id>')
@login_required
def excluirAgendamento(id):
    if not current_user.is_admin:
        abort(403)
    agendamento = Agendamentos.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/unirAgendamentos/<int:id1>/<int:id2>', methods=['POST'])
@login_required
def unirAgendamentos(id1, id2):
    agendamento1 = Agendamentos.query.get_or_404(id1)
    agendamento2 = Agendamentos.query.get_or_404(id2)

    dias_semana = {
        "Monday": 2, "Tuesday": 3, "Wednesday": 4,
        "Thursday": 5, "Friday": 6, "Saturday": 7, "Sunday": 1
    }

    dia1 = request.form.get('dia1')
    dia2 = request.form.get('dia2')

    if dias_semana[dia1] < dias_semana[dia2]:
        mais_recente, mais_antigo = agendamento1, agendamento2
    else:
        mais_recente, mais_antigo = agendamento2, agendamento1

    agendamentoUnico = Agendamentos(clienteId=current_user.id, data=mais_recente.data)

    for servico in mais_recente.servicos + mais_antigo.servicos:
        if servico not in agendamentoUnico.servicos:
            agendamentoUnico.servicos.append(servico)

    mais_recente.estado = Estado.cancelado
    mais_antigo.estado = Estado.cancelado

    try:
        db.session.add(agendamentoUnico)
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        return f"Erro ao unir agendamentos: {e}", 500


@app.route('/historico')
@login_required
def historico():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = Agendamentos.query.filter_by(clienteId=current_user.id)

    if data_inicio:
        query = query.filter(Agendamentos.data >= datetime.strptime(data_inicio, '%Y-%m-%d'))
    if data_fim:
        query = query.filter(Agendamentos.data <= datetime.strptime(data_fim, '%Y-%m-%d').replace(hour=23, minute=59))

    agendamentos = query.order_by(Agendamentos.data.desc()).all()
    return render_template('cliente/historico.html', agendamentos=agendamentos)


@app.route('/desempenho')
@login_required
def desempenho():
    if not current_user.is_admin:
        abort(403)

    hoje = datetime.now()
    semanas = []
    for i in range(3, -1, -1):
        inicio = hoje - timedelta(weeks=i, days=hoje.weekday())
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = inicio + timedelta(days=6, hours=23, minutes=59)
        semanas.append((inicio, fim))

    dados_semanas = []
    for inicio, fim in semanas:
        ags = Agendamentos.query.filter(
            Agendamentos.data >= inicio,
            Agendamentos.data <= fim,
            Agendamentos.estado != Estado.cancelado
        ).all()

        total_servicos = sum(len(ag.servicos) for ag in ags)
        receita = sum(s.preco for ag in ags for s in ag.servicos)
        confirmados = sum(1 for ag in ags if ag.is_confirmed)

        dados_semanas.append({
            'periodo': f"{inicio.strftime('%d/%m')} – {fim.strftime('%d/%m')}",
            'agendamentos': len(ags),
            'servicos': total_servicos,
            'receita': receita,
            'confirmados': confirmados,
        })

    return render_template('gerencial/desempenho.html', semanas=dados_semanas)


@app.route('/listarAgendamentos')
@login_required
def listarAgendamentos():
    if not current_user.is_admin:
        abort(403)

    estado_filtro = request.args.get('estado')
    query = Agendamentos.query

    if estado_filtro:
        try:
            query = query.filter(Agendamentos.estado == Estado[estado_filtro])
        except KeyError:
            pass

    agendamentos = query.order_by(Agendamentos.data.asc()).all()
    return render_template('gerencial/listar_agendamentos.html',
                           agendamentos=agendamentos,
                           estados=Estado,
                           estado_filtro=estado_filtro)


@app.route('/servicos', methods=['GET', 'POST'])
@login_required
def servicos():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        novo_servico = Servico(
            nome=request.form['nome'],
            preco=request.form['preco'],
            descricao=request.form['descricao']
        )
        db.session.add(novo_servico)
        db.session.commit()
        return redirect(url_for('servicos'))

    todos_servicos = Servico.query.all()
    return render_template('gerencial/cadastroServico.html', servicos=todos_servicos)


@app.route('/cadastroCliente', methods=['GET', 'POST'])
@login_required
def cadastroCliente():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        novo_cliente = Cliente(
            nome=request.form['nome'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            senha=generate_password_hash(request.form['senha'])
        )
        db.session.add(novo_cliente)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('gerencial/cadastroCliente.html')


def inicializar_dados():
    db.create_all()

    admin_email = "cabelereiraLeila@adm.com"
    if not Cliente.query.filter_by(email=admin_email).first():
        db.session.add(Cliente(
            nome="Administrador",
            email=admin_email,
            telefone="000000000",
            senha=generate_password_hash("admin123"),
            is_admin=True
        ))

    servicos_padrao = [
        {"nome": "Corte de Cabelo", "preco": 50.0, "descricao": "Corte profissional de cabelo."},
        {"nome": "Manicure",        "preco": 30.0, "descricao": "Manicure completa."},
        {"nome": "Pedicure",        "preco": 40.0, "descricao": "Pedicure completa."},
        {"nome": "Escova",          "preco": 60.0, "descricao": "Escova modeladora."},
        {"nome": "Design de Sobrancelhas", "preco": 20.0, "descricao": "Design profissional de sobrancelhas."},
        {"nome": "Maquiagem",       "preco": 80.0, "descricao": "Maquiagem completa para eventos."},
    ]
    for dados in servicos_padrao:
        if not Servico.query.filter_by(nome=dados["nome"]).first():
            db.session.add(Servico(**dados))

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        inicializar_dados()
    app.run(debug=True)
