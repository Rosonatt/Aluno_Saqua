from flask import Flask, render_template, request, redirect, url_for, session, flash
import uuid # Para gerar IDs únicos para denúncias

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Chave secreta para sessões

# --- CONFIGURAÇÕES GLOBAIS DE REGRAS ---
MAX_FALTAS_PERMITIDAS = 8
TOTAL_AULAS_PADRAO = 100 # Para calcular porcentagem de faltas (ex: 8 faltas = 8%)
NOTA_MINIMA_APROVACAO_MATERIA = 14 # Soma das duas notas para aprovação (7 em uma escala de 10)

# Matérias padrão do Ensino Fundamental para inicializar novos alunos
MATERIAS_ENSINO_FUNDAMENTAL = [
    'Português', 'Matemática', 'História', 'Geografia',
    'Ciências', 'Artes', 'Educação Física', 'Inglês'
]
# --- FIM DAS CONFIGURAÇÕES ---

# Banco de dados em memória para o MVP (substituir por DB real em produção)
# Senhas são armazenadas em texto simples para simplicidade do MVP, NÃO FAÇA ISSO EM PRODUÇÃO!
USERS = {
    'alunos': {},  # {matricula: {'password': 'pwd', 'nome': 'Nome Aluno', 'turma': '1A', 'notas': {'Matemática': [8, 7]}, 'faltas': 2}}
    'pais': {},    # {username: {'password': 'pwd', 'filho_matricula': '123'}}
    'professores': {}, # {username: {'password': 'pwd', 'disciplina': 'Matemática'}}
    'psicopedagogos': {} # {username: {'password': 'pwd'}}
}

DENUNCIAS = {} # {denuncia_id: {'aluno_matricula': '123', 'descricao': '...', 'urgencia': 'baixa', 'status': 'aberta'}}

# Adicionar alguns dados de teste
# Nomes completos dos alunos conforme solicitado, com TURMA e todas as MATÉRIAS PADRÃO
# As notas são exemplos; para novas matérias em alunos existentes, use [0,0]
USERS['alunos']['12345'] = {'password': 'aluno', 'nome': 'Rosonatt Ferreira Ramos', 'turma': '9A', 'notas': {
    'Matemática': [8, 7], 'Português': [9, 8], 'História': [7, 7], 'Geografia': [0,0], 'Ciências': [8,9], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [0,0]
}, 'faltas': 2}
USERS['alunos']['67890'] = {'password': 'aluno', 'nome': 'Ryan Guiwison', 'turma': '8B', 'notas': {
    'Matemática': [5,4], 'Português': [0,0], 'História': [6, 7.5], 'Geografia': [0,0], 'Ciências': [9, 9.5], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [0,0]
}, 'faltas': 9} # Reprovado por falta
USERS['alunos']['11223'] = {'password': 'aluno', 'nome': 'Bruno Alves', 'turma': '7C', 'notas': {
    'Matemática': [0,0], 'Português': [7,6.5], 'História': [0,0], 'Geografia': [7.5, 9], 'Ciências': [0,0], 'Artes': [5, 4], 'Educação Física': [0,0], 'Inglês': [0,0]
}, 'faltas': 1} # Reprovado em Artes e Português
USERS['alunos']['22334'] = {'password': 'aluno', 'nome': 'Natalia Crys Cardoso', 'turma': '9A', 'notas': {
    'Matemática': [0,0], 'Português': [0,0], 'História': [0,0], 'Geografia': [0,0], 'Ciências': [0,0], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [8.5, 9], 'Física': [6.5, 7.5] # Exemplo de matéria extra
}, 'faltas': 0}
USERS['alunos']['33445'] = {'password': 'aluno', 'nome': 'Kevin Paula', 'turma': '6D', 'notas': {
    'Matemática': [0,0], 'Português': [0,0], 'História': [0,0], 'Geografia': [0,0], 'Ciências': [0,0], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [0,0], 'Química': [7, 7], 'Literatura': [8, 6] # Exemplo de matéria extra
}, 'faltas': 3}
USERS['alunos']['44556'] = {'password': 'aluno', 'nome': 'Raissa Leite', 'turma': '5E', 'notas': {
    'Matemática': [0,0], 'Português': [0,0], 'História': [0,0], 'Geografia': [0,0], 'Ciências': [0,0], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [0,0], 'Sociologia': [9, 8.5], 'Filosofia': [7, 7] # Exemplo de matéria extra
}, 'faltas': 1}
USERS['alunos']['55667'] = {'password': 'aluno', 'nome': 'João Candia', 'turma': '4F', 'notas': {
    'Matemática': [0,0], 'Português': [0,0], 'História': [0,0], 'Geografia': [0,0], 'Ciências': [0,0], 'Artes': [0,0], 'Educação Física': [9.5, 9], 'Inglês': [0,0], 'Biologia': [6, 6.5] # Exemplo de matéria extra
}, 'faltas': 0} # Reprovado em Biologia
USERS['alunos']['66778'] = {'password': 'aluno', 'nome': 'Ronald Carvalho', 'turma': '3G', 'notas': {
    'Matemática': [7, 7], 'Português': [7.5, 7.5], 'História': [0,0], 'Geografia': [0,0], 'Ciências': [0,0], 'Artes': [0,0], 'Educação Física': [0,0], 'Inglês': [0,0]
}, 'faltas': 2}


