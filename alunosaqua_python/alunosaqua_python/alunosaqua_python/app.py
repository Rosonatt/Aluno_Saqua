from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import calendar
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar'

# --- CONFIGURAÇÕES GLOBAIS DE REGRAS ---
MAX_FALTAS_PERMITIDAS = 4
TOTAL_AULAS_PADRAO = 100
NOTA_MINIMA_APROVACAO_MATERIA = 14
MATERIAS_ENSINO_FUNDAMENTAL = [
    'Português', 'Matemática', 'História', 'Geografia',
    'Ciências', 'Artes', 'Educação Física', 'Inglês'
]
# --- FIM DAS CONFIGURAÇÕES ---

# --- BANCO DE DADOS SIMULADO ---
USERS = {
    'alunos': {
        '202411251': {'password': generate_password_hash('aluno'), 'nome': 'Rosonatt Ferreira Ramos', 'turma': '9A', 'notas': {'Matemática': [8, 7], 'Português': [9, 8], 'História': [7, 7], 'Ciências': [10, 9]}, 'faltas': ['2025-09-10', '2025-09-22'], 'provas': {'Matemática': ['2025-09-29']}},
        '67890': {'password': generate_password_hash('aluno'), 'nome': 'Ryan Guiwison', 'turma': '8B', 'notas': {'Matemática': [5, 4], 'Português': [6, 7.5], 'Artes': [5, 5]}, 'faltas': ['2025-09-01','2025-09-02','2025-09-03','2025-09-08','2025-09-09','2025-09-10','2025-09-15','2025-09-16','2025-09-17'], 'provas': {}},
        '11223': {'password': generate_password_hash('aluno'), 'nome': 'Bruno Alves', 'turma': '7C', 'notas': {'Artes': [5, 4], 'Português': [7, 6.5]}, 'faltas': ['2025-09-11'], 'provas': {}},
        '22334': {'password': generate_password_hash('aluno'), 'nome': 'Natalia Crys Cardoso', 'turma': '9A', 'notas': {'Inglês': [8.5, 9], 'Física': [6.5, 7.5]}, 'faltas': [], 'provas': {}},
        '33445': {'password': generate_password_hash('aluno'), 'nome': 'Kevin Paula', 'turma': '6D', 'notas': {'Química': [7, 7], 'Literatura': [8, 6]}, 'faltas': ['2025-09-05','2025-09-12','2025-09-19'], 'provas': {}},
        '44556': {'password': generate_password_hash('aluno'), 'nome': 'Raissa Leite', 'turma': '5E', 'notas': {'Sociologia': [9, 8.5], 'Filosofia': [7, 7]}, 'faltas': ['2025-09-23'], 'provas': {}},
        '55667': {'password': generate_password_hash('aluno'), 'nome': 'João Candia', 'turma': '4F', 'notas': {'Educação Física': [9.5, 9], 'Biologia': [6, 6.5]}, 'faltas': [], 'provas': {'Biologia': ['2025-09-26']}},
        '66778': {'password': generate_password_hash('aluno'), 'nome': 'Ronald Carvalho', 'turma': '3G', 'notas': {'Matemática': [7, 7], 'Português': [7.5, 7.5]}, 'faltas': ['2025-09-04','2025-09-18'], 'provas': {}}
    },
    'pais': {
        'pai_rosonatt': {'password': generate_password_hash('pai'), 'filho_matricula': '202411251'},
        'pai_ryan': {'password': generate_password_hash('pai2'), 'filho_matricula': '67890'},
        'pai_bruno': {'password': generate_password_hash('mae'), 'filho_matricula': '11223'},
        'mae_natalia': {'password': generate_password_hash('pais'), 'filho_matricula': '22334'},
        'pai_kevin': {'password': generate_password_hash('pais2'), 'filho_matricula': '33445'},
        'mae_raissa': {'password': generate_password_hash('pais3'), 'filho_matricula': '44556'},
        'pai_joao': {'password': generate_password_hash('pais4'), 'filho_matricula': '55667'},
        'mae_ronald': {'password': generate_password_hash('pais5'), 'filho_matricula': '66778'},
    },
    'professores': {
        'prof_carlos': {'password': generate_password_hash('prof123'), 'nome': 'Carlos Mendes', 'disciplinas': ['Matemática', 'Ciências']},
        'prof_ana': {'password': generate_password_hash('prof456'), 'nome': 'Ana Souza', 'disciplinas': ['Português', 'História']},
        'prof_beatriz': {'password': generate_password_hash('prof789'), 'nome': 'Beatriz Lima', 'disciplinas': ['Artes', 'Educação Física']},
        'prof_roberto': {'password': generate_password_hash('prof101'), 'nome': 'Roberto Costa', 'disciplinas': ['Geografia', 'Inglês']}
    },
    'psicopedagogos': {
        'psi_joana': {'password': generate_password_hash('psi'), 'nome': 'Joana'},
        'psi_pedro': {'password': generate_password_hash('psi2'), 'nome': 'Pedro'},
        'coord_educ': {'password': generate_password_hash('coord'), 'nome': 'Coordenadora Maria'},
        'sup_psi': {'password': generate_password_hash('sup'), 'nome': 'Supervisor Antonio'},
    }
}
DENUNCIAS = {}

# --- FUNÇÃO AUXILIAR DE CÁLCULOS ---
def calcular_dados_aluno(aluno_data):
    num_faltas = len(aluno_data.get('faltas', []))
    porcentagem_faltas = (num_faltas / TOTAL_AULAS_PADRAO) * 100 if TOTAL_AULAS_PADRAO > 0 else 0
    status_faltas = 'REPROVADO POR FALTAS' if num_faltas > MAX_FALTAS_PERMITIDAS else 'APROVADO POR FALTAS'
    
    medias_materias = {}
    materias_reprovadas = []
    
    for disciplina, notas_list in aluno_data.get('notas', {}).items():
        if isinstance(notas_list, list) and len(notas_list) == 2:
            soma_notas = sum(notas_list)
            status_materia = 'APROVADO' if soma_notas >= NOTA_MINIMA_APROVACAO_MATERIA else 'REPROVADO'
            if status_materia == 'REPROVADO': materias_reprovadas.append(disciplina)
            medias_materias[disciplina] = {'nota1': notas_list[0], 'nota2': notas_list[1], 'soma': round(soma_notas, 1), 'status': status_materia}
        else:
            nota1 = notas_list[0] if isinstance(notas_list, list) and len(notas_list) > 0 else 'N/A'
            medias_materias[disciplina] = {'nota1': nota1, 'nota2': 'N/A', 'soma': 'N/A', 'status': 'PENDENTE'}

    status_geral_notas = 'REPROVADO POR NOTA' if materias_reprovadas else 'APROVADO POR NOTA'
    status_final = 'APROVADO'
    if 'REPROVADO' in status_faltas or 'REPROVADO' in status_geral_notas: status_final = 'REPROVADO'

    return {
        'num_faltas': num_faltas, 'porcentagem_faltas': round(porcentagem_faltas, 2),
        'status_faltas': status_faltas, 'medias_materias': medias_materias,
        'materias_reprovadas': materias_reprovadas, 'status_geral_notas': status_geral_notas,
        'status_final_aluno': status_final
    }

# --- FUNÇÃO AUXILIAR PARA CRIAR O MENU RECURSIVO (DADOS) ---
def get_aluno_menu():
    # Estrutura de dados hierárquica que será renderizada no HTML usando a Macro Recursiva
    return [
        {'name': 'Dashboard', 'url': url_for('aluno_dashboard'), 'icon': '🏠', 'children': []},
        {
            'name': 'Acadêmico',
            'url': '#', # Item pai não clicável
            'icon': '📚',
            'children': [
                {'name': 'Minhas Notas', 'url': url_for('aluno_notas'), 'icon': '📊', 'children': []},
                {'name': 'Minha Presença', 'url': url_for('aluno_presenca'), 'icon': '📅', 'children': []},
            ]
        },
        {'name': 'Fazer Denúncia', 'url': url_for('aluno_denunciar'), 'icon': '🚨', 'children': []},
        {'name': 'Sair', 'url': url_for('logout'), 'icon': '🚪', 'children': []}
    ]

# --- ROTAS PRINCIPAIS ---
@app.route('/')
def index():
    # TEMPORARIAMENTE passando o menu para testar a recursividade no index.html
    return render_template('index.html', menu=get_aluno_menu())

