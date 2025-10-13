from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import uuid
import calendar
from datetime import datetime, timedelta
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except locale.Error:
        print("Locale pt_BR não encontrado.")


# Importa dados e configurações do nosso novo arquivo de modelos
from .models import USERS, DENUNCIAS, calcular_dados_aluno, NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS, HOLIDAYS_2025

main_bp = Blueprint('main', __name__)
aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')
pais_bp = Blueprint('pais', __name__, url_prefix='/pais')
professor_bp = Blueprint('professor', __name__, url_prefix='/professor')
psicopedagogo_bp = Blueprint('psicopedagogo', __name__, url_prefix='/psicopedagogo')


# --- ROTAS PRINCIPAIS ---
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/informacoes-cadastro')
def informacoes_cadastro():
    return render_template('informacoes_cadastro.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type, username, password = request.form['user_type'], request.form['username'].strip(), request.form['password']
        
        user_map = {
            'aluno': ('alunos', 'aluno.dashboard'), 
            'pais': ('pais', 'pais.dashboard'), 
            'professor': ('professores', 'professor.dashboard'), 
            'psicopedagogo': ('psicopedagogos', 'psicopedagogo.dashboard')
        }
        
        if user_type in user_map:
            cat, endp = user_map[user_type]
            user = USERS[cat].get(username)
            
            if user and check_password_hash(user.get('password'), password):
                session['user_type'] = user_type
                session['username'] = username
                session['display_name'] = user['nome']
                redirect_url = url_for(endp)
                return render_template('loading.html', redirect_url=redirect_url)
        
        flash('Usuário ou senha incorretos.', 'danger')
        
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# --- ROTAS DO ALUNO ---
@aluno_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    
    aluno = USERS['alunos'].get(session['username'])
    if not aluno: return redirect(url_for('main.logout')) 
    
    return render_template('aluno_dashboard.html', aluno=aluno)

@aluno_bp.route('/notas')
def notas():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    aluno_data = USERS['alunos'].get(session['username'])
    if not aluno_data: return redirect(url_for('main.logout'))

    return render_template('aluno_notas.html', aluno=aluno_data, dados_calculados=calcular_dados_aluno(aluno_data), config={'NOTA_MINIMA_APROVACAO_MATERIA': NOTA_MINIMA_APROVACAO_MATERIA})

@aluno_bp.route('/presenca')
def presenca():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    
    aluno_data = USERS['alunos'].get(session['username'])
    if not aluno_data: return redirect(url_for('main.logout'))

    # Lógica para obter o mês e ano da URL, ou usar a data atual
    try:
        ano_atual = int(request.args.get('ano', datetime.now().year))
        mes_atual = int(request.args.get('mes', datetime.now().month))
        if not 1 <= mes_atual <= 12: raise ValueError("Mês inválido")
    except (ValueError, TypeError):
        ano_atual, mes_atual = datetime.now().year, datetime.now().month

    # Lógica para navegação do calendário
    primeiro_dia_do_mes = datetime(ano_atual, mes_atual, 1)
    mes_anterior_data = primeiro_dia_do_mes - timedelta(days=1)
    ano_anterior, mes_anterior = mes_anterior_data.year, mes_anterior_data.month
    _, ultimo_dia_num = calendar.monthrange(ano_atual, mes_atual)
    ultimo_dia_do_mes = datetime(ano_atual, mes_atual, ultimo_dia_num)
    mes_seguinte_data = ultimo_dia_do_mes + timedelta(days=1)
    ano_seguinte, mes_seguinte = mes_seguinte_data.year, mes_seguinte_data.month

    dados = calcular_dados_aluno(aluno_data)
    
    # 1. Obter e Validar a Disciplina Selecionada
    disciplinas_aluno = sorted(aluno_data.get('notas', {}).keys())
    
    default_discipline = disciplinas_aluno[0] if disciplinas_aluno else 'Matemática'
    disciplina_sel = request.args.get('disciplina', default_discipline)
    
    # 2. CÁLCULO ESTATÍSTICO DA DISCIPLINA SELECIONADA
    faltas_disciplina_total = dados['detalhe_faltas_por_materia'].get(disciplina_sel, {'total': 0, 'justificadas': 0})
    num_faltas_disciplina = faltas_disciplina_total['total']
    num_justificadas_disciplina = faltas_disciplina_total['justificadas']
    num_nao_justificadas_disciplina = num_faltas_disciplina - num_justificadas_disciplina
    
    status_disciplina_faltas = 'REPROVADO POR FALTAS' if num_nao_justificadas_disciplina > MAX_FALTAS_PERMITIDAS else 'APROVADO'
    
    subject_stats={
        'total_faltas': num_faltas_disciplina,
        'justificadas': num_justificadas_disciplina,
        'nao_justificadas': num_nao_justificadas_disciplina,
        'status': status_disciplina_faltas
    }
    
    # 3. Prepara dados para o calendário
    cal = calendar.Calendar()
    cal.setfirstweekday(calendar.SUNDAY)
    semanas_do_mes = cal.monthdatescalendar(ano_atual, mes_atual)
    
    # Consolida todas as faltas (para o gráfico global)
    todas_as_faltas = set()
    for faltas_obj_list in aluno_data.get('faltas', {}).values():
        for falta_dict in faltas_obj_list:
            todas_as_faltas.add(falta_dict['date'])
    
    # Faltas para marcar no calendário (SÓ DA DISCIPLINA SELECIONADA)
    faltas_disciplina = set()
    if disciplina_sel:
        for falta_dict in aluno_data.get('faltas', {}).get(disciplina_sel, []):
            faltas_disciplina.add(falta_dict['date'])
        
    provas_disciplina = aluno_data.get('provas', {}).get(disciplina_sel, [])
    
    dias_nao_letivos = HOLIDAYS_2025 # Feriados

    proximos_feriados = []
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    for data_str in HOLIDAYS_2025:
        if data_str >= hoje_str:
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                nome_feriado = data_obj.strftime('%d/%m/%Y (%A)') 
                proximos_feriados.append({'data': data_obj, 'nome': nome_feriado})
            except ValueError:
                continue
    
    proximos_feriados_ordenados = sorted(proximos_feriados, key=lambda x: x['data'])[:5]
    
    return render_template(
        'aluno_presenca.html',
        aluno=aluno_data,
        dados_calculados=dados,
        semanas=semanas_do_mes,
        mes_atual=mes_atual,
        ano_atual=ano_atual,
        hoje=datetime.now().date(),
        chart_data={'presente': 100 - dados['porcentagem_faltas'], 'ausente': dados['porcentagem_faltas']},
        ano_anterior=ano_anterior, mes_anterior=mes_anterior,
        ano_seguinte=ano_seguinte, mes_seguinte=mes_seguinte,
        todas_as_faltas=todas_as_faltas,
        dias_nao_letivos=dias_nao_letivos,
        proximos_feriados=proximos_feriados_ordenados,
        MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS,
        
        # VARIÁVEIS CHAVE PASSADAS AO TEMPLATE
        faltas_disciplina=faltas_disciplina, 
        provas_disciplina=provas_disciplina,
        disciplina_selecionada=disciplina_sel,
        disciplinas_aluno=disciplinas_aluno,
        subject_stats=subject_stats # Variável agora está sendo passada
    )

@aluno_bp.route('/denunciar', methods=['GET', 'POST'])
def denunciar():
    if session.get('user_type') != 'aluno': return redirect(url_for('main.login'))
    if request.method == 'POST':
        den_id = str(uuid.uuid4())
        denuncia_data = {
            'id': den_id,
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
        return redirect(url_for('aluno.dashboard'))
    return render_template('aluno_denunciar.html')


# --- ROTAS DOS PAIS ---
@pais_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'pais': return redirect(url_for('main.login'))
    
    filho_matricula = USERS['pais'].get(session['username'], {}).get('filho_matricula', '').strip()
    filho = USERS['alunos'].get(filho_matricula)
    if not filho: return redirect(url_for('main.logout'))
    
    return render_template('pais_dashboard.html', filho=filho, dados_calculados=calcular_dados_aluno(filho), MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)


# --- ROTAS DO PROFESSOR ---
@professor_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'professor': return redirect(url_for('main.login'))
    
    prof_data = USERS['professores'].get(session['username'])
    if not prof_data: return redirect(url_for('main.logout'))

    disciplinas = prof_data['disciplinas']
    disciplina_sel = request.args.get('disciplina', disciplinas[0])
    alunos_filtrados = []
    for matricula, aluno_data in USERS['alunos'].items():
        dados = calcular_dados_aluno(aluno_data)
        info_disciplina = dados['medias_materias'].get(disciplina_sel, {})
        aluno_info = {
            'matricula': matricula, 'nome': aluno_data['nome'],
            'nota1': info_disciplina.get('nota1', 'N/A'),
            'nota2': info_disciplina.get('nota2', 'N/A'),
            'media': info_disciplina.get('media', 'N/A'),
            'faltas_nao_justificadas': dados['num_nao_justificadas'], 
            'faltas': dados['faltas_por_materia'].get(disciplina_sel, 0)
        }
        alunos_filtrados.append(aluno_info)
    return render_template('professor_dashboard.html', alunos=alunos_filtrados, disciplinas=disciplinas, disciplina_selecionada=disciplina_sel, NOTA_MINIMA=NOTA_MINIMA_APROVACAO_MATERIA, MAX_FALTAS_PERMITIDAS=MAX_FALTAS_PERMITIDAS)

@professor_bp.route('/atualizar-dados/<matricula>', methods=['GET', 'POST'])
def atualizar_dados(matricula):
    if session.get('user_type') != 'professor': return redirect(url_for('main.login'))
    
    prof_data = USERS['professores'].get(session['username'])
    if not prof_data: return redirect(url_for('main.logout'))

    disciplina = request.args.get('disciplina')
    if not disciplina:
        flash('Disciplina não especificada.', 'danger')
        return redirect(url_for('professor.dashboard'))
    
    aluno_data = USERS['alunos'].get(matricula)
    if not aluno_data: return redirect(url_for('professor.dashboard'))
    
    if disciplina not in prof_data['disciplinas']:
        flash(f'Você não tem permissão para editar a disciplina de {disciplina}.', 'danger')
        return redirect(url_for('professor.dashboard'))
    
    if request.method == 'POST':
        # Lógica de Notas
        n1_str, n2_str = request.form.get(f'nota_{disciplina}_1'), request.form.get(f'nota_{disciplina}_2')
        if n1_str and n2_str:
            try:
                if 'notas' not in aluno_data: aluno_data['notas'] = {}
                aluno_data['notas'][disciplina] = [float(n1_str), float(n2_str)]
                flash(f'Notas de {disciplina} atualizadas com sucesso!', 'success')
            except ValueError:
                flash('Valor inválido para as notas. Use apenas números.', 'danger')

        # Lógica de Faltas (processamento da string de datas)
        num_faltas_count = int(request.form.get('num_faltas_count', 0))
        novas_faltas = []
        datas_invalidas = []
        
        for i in range(num_faltas_count):
            data_str = request.form.get(f'falta_data_{i}', '').strip()
            is_justified = request.form.get(f'falta_justificada_{i}') == 'True'
            
            if data_str:
                try:
                    datetime.strptime(data_str, '%Y-%m-%d')
                    novas_faltas.append({'date': data_str, 'justified': is_justified})
                except ValueError:
                    datas_invalidas.append(data_str)
            
        aluno_data.setdefault('faltas', {})[disciplina] = novas_faltas
        
        if novas_faltas:
            flash(f'{len(novas_faltas)} falta(s) em {disciplina} foram salvas/atualizadas. {len(datas_invalidas)} datas ignoradas.', 'success')
        
        if datas_invalidas:
            flash(f'As seguintes datas foram ignoradas por estarem em formato inválido: {", ".join(datas_invalidas)}', 'warning')
        
        return redirect(url_for('professor.dashboard', disciplina=disciplina))
        
    # Lógica GET (Prepara dados para pré-preenchimento)
    faltas_da_disciplina = aluno_data.get('faltas', {}).get(disciplina, [])

    if disciplina not in aluno_data.get('notas', {}):
        aluno_data.setdefault('notas', {})[disciplina] = []
    return render_template('professor_atualizar_dados.html', 
        aluno=aluno_data, 
        matricula=matricula, 
        disciplina=disciplina,
        faltas_da_disciplina=faltas_da_disciplina
    )


# --- ROTAS DO PSICOPEDAGOGO ---
@psicopedagogo_bp.route('/dashboard')
def dashboard():
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    denuncias_abertas = [{'aluno_nome': USERS['alunos'].get(d['aluno_matricula'], {'nome': 'N/A'})['nome'], **d} for id, d in DENUNCIAS.items() if d['status'] == 'aberta']
    denuncias_ordenadas = sorted(denuncias_abertas, key=lambda d: (d['urgencia'] != 'alta', d['urgencia'] != 'média', d['urgencia'] != 'baixa'))
    return render_template('psicopedagogo_dashboard.html', denuncias=denuncias_ordenadas)

@psicopedagogo_bp.route('/definir_urgencia/<denuncia_id>', methods=['POST'])
def definir_urgencia(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['urgencia'] = request.form['urgencia']
        flash('Urgência da denúncia atualizada.', 'success')
    return redirect(url_for('psicopedagogo.dashboard'))

# No arquivo app/routes.py, substitua a função denuncia_detalhe:

@psicopedagogo_bp.route('/denuncia/<denuncia_id>')
def denuncia_detalhe(denuncia_id): # Nome do argumento CORRIGIDO: Agora usa 'denuncia_id'
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    
    denuncia = DENUNCIAS.get(denuncia_id)
    if not denuncia: return redirect(url_for('psicopedagogo.dashboard'))
    aluno = USERS['alunos'].get(denuncia['aluno_matricula'], {})
    
    # Renderiza o template, usando a variável corrigida
    return render_template('denuncia_detalhe.html', denuncia_id=denuncia_id, denuncia=denuncia, aluno=aluno, dados_calculados=calcular_dados_aluno(aluno) if aluno else {})

@psicopedagogo_bp.route('/fechar_caso/<denuncia_id>', methods=['POST'])
def fechar_caso(denuncia_id):
    if session.get('user_type') != 'psicopedagogo': return redirect(url_for('main.login'))
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['status'] = 'fechada'
        flash('Caso fechado com sucesso.', 'success')
    return redirect(url_for('psicopedagogo.dashboard'))