USERS['pais']['pai_rosanatt'] = {'password': 'pai', 'filho_matricula': '12345'}
USERS['professores']['prof_mat'] = {'password': 'prof', 'disciplina': 'Matemática'}
USERS['psicopedagogos']['psi_joana'] = {'password': 'psi'}

# --- NOVOS LOGINS ADICIONADOS ---
# Mais logins de Professores
USERS['professores']['prof_port'] = {'password': 'prof2', 'disciplina': 'Português'}
USERS['professores']['prof_hist'] = {'password': 'prof3', 'disciplina': 'História'}
USERS['professores']['prof_cienc'] = {'password': 'prof4', 'disciplina': 'Ciências'}
USERS['professores']['prof_edfis'] = {'password': 'prof5', 'disciplina': 'Educação Física'}
USERS['professores']['prof_geo'] = {'password': 'prof6', 'disciplina': 'Geografia'}
USERS['professores']['prof_artes'] = {'password': 'prof7', 'disciplina': 'Artes'}
USERS['professores']['prof_ingles'] = {'password': 'prof8', 'disciplina': 'Inglês'}


# Mais logins de Pais
USERS['pais']['pai_ryan'] = {'password': 'pai2', 'filho_matricula': '67890'}
USERS['pais']['pai_bruno'] = {'password': 'mae', 'filho_matricula': '11223'}
USERS['pais']['mae_natalia'] = {'password': 'pais', 'filho_matricula': '22334'}
USERS['pais']['pai_kevin'] = {'password': 'pais2', 'filho_matricula': '33445'}
USERS['pais']['mae_raissa'] = {'password': 'pais3', 'filho_matricula': '44556'}
USERS['pais']['pai_joao'] = {'password': 'pais4', 'filho_matricula': '55667'}
USERS['pais']['mae_ronald'] = {'password': 'pais5', 'filho_matricula': '66778'}

# Mais logins de Psicopedagogos
USERS['psicopedagogos']['psi_pedro'] = {'password': 'psi2'}
USERS['psicopedagogos']['coord_educ'] = {'password': 'coord'}
USERS['psicopedagogos']['sup_psi'] = {'password': 'sup'}


DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '12345', 'descricao': 'Rosonatt está sendo excluído nos trabalhos em grupo.', 'urgencia': 'média', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '67890', 'descricao': 'Ryan foi alvo de piadas sobre sua aparência na aula de educação física.', 'urgencia': 'alta', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '11223', 'descricao': 'Bruno tem sido ignorado pelos colegas durante o recreio.', 'urgencia': 'baixa', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '22334', 'descricao': 'Natalia recebeu mensagens ofensivas em um grupo de chat da turma.', 'urgencia': 'alta', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '33445', 'descricao': 'Kevin se queixou de objetos escondidos em sua mochila por colegas.', 'urgencia': 'média', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '44556', 'descricao': 'Raissa está sendo constantemente interrompida e desacreditada nas apresentações.', 'urgencia': 'baixa', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '55667', 'descricao': 'João teve seus materiais escolares danificados no armário.', 'urgencia': 'alta', 'status': 'aberta'}
DENUNCIAS[str(uuid.uuid4())] = {'aluno_matricula': '66778', 'descricao': 'Ronald tem sido alvo de apelidos pejorativos por parte de um grupo de alunos.', 'urgencia': 'média', 'status': 'aberta'}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']

        if user_type == 'aluno':
            if username in USERS['alunos'] and USERS['alunos'][username]['password'] == password:
                session['user_type'] = user_type
                session['username'] = username
                flash('Login de aluno realizado com sucesso!', 'success')
                return redirect(url_for('aluno_dashboard'))
        elif user_type == 'pais':
            if username in USERS['pais'] and USERS['pais'][username]['password'] == password:
                session['user_type'] = user_type
                session['username'] = username
                flash('Login de pais realizado com sucesso!', 'success')
                return redirect(url_for('pais_dashboard'))
        elif user_type == 'professor':
            if username in USERS['professores'] and USERS['professores'][username]['password'] == password:
                session['user_type'] = user_type
                session['username'] = username
                flash('Login de professor realizado com sucesso!', 'success')
                return redirect(url_for('professor_dashboard'))
        elif user_type == 'psicopedagogo':
            if username in USERS['psicopedagogos'] and USERS['psicopedagogos'][username]['password'] == password:
                session['user_type'] = user_type
                session['username'] = username
                flash('Login de psicopedagogo realizado com sucesso!', 'success')
                return redirect(url_for('psicopedagogo_dashboard'))

        flash('Usuário ou senha incorretos. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        matricula = request.form['matricula']
        password = request.form['password']
        nome = request.form['nome']
        # Alunos novos não tem turma no cadastro inicial, será adicionado depois pelo admin/professor
        # Para um MVP, podemos atribuir uma turma padrão aqui ou deixar vazio.
        turma = request.form.get('turma', 'Turma Padrão') # Pode adicionar um campo no form ou definir um padrão

        if matricula in USERS['alunos']:
            flash('Matrícula já cadastrada. Por favor, faça login.', 'warning')
        else:
            # Inicializa um novo aluno com todas as matérias padrão, com notas vazias
            initial_notas = {materia: [] for materia in MATERIAS_ENSINO_FUNDAMENTAL}
            USERS['alunos'][matricula] = {'password': password, 'nome': nome, 'turma': turma, 'notas': initial_notas, 'faltas': 0}
            flash('Cadastro de aluno realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_type', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# --- Funções Auxiliares para Cálculos ---
def calcular_dados_aluno(aluno_data):
    # Cálculo de faltas
    porcentagem_faltas = (aluno_data['faltas'] / TOTAL_AULAS_PADRAO) * 100
    status_faltas = 'REPROVADO POR FALTAS' if aluno_data['faltas'] > MAX_FALTAS_PERMITIDAS else 'APROVADO POR FALTAS'
    
    # Dados para gráfico de faltas (presente/ausente)
    faltas_grafico = {
        'ausente': porcentagem_faltas,
        'presente': 100 - porcentagem_faltas
    }

    # Cálculo de notas por matéria e status
    medias_materias = {}
    materias_reprovadas = []
    
    # Para o gráfico de notas geral
    total_disciplinas = len(aluno_data['notas'])
    
    for disciplina, notas_list in aluno_data['notas'].items():
        if isinstance(notas_list, list) and len(notas_list) == 2:
            soma_notas = sum(notas_list)
            status_materia = 'APROVADO' if soma_notas >= NOTA_MINIMA_APROVACAO_MATERIA else 'REPROVADO'
            
            medias_materias[disciplina] = {
                'nota1': notas_list[0],
                'nota2': notas_list[1],
                'soma': soma_notas,
                'status': status_materia
            }
            if status_materia == 'REPROVADO':
                materias_reprovadas.append(disciplina)
        elif isinstance(notas_list, list) and len(notas_list) < 2: # Matéria com menos de 2 notas
             medias_materias[disciplina] = {'nota1': (notas_list[0] if len(notas_list) > 0 else 'N/A'),
                                            'nota2': 'N/A',
                                            'soma': 'N/A',
                                            'status': 'FALTAM NOTAS'} # Indica que faltam notas para calcular
             materias_reprovadas.append(disciplina) # Considera como reprovado ou em progresso para atenção
        else: # Formato de nota inválido
            medias_materias[disciplina] = {'nota1': 'N/A', 'nota2': 'N/A', 'soma': 'N/A', 'status': 'ERRO NO FORMATO'}
            materias_reprovadas.append(disciplina) # Considera como reprovado para atenção

    # Status geral de notas
    status_geral_notas = 'APROVADO POR NOTA'
    if materias_reprovadas:
        status_geral_notas = 'REPROVADO POR NOTA'
        
    # Dados para gráfico de notas (aprovado/reprovado por disciplina)
    # Garante que total_disciplinas não é zero para evitar divisão por zero
    if total_disciplinas > 0:
        aprovadas_percent = ((total_disciplinas - len(materias_reprovadas)) / total_disciplinas) * 100
        reprovadas_percent = (len(materias_reprovadas) / total_disciplinas) * 100
    else:
        aprovadas_percent = 0
        reprovadas_percent = 0


    notas_grafico = {
        'reprovadas': round(reprovadas_percent, 2),
        'aprovadas': round(aprovadas_percent, 2)
    }


    # Status final do aluno (combinando faltas e notas)
    status_final = 'APROVADO'
    if status_faltas == 'REPROVADO POR FALTAS' or status_geral_notas == 'REPROVADO POR NOTA':
        status_final = 'REPROVADO'
        if status_faltas == 'REPROVADO POR FALTAS' and status_geral_notas == 'REPROVADO POR NOTA':
            status_final = 'REPROVADO (Faltas e Notas)'
        elif status_faltas == 'REPROVADO POR FALTAS':
            status_final = 'REPROVADO (Faltas)'
        elif status_geral_notas == 'REPROVADO POR NOTA':
            status_final = 'REPROVADO (Notas)'
    else:
        status_final = 'APROVADO'


    return {
        'porcentagem_faltas': round(porcentagem_faltas, 2),
        'status_faltas': status_faltas,
        'status_final_aluno': status_final,
        'medias_materias': medias_materias,
        'materias_reprovadas': materias_reprovadas, # Nova lista de matérias reprovadas
        'status_geral_notas': status_geral_notas,
        'faltas_grafico': faltas_grafico, # Dados para o gráfico de faltas
        'notas_grafico': notas_grafico # Dados para o gráfico de notas
    }


# --- Dashboards ---

@app.route('/aluno/dashboard')
def aluno_dashboard():
    if 'user_type' not in session or session['user_type'] != 'aluno':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    aluno_data = USERS['alunos'][session['username']]
    
    # Calcular dados dinamicamente antes de enviar para o template
    dados_calculados = calcular_dados_aluno(aluno_data)
    
    return render_template('aluno_dashboard.html', 
                           aluno=aluno_data, 
                           dados_calculados=dados_calculados,
                           config=app.config) # Passa config para o template

@app.route('/aluno/denunciar', methods=['GET', 'POST'])
def aluno_denunciar():
    if 'user_type' not in session or session['user_type'] != 'aluno':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        descricao = request.form['descricao']
        urgencia = request.form['urgencia']
        denuncia_id = str(uuid.uuid4())
        DENUNCIAS[denuncia_id] = {
            'aluno_matricula': session['username'],
            'descricao': descricao,
            'urgencia': urgencia,
            'status': 'aberta'
        }
        flash('Denúncia enviada com sucesso! Ela é anônima para a equipe de psicopedagogia.', 'success')
        return redirect(url_for('aluno_dashboard'))
    return render_template('aluno_denunciar.html') 

@app.route('/pais/dashboard')
def pais_dashboard():
    if 'user_type' not in session or session['user_type'] != 'pais':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))

    pai_data = USERS['pais'][session['username']]
    filho_matricula = pai_data['filho_matricula']
    filho_data = USERS['alunos'].get(filho_matricula)

    if not filho_data:
        flash('Matrícula do filho não encontrada. Verifique se o pai está associado a um aluno existente.', 'danger')
        return redirect(url_for('logout')) 

    # Calcular dados dinamicamente antes de enviar para o template
    dados_calculados_filho = calcular_dados_aluno(filho_data)

    return render_template('pais_dashboard.html', 
                           filho=filho_data, 
                           dados_calculados=dados_calculados_filho,
                           config=app.config) # Passa config para o template

