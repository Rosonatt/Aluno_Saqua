from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import calendar
from datetime import datetime, timedelta # Importa o timedelta

app = Flask(__name__)
app.secret_key = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar'

# --- CONFIGURAÇÕES GLOBAIS DE REGRAS ---
MAX_FALTAS_PERMITIDAS = 4
TOTAL_AULAS_PADRAO = 100
NOTA_MINIMA_APROVACAO_MATERIA = 7
MATERIAS_ENSINO_FUNDAMENTAL = [
    'Português', 'Matemática', 'História', 'Geografia',
    'Ciências', 'Artes', 'Educação Física', 'Inglês'
]
# --- FIM DAS CONFIGURAÇÕES ---

# --- BANCO DE DADOS SIMULADO ---
USERS = {
    'alunos': {
        '202411251': {'password': generate_password_hash('aluno'), 'nome': 'Rosonatt Ferreira Ramos', 'turma': '9A', 'notas': {'Matemática': [8, 7], 'Português': [9, 8], 'História': [7, 7], 'Ciências': [10, 9]}, 'faltas': ['2025-09-10', '2025-09-22'], 'provas': {'Matemática': ['2025-09-29']}},
        '202411281': {'password': generate_password_hash('aluno'), 'nome': 'Ryan Guiwison', 'turma': '8B', 'notas': {'Matemática': [5, 4], 'Português': [6, 7.5], 'Artes': [5, 5]}, 'faltas': ['2025-09-01','2025-09-02','2025-09-03','2025-09-08','2025-09-09','2025-09-10','2025-09-15','2025-09-16','2025-09-17'], 'provas': {}},
        '11223': {'password': generate_password_hash('aluno'), 'nome': 'Bruno Alves', 'turma': '7C', 'notas': {'Artes': [5, 4], 'Português': [7, 6.5]}, 'faltas': ['2025-09-11'], 'provas': {}},
        '22334': {'password': generate_password_hash('aluno'), 'nome': 'Natalia Crys Cardoso', 'turma': '9A', 'notas': {'Inglês': [8.5, 9], 'Física': [6.5, 7.5]}, 'faltas': [], 'provas': {}},
        '33445': {'password': generate_password_hash('aluno'), 'nome': 'Kevin Paula', 'turma': '6D', 'notas': {'Química': [7, 7], 'Literatura': [8, 6]}, 'faltas': ['2025-09-05','2025-09-12','2025-09-19'], 'provas': {}},
        '44556': {'password': generate_password_hash('aluno'), 'nome': 'Raissa Leite', 'turma': '5E', 'notas': {'Sociologia': [9, 8.5], 'Filosofia': [7, 7]}, 'faltas': ['2025-09-23'], 'provas': {}},
        '55667': {'password': generate_password_hash('aluno'), 'nome': 'João Candia', 'turma': '4F', 'notas': {'Educação Física': [9.5, 9], 'Biologia': [6, 6.5]}, 'faltas': [], 'provas': {'Biologia': ['2025-09-26']}},
        '66778': {'password': generate_password_hash('aluno'), 'nome': 'Ronald Carvalho', 'turma': '3G', 'notas': {'Matemática': [7, 7], 'Português': [7.5, 7.5]}, 'faltas': ['2025-09-04','2025-09-18'], 'provas': {}}
    },
    'pais': {
        'pai_rosonatt': {'password': generate_password_hash('pai'), 'filho_matricula': '202411251'},
        'pai_ryan': {'password': generate_password_hash('pai2'), 'filho_matricula': '202411281'},
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
    status_faltas = 'REPROVADO POR FALTAS' if num_faltas > MAX_FALTAS_PERMITIDAS else 'APROVADO'
    
    medias_materias = {}
    materias_reprovadas = []
    
    for disciplina, notas_list in aluno_data.get('notas', {}).items():
        if isinstance(notas_list, list) and len(notas_list) == 2:
            media_notas = sum(notas_list)/2
            status_materia = 'APROVADO' if media_notas >= NOTA_MINIMA_APROVACAO_MATERIA else 'REPROVADO'
            if status_materia == 'REPROVADO': materias_reprovadas.append(disciplina)
            medias_materias[disciplina] = {'nota1': notas_list[0], 'nota2': notas_list[1], 'media': round(media_notas, 1), 'status': status_materia}
        else:
            nota1 = notas_list[0] if isinstance(notas_list, list) and len(notas_list) > 0 else 'N/A'
            medias_materias[disciplina] = {'nota1': nota1, 'nota2': 'N/A', 'media': 'N/A', 'status': 'PENDENTE'}

    status_geral_notas = 'REPROVADO POR NOTA' if materias_reprovadas else 'APROVADO POR NOTA'
    status_final = 'APROVADO'
    if 'REPROVADO' in status_faltas or 'REPROVADO' in status_geral_notas: status_final = 'REPROVADO'

    return {
        'num_faltas': num_faltas, 'porcentagem_faltas': round(porcentagem_faltas, 2),
        'status_faltas': status_faltas, 'medias_materias': medias_materias,
        'materias_reprovadas': materias_reprovadas, 'status_geral_notas': status_geral_notas,
        'status_final_aluno': status_final
    }

# --- ROTAS PRINCIPAIS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/informacoes-cadastro')
def informacoes_cadastro():
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
                redirect_url = url_for(endp)
                return render_template('loading.html', redirect_url=redirect_url)
        flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ROTAS DO ALUNO ---
@app.route('/aluno/dashboard')
def aluno_dashboard():
    if session.get('user_type') != 'aluno': return redirect(url_for('login'))
    return render_template('aluno_dashboard.html', aluno=USERS['alunos'][session['username']])

@app.route('/aluno/notas')
def aluno_notas():
    if session.get('user_type') != 'aluno': return redirect(url_for('login'))
    aluno_data = USERS['alunos'][session['username']]
    return render_template('aluno_notas.html', aluno=aluno_data, dados_calculados=calcular_dados_aluno(aluno_data), config=app.config)

# ====================================================================
# INÍCIO DA ALTERAÇÃO
# ====================================================================
@app.route('/aluno/presenca')
def aluno_presenca():
    if session.get('user_type') != 'aluno':
        return redirect(url_for('login'))

    # 1. Obter o mês e o ano da URL, ou usar a data atual como padrão.
    try:
        ano_atual = int(request.args.get('ano', datetime.now().year))
        mes_atual = int(request.args.get('mes', datetime.now().month))
        if not 1 <= mes_atual <= 12: # Garante que o mês seja válido
            raise ValueError("Mês inválido")
    except (ValueError, TypeError):
        # Se os parâmetros forem inválidos, retorna para a data atual
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month

    # 2. Calcular mês anterior e próximo para os botões de navegação
    primeiro_dia_do_mes = datetime(ano_atual, mes_atual, 1)
    
    # Mês anterior: pega o primeiro dia do mês atual e subtrai 1 dia
    mes_anterior_data = primeiro_dia_do_mes - timedelta(days=1)
    ano_anterior = mes_anterior_data.year
    mes_anterior = mes_anterior_data.month
    
    # Próximo mês: pega o último dia do mês atual e adiciona 1 dia
    _, ultimo_dia_num = calendar.monthrange(ano_atual, mes_atual)
    ultimo_dia_do_mes = datetime(ano_atual, mes_atual, ultimo_dia_num)
    mes_seguinte_data = ultimo_dia_do_mes + timedelta(days=1)
    ano_seguinte = mes_seguinte_data.year
    mes_seguinte = mes_seguinte_data.month

    # Lógica original da função
    aluno_data = USERS['alunos'][session['username']]
    dados = calcular_dados_aluno(aluno_data)
    
    cal = calendar.Calendar()
    # Gera o calendário para o mês e ano CORRETOS (vindos da URL ou atuais)
    semanas_do_mes = cal.monthdatescalendar(ano_atual, mes_atual)
    
    chart = {'presente': 100 - dados['porcentagem_faltas'], 'ausente': dados['porcentagem_faltas']}
    hoje = datetime.now().date()

    # 3. Passar todas as variáveis, incluindo as novas, para o template
    return render_template(
        'aluno_presenca.html',
        aluno=aluno_data,
        dados_calculados=dados,
        semanas=semanas_do_mes,
        mes_atual=mes_atual,
        ano_atual=ano_atual,
        hoje=hoje,
        chart_data=chart,
        config=app.config,
        # Novas variáveis para os botões de navegação
        ano_anterior=ano_anterior,
        mes_anterior=mes_anterior,
        ano_seguinte=ano_seguinte,
        mes_seguinte=mes_seguinte
    )
# ====================================================================
# FIM DA ALTERAÇÃO
# ====================================================================

@app.route('/aluno/denunciar', methods=['GET', 'POST'])
def aluno_denunciar():
    if session.get('user_type') != 'aluno':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        den_id = str(uuid.uuid4())
        
        denuncia_data = {
            'ID': den_id.split('-')[0].upper(),
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
        
    return render_template('aluno_denunciar.html')

# --- ROTAS DOS PAIS ---
@app.route('/pais/dashboard')
def pais_dashboard():
    if session.get('user_type') != 'pais': return redirect(url_for('login'))
    filho = USERS['alunos'].get(USERS['pais'][session['username']]['filho_matricula'])
    if not filho: return redirect(url_for('logout'))
    return render_template('pais_dashboard.html', filho=filho, dados_calculados=calcular_dados_aluno(filho), config=app.config)

# --- ROTAS DO PROFESSOR ---
@app.route('/professor/dashboard')
def professor_dashboard():
    if session.get('user_type') != 'professor': return redirect(url_for('login'))
    prof_data = USERS['professores'][session['username']]
    disciplinas = prof_data['disciplinas']
    disciplina_sel = request.args.get('disciplina', disciplinas[0])
    alunos_filtrados = []
    for matricula, aluno_data in USERS['alunos'].items():
        if disciplina_sel in aluno_data.get('notas', {}):
            dados = calcular_dados_aluno(aluno_data)
            status_disciplina = dados['medias_materias'].get(disciplina_sel, {}).get('status', 'PENDENTE')
            aluno_info = {'matricula': matricula, 'nome': aluno_data['nome'], 'turma': aluno_data.get('turma', 'N/A'), 'num_faltas': dados['num_faltas'], 'status_disciplina': status_disciplina, 'status_faltas': dados['status_faltas']}
            alunos_filtrados.append(aluno_info)
    return render_template('professor_dashboard.html', alunos=alunos_filtrados, disciplinas=disciplinas, disciplina_selecionada=disciplina_sel)

@app.route('/professor/atualizar-dados/<matricula>/<disciplina>', methods=['GET', 'POST'])
def professor_atualizar_dados(matricula, disciplina):
    if session.get('user_type') != 'professor': return redirect(url_for('login'))
    aluno_data = USERS['alunos'].get(matricula)
    if not aluno_data: return redirect(url_for('professor_dashboard'))
    if disciplina not in USERS['professores'][session['username']]['disciplinas']:
        return redirect(url_for('professor_dashboard'))
        
    if request.method == 'POST':
        n1_str, n2_str = request.form.get(f'nota_{disciplina}_1'), request.form.get(f'nota_{disciplina}_2')
        if n1_str and n2_str:
            try:
                aluno_data['notas'][disciplina] = [float(n1_str), float(n2_str)]
                flash(f'Notas de {disciplina} atualizadas com sucesso!', 'success')
            except ValueError:
                flash('Valor inválido para as notas. Use apenas números.', 'danger')

        num_faltas_str = request.form.get('faltas')
        if num_faltas_str is not None:
            try:
                num_faltas = int(num_faltas_str)
                if num_faltas >= 0:
                    aluno_data['faltas'] = [f'falta_{i+1}' for i in range(num_faltas)]
                    flash(f'Número de faltas atualizado para {num_faltas}.', 'success')
                else:
                    flash('O número de faltas não pode ser negativo.', 'danger')
            except (ValueError, TypeError):
                flash('Valor inválido para o número de faltas. Use apenas números inteiros.', 'danger')
                
        return redirect(url_for('professor_dashboard', disciplina=disciplina))
        
    if disciplina not in aluno_data.get('notas', {}): aluno_data.get('notas', {})[disciplina] = []
    return render_template('professor_atualizar_dados.html', aluno=aluno_data, matricula=matricula, disciplina=disciplina, config=app.config)

# --- ROTAS DO PSICOPEDAGOGO ---
@app.route('/psicopedagogo/dashboard')
def psicopedagogo_dashboard():
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('login'))
    denuncias_abertas = [{'id': id, 'aluno_nome': USERS['alunos'].get(d['aluno_matricula'], {'nome': 'N/A'})['nome'], **d} for id, d in DENUNCIAS.items() if d['status'] == 'aberta']
    denuncias_ordenadas = sorted(denuncias_abertas, key=lambda d: (d['urgencia'] == 'não classificada'), reverse=True)
    return render_template('psicopedagogo_dashboard.html', denuncias=denuncias_ordenadas)

@app.route('/psicopedagogo/definir_urgencia/<denuncia_id>', methods=['POST'])
def definir_urgencia(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('login'))
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['urgencia'] = request.form['urgencia']
        flash('Urgência da denúncia atualizada.', 'success')
    return redirect(url_for('psicopedagogo_dashboard'))

@app.route('/psicopedagogo/denuncia/<denuncia_id>')
def denuncia_detalhe(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('login'))
    denuncia = DENUNCIAS.get(denuncia_id)
    if not denuncia: return redirect(url_for('psicopedagogo_dashboard'))
    aluno = USERS['alunos'].get(denuncia['aluno_matricula'], {})
    return render_template('denuncia_detalhe.html', denuncia_id=denuncia_id, denuncia=denuncia, aluno=aluno, dados_calculados=calcular_dados_aluno(aluno) if aluno else {}, config=app.config)

@app.route('/psicopedagogo/fechar_caso/<denuncia_id>', methods=['POST'])
def psicopedagogo_fechar_caso(denuncia_id):
    if session.get('user_type') != 'psicopedagogo':
        return redirect(url_for('login'))
    
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['status'] = 'fechada'
        flash('Caso fechado com sucesso.', 'success')
    else:
        flash('Denúncia não encontrada.', 'danger')
        
    return redirect(url_for('psicopedagogo_dashboard'))

if __name__ == '__main__':
    app.config.update(NOTA_MINIMA_APROVACAO_MATERIA=NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)
    app.run(debug=True)