@app.route('/informacoes-cadastro')
def informacoes_cadastro():
    # Assumindo que você tem um informacoes_cadastro.html
    return render_template('informacoes_cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type, username, password = request.form['user_type'], request.form['username'], request.form['password']
        user_map = {'aluno': ('alunos', 'aluno_dashboard'), 'pais': ('pais', 'pais_dashboard'), 'professor': ('professores', 'professor_dashboard'), 'psicopedagogo': ('psicopedagogos', 'psicopedagogo_dashboard')}
        if user_type in user_map:
            cat, endp = user_map[user_type]
            user = USERS[cat].get(username)
            if user and check_password_hash(user.get('password'), password):
                session['user_type'], session['username'] = user_type, username
                # Redireciona para a tela de loading, que por sua vez redirecionará para o dashboard
                redirect_url = url_for(endp)
                return render_template('loading.html', redirect_url=redirect_url)
        flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ROTAS DO ALUNO ---
# ********** ROTAS ATUALIZADAS PARA PASSAR O MENU **********
@app.route('/aluno/dashboard')
def aluno_dashboard():
    if session.get('user_type') != 'aluno': return redirect(url_for('login'))
    # Passando a estrutura de menu hierárquica
    return render_template('aluno_dashboard.html', aluno=USERS['alunos'][session['username']], menu=get_aluno_menu())

@app.route('/aluno/notas')
def aluno_notas():
    if session.get('user_type') != 'aluno': return redirect(url_for('login'))
    aluno_data = USERS['alunos'][session['username']]
    return render_template('aluno_notas.html', aluno=aluno_data, dados_calculados=calcular_dados_aluno(aluno_data), config=app.config, menu=get_aluno_menu())

@app.route('/aluno/presenca')
def aluno_presenca():
    if session.get('user_type') != 'aluno': return redirect(url_for('login'))
    aluno_data = USERS['alunos'][session['username']]
    dados = calcular_dados_aluno(aluno_data)
    try: year, month, hoje = datetime.now().year, datetime.now().month, datetime.now().date()
    except: year, month, hoje = 2025, 9, datetime(2025, 9, 30).date()
    cal = calendar.Calendar()
    semanas_do_mes = cal.monthdatescalendar(year, month)
    chart = {'presente': 100 - dados['porcentagem_faltas'], 'ausente': dados['porcentagem_faltas']}
    return render_template('aluno_presenca.html', aluno=aluno_data, dados_calculados=dados, semanas=semanas_do_mes, mes_atual=month, ano_atual=year, hoje=hoje, chart_data=chart, config=app.config, menu=get_aluno_menu())

@app.route('/aluno/denunciar', methods=['GET', 'POST'])
def aluno_denunciar():
    if session.get('user_type') != 'aluno':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        den_id = str(uuid.uuid4())
        
        denuncia_data = {
            'serial': den_id.split('-')[0].upper(),
            'aluno_matricula': session['username'],
            'status': 'aberta',
            'urgencia': 'não classificada',
            'descricao': request.form.get('descricao', 'Não preenchido'),
            'agressor_tipo': request.form.getlist('agressor_tipo[]'),
            'natureza': request.form.getlist('natureza[]'),
            'frequencia': request.form.getlist('frequencia[]'),
            'local': request.form.getlist('local[]'),
            'reportado': request.form.getlist('reportado[]'),
            'vitima_conhecimento': request.form.getlist('vitima_conhecimento[]'),
            'evidencia': request.form.getlist('evidencia[]'),
            'gravidade': request.form.getlist('gravidade[]'),
            'expectativa': request.form.get('expectativa', 'Não preenchido')
        }
        
        DENUNCIAS[den_id] = denuncia_data

        flash('Denúncia enviada com sucesso!', 'success')
        return redirect(url_for('aluno_dashboard'))
        
    return render_template('aluno_denunciar.html', menu=get_aluno_menu()) # Passando o menu aqui também

# --- ROTAS DOS PAIS (Mantidas as originais, mas devem usar o base.html também) ---
@app.route('/pais/dashboard')
def pais_dashboard():
    if session.get('user_type') != 'pais': return redirect(url_for('login'))
    filho = USERS['alunos'].get(USERS['pais'][session['username']]['filho_matricula'])
    if not filho: return redirect(url_for('logout'))
    # Supondo que você criaria um menu específico para pais ou usaria um template base
    return render_template('pais_dashboard.html', filho=filho, dados_calculados=calcular_dados_aluno(filho), config=app.config)

# ... (outras rotas)

if __name__ == '__main__':
    app.config.update(NOTA_MINIMA_APROVACAO_MATERIA=NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)
    app.run(debug=True)