@app.route('/professor/dashboard')
def professor_dashboard():
    if 'user_type' not in session or session['user_type'] != 'professor':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    professor_data = USERS['professores'][session['username']]
    disciplina_professor = professor_data.get('disciplina')

    alunos_para_professor = {}
    for matricula, aluno_data in USERS['alunos'].items():
        dados_calculados = calcular_dados_aluno(aluno_data)
        
        # Filtra alunos pela disciplina do professor para a tabela principal
        # Apenas adiciona o aluno se ele tiver a disciplina do professor
        # ou se o professor for "geral" (sem disciplina específica)
        if disciplina_professor:
            if disciplina_professor in aluno_data['notas']: # Aluno tem a disciplina que o professor ensina
                # Pega a soma e o status da disciplina específica para a tabela do professor
                nota_disciplina = dados_calculados['medias_materias'].get(disciplina_professor, {'soma': 'N/A', 'status': 'N/A'})
                alunos_para_professor[matricula] = {
                    **aluno_data,
                    'matricula_aluno': matricula,
                    'nota_disciplina_professor_soma': nota_disciplina['soma'],
                    'status_disciplina_professor': nota_disciplina['status'],
                    **dados_calculados # Mantém outros dados calculados (faltas, status final)
                }
        else: # Professor sem disciplina específica (geral), pode ver todos os alunos
            alunos_para_professor[matricula] = {**aluno_data, 'matricula_aluno': matricula, **dados_calculados}
        
    # Ordenar alunos pela turma e depois pelo nome
    alunos_ordenados = sorted(alunos_para_professor.values(), key=lambda x: (x.get('turma', ''), x['nome']))


    return render_template('professor_dashboard.html', alunos=alunos_ordenados, disciplina_professor=disciplina_professor)

@app.route('/professor/atualizar_dados/<matricula>', methods=['GET', 'POST'])
def professor_atualizar_dados(matricula):
    if 'user_type' not in session or session['user_type'] != 'professor':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    professor_data = USERS['professores'][session['username']]
    disciplina_professor = professor_data.get('disciplina')

    aluno_data = USERS['alunos'].get(matricula)
    if not aluno_data:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('professor_dashboard'))

    if request.method == 'POST':
        # Atualizar faltas (se o professor tiver permissão geral de faltas ou se for um professor de turma)
        # Para simplificar o MVP, qualquer professor pode atualizar faltas.
        faltas = request.form.get('faltas', type=int)
        if faltas is not None:
            aluno_data['faltas'] = faltas
        
        # Lógica para atualizar notas
        # O professor só atualiza a disciplina que ele leciona ou, se for geral, todas as que vê no form
        if disciplina_professor: # Professor com disciplina específica
            nota1_str = request.form.get(f'nota_{disciplina_professor}_1')
            nota2_str = request.form.get(f'nota_{disciplina_professor}_2')
            
            # Garante que a disciplina do professor exista nas notas do aluno
            if disciplina_professor not in aluno_data['notas']:
                aluno_data['notas'][disciplina_professor] = [] # Inicializa se não existir
            
            if nota1_str is not None and nota2_str is not None:
                try:
                    aluno_data['notas'][disciplina_professor] = [float(nota1_str), float(nota2_str)]
                    flash(f'Notas de {disciplina_professor} para {aluno_data["nome"]} atualizadas com sucesso!', 'success')
                except ValueError:
                    flash(f'Notas inválidas para {disciplina_professor}. Certifique-se de que são números.', 'warning')
            else:
                flash(f'Preencha ambas as notas para {disciplina_professor}.', 'warning')
        else: # Professor sem disciplina específica (geral)
            # Ele pode atualizar qualquer disciplina que apareça no formulário
            for disciplina_nome in request.form:
                if disciplina_nome.startswith('nota_') and disciplina_nome.endswith('_1'):
                    disciplina = disciplina_nome.replace('nota_', '').replace('_1', '')
                    nota1_str = request.form.get(f'nota_{disciplina}_1')
                    nota2_str = request.form.get(f'nota_{disciplina}_2')

                    if disciplina not in aluno_data['notas']:
                        aluno_data['notas'][disciplina] = []
                    
                    if nota1_str is not None and nota2_str is not None:
                        try:
                            aluno_data['notas'][disciplina] = [float(nota1_str), float(nota2_str)]
                            flash(f'Notas de {disciplina} para {aluno_data["nome"]} atualizadas com sucesso!', 'success')
                        except ValueError:
                            flash(f'Notas inválidas para {disciplina}. Certifique-se de que são números.', 'warning')
        
        # Lógica para adicionar uma nova disciplina completa (se o professor tiver permissão)
        # Para o MVP, qualquer professor pode adicionar uma nova disciplina, se não existir
        nova_disciplina_nome = request.form.get('nova_disciplina_nome')
        nova_disciplina_nota1 = request.form.get('nova_disciplina_nota1')
        nova_disciplina_nota2 = request.form.get('nova_disciplina_nota2')

        if nova_disciplina_nome:
            if nova_disciplina_nome not in aluno_data['notas']:
                if nova_disciplina_nota1 and nova_disciplina_nota2:
                    try:
                        aluno_data['notas'][nova_disciplina_nome] = [float(nova_disciplina_nota1), float(nova_disciplina_nota2)]
                        flash(f'Disciplina "{nova_disciplina_nome}" adicionada com sucesso para {aluno_data["nome"]}!', 'success')
                    except ValueError:
                        flash('Notas da nova disciplina devem ser números.', 'warning')
                else:
                    flash('Por favor, insira as duas notas para a nova disciplina.', 'warning')
            else:
                flash(f'Disciplina "{nova_disciplina_nome}" já existe para {aluno_data["nome"]}.', 'info')


        return redirect(url_for('professor_dashboard'))
    
    # Ao carregar a página de atualização, garantir que o aluno tenha as matérias corretas para o professor
    if disciplina_professor: # Professor com disciplina específica, só verá a sua
        if disciplina_professor not in aluno_data['notas']:
            aluno_data['notas'][disciplina_professor] = [] # Garante que a disciplina do professor exista para o aluno
        # Aqui, podemos criar um dicionário de notas filtrado para passar ao template
        aluno_notas_filtradas = {disciplina_professor: aluno_data['notas'][disciplina_professor]}
        aluno_data['notas'] = aluno_notas_filtradas # Sobrescreve para o template só ver a dele
    else: # Professor geral, vê todas as padrão e extras
        for materia in MATERIAS_ENSINO_FUNDAMENTAL:
            if materia not in aluno_data['notas']:
                aluno_data['notas'][materia] = [] # Inicializa com lista vazia para exibição

    return render_template('professor_atualizar_dados.html', aluno=aluno_data, config=app.config, disciplina_professor=disciplina_professor)


@app.route('/psicopedagogo/dashboard')
def psicopedagogo_dashboard():
    if 'user_type' not in session or session['user_type'] != 'psicopedagogo':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    # Classificar denúncias por urgência e status 'aberta'
    denuncias_urgencia = {'alta': [], 'média': [], 'baixa': []}
    for denuncia_id, denuncia_info in DENUNCIAS.items():
        if denuncia_info['status'] == 'aberta': # Apenas denúncias abertas
            # Adicionar nome do aluno e notas para o psicopedagogo ter contexto
            aluno_info = USERS['alunos'].get(denuncia_info['aluno_matricula'], {'nome': 'Aluno Desconhecido', 'notas': {}})
            dados_calculados_aluno = calcular_dados_aluno(aluno_info)
            denuncia_info_com_nome = {
                **denuncia_info,
                'aluno_nome': aluno_info['nome'],
                'aluno_notas_calculadas': dados_calculados_aluno['medias_materias'] # Passa as notas calculadas
            }
            denuncias_urgencia[denuncia_info['urgencia']].append({'id': denuncia_id, **denuncia_info_com_nome})
    
    return render_template('psicopedagogo_dashboard.html', denuncias=denuncias_urgencia, config=app.config)

@app.route('/psicopedagogo/denuncia/<denuncia_id>')
def denuncia_detalhe(denuncia_id):
    if 'user_type' not in session or session['user_type'] != 'psicopedagogo':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    denuncia = DENUNCIAS.get(denuncia_id)
    if not denuncia:
        flash('Denúncia não encontrada.', 'danger')
        return redirect(url_for('psicopedagogo_dashboard'))
    
    # Adicionar nome do aluno e dados calculados de notas para o psicopedagogo
    aluno_info = USERS['alunos'].get(denuncia['aluno_matricula'], {'nome': 'Aluno Desconhecido', 'notas': {}})
    dados_calculados_aluno = calcular_dados_aluno(aluno_info)

    return render_template('denuncia_detalhe.html', 
                           denuncia=denuncia, 
                           denuncia_id=denuncia_id, 
                           aluno_nome=aluno_info['nome'],
                           aluno_notas_calculadas=dados_calculados_aluno['medias_materias'], # Passa as notas calculadas
                           config=app.config)

@app.route('/psicopedagogo/fechar_denuncia/<denuncia_id>', methods=['POST'])
def fechar_denuncia(denuncia_id):
    if 'user_type' not in session or session['user_type'] != 'psicopedagogo':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('login'))
    
    if denuncia_id in DENUNCIAS:
        DENUNCIAS[denuncia_id]['status'] = 'fechada'
        flash('Denúncia marcada como fechada.', 'success')
    else:
        flash('Denúncia não encontrada.', 'danger')
    return redirect(url_for('psicopedagogo_dashboard'))


if __name__ == '__main__':
    # Define as configurações no app para poder acessá-las nos templates
    app.config['MAX_FALTAS_PERMITIDAS'] = MAX_FALTAS_PERMITIDAS
    app.config['TOTAL_AULAS_PADRAO'] = TOTAL_AULAS_PADRAO
    app.config['NOTA_MINIMA_APROVACAO_MATERIA'] = NOTA_MINIMA_APROVACAO_MATERIA
    app.config['MATERIAS_ENSINO_FUNDAMENTAL'] = MATERIAS_ENSINO_FUNDAMENTAL

    app.run(debug=True)