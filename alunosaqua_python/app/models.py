from werkzeug.security import generate_password_hash

# --- CONFIGURAÇÕES GLOBAIS DE REGRAS ---
MAX_FALTAS_PERMITIDAS = 4
TOTAL_AULAS_PADRAO = 100
NOTA_MINIMA_APROVACAO_MATERIA = 7

# --- FERIADOS NACIONAIS 2025 + MUNICIPAIS (SAQUAREMA) ---
HOLIDAYS_2025 = [
    '2025-01-01', # Ano Novo
    '2025-03-03', # Carnaval (Segunda)
    '2025-03-04', # Carnaval (Terça)
    '2025-03-05', # Quarta-feira de Cinzas
    '2025-04-18', # Sexta-feira Santa
    '2025-04-21', # Tiradentes
    '2025-05-01', # Dia do Trabalho
    '2025-06-19', # Corpus Christi
    '2025-09-08', # N. Sra. de Nazareth (Municipal - Saquarema)
    '2025-10-15', # Dia do Professor
    '2025-10-28', # Dia do Servidor Público
    '2025-11-15', # Proclamação da República
    '2025-11-20', # Dia da Consciência Negra
    '2025-12-25', # Natal
]

# --- BANCO DE DADOS SIMULADO (ESTRUTURA ATUALIZADA) ---
USERS = {
    'alunos': {
        '202411251': {'password': generate_password_hash('aluno'), 'nome': 'Rosonatt Ferreira Ramos', 'turma': '9A', 'notas': {'Matemática': [8, 7], 'Português': [9, 8], 'História': [7, 7], 'Ciências': [10, 9]}, 
            'faltas': {'Matemática': [{'date': '2025-10-01', 'justified': False}], 'Português': [{'date': '2025-10-02', 'justified': True}, {'date': '2025-09-15', 'justified': False}]}, 
            'provas': {'Matemática': ['2025-10-06']}},
        '202411281': {'password': generate_password_hash('aluno'), 'nome': 'Ryan Guiwison', 'turma': '8B', 'notas': {'Matemática': [5, 4], 'Português': [6, 7.5], 'Artes': [5, 5]}, 
            'faltas': {'Matemática': [{'date': '2025-10-03', 'justified': False}], 'Português': [{'date': '2025-09-08', 'justified': True}], 'Artes': [{'date': '2025-08-10', 'justified': False}, {'date': '2025-08-15', 'justified': False}, {'date': '2025-08-16', 'justified': False}, {'date': '2025-08-17', 'justified': True}, {'date': '2025-08-18', 'justified': False}]}, 
            'provas': {}},
        '202411333': {'password': generate_password_hash('aluno'), 'nome': 'Bruno Alves', 'turma': '7C', 'notas': {'Artes': [5, 4], 'Português': [7, 6.5]}, 'faltas': {'Artes': [{'date': '2025-09-11', 'justified': False}]}, 'provas': {}},
        '202411325': {'password': generate_password_hash('aluno'), 'nome': 'Natalia Crys Cardoso', 'turma': '9A', 'notas': {'Inglês': [8.5, 9], 'Física': [6.5, 7.5]}, 'faltas': {}, 'provas': {}},
        '202411265': {'password': generate_password_hash('aluno'), 'nome': 'Kevin Paula', 'turma': '6D', 'notas': {'Química': [7, 7], 'Literatura': [8, 6]}, 'faltas': {'Química': [{'date': '2025-09-05', 'justified': False}, {'date': '2025-09-12', 'justified': False}, {'date': '2025-09-19', 'justified': False}]}, 'provas': {}},
        '202411271': {'password': generate_password_hash('aluno'), 'nome': 'Raissa Leite', 'turma': '5E', 'notas': {'Sociologia': [9, 8.5], 'Filosofia': [7, 7]}, 'faltas': {'Sociologia': [{'date': '2025-09-23', 'justified': False}]}, 'provas': {}},
        '55667': {'password': generate_password_hash('aluno'), 'nome': 'João Candia', 'turma': '4F', 'notas': {'Educação Física': [9.5, 9], 'Biologia': [6, 6.5]}, 'faltas': {}, 'provas': {'Biologia': ['2025-09-26']}},
        '66778': {'password': generate_password_hash('aluno'), 'nome': 'Ronald Carvalho', 'turma': '3G', 'notas': {'Matemática': [7, 7], 'Português': [7.5, 7.5]}, 'faltas': {'Matemática': [{'date': '2025-09-04', 'justified': False}], 'Português': [{'date': '2025-09-18', 'justified': False}]}, 'provas': {}}
    },
    'pais': {
        'pai_rosonatt': {'password': generate_password_hash('pai'), 'nome': 'Responsável Rosonatt', 'filho_matricula': '202411251'},
        'pai_ryan': {'password': generate_password_hash('pai2'), 'nome': 'Responsável Ryan', 'filho_matricula': '202411281'},
        'pai_bruno': {'password': generate_password_hash('mae'), 'nome': 'Responsável Bruno', 'filho_matricula': '202411333'},
        'mae_natalia': {'password': generate_password_hash('pais'), 'nome': 'Responsável Natalia', 'filho_matricula': '202411325'},
        'pai_kevin': {'password': generate_password_hash('pais2'), 'nome': 'Responsável Kevin', 'filho_matricula': '202411265'},
        'mae_raissa': {'password': generate_password_hash('pais3'), 'nome': 'Responsável Raissa', 'filho_matricula': '202411271'},
        'pai_joao': {'password': generate_password_hash('pais4'), 'nome': 'Responsável João', 'filho_matricula': '55667'},
        'mae_ronald': {'password': generate_password_hash('pais5'), 'nome': 'Responsável Ronald', 'filho_matricula': '66778'},
    },
    'professores': {
        '202411000': {'password': generate_password_hash('prof'), 'nome': 'Lucas', 'disciplinas': ['Matemática', 'Ciências']},
        '202411111': {'password': generate_password_hash('prof'), 'nome': 'André', 'disciplinas': ['Português', 'História']},
        '202411222': {'password': generate_password_hash('prof'), 'nome': 'Diego', 'disciplinas': ['Artes', 'Educação Física']},
        '202411333': {'password': generate_password_hash('prof'), 'nome': 'Gioliano', 'disciplinas': ['Geografia', 'Inglês']}
    },
    'psicopedagogos': {
        'psi_joana': {'password': generate_password_hash('psi'), 'nome': 'Joana'},
        'psi_pedro': {'password': generate_password_hash('psi2'), 'nome': 'Pedro'},
        'coord_educ': {'password': generate_password_hash('coord'), 'nome': 'Coordenadora Maria'},
        'sup_psi': {'password': generate_password_hash('sup'), 'nome': 'Supervisor Antonio'},
    }
}
DENUNCIAS = {}

# --- FUNÇÃO AUXILIAR DE CÁLCULOS (ATUALIZADA) ---
def calcular_dados_aluno(aluno_data):
    # Faltas por Matéria
    faltas_por_materia = {}
    num_justificadas = 0
    num_faltas_total = 0
    
    for materia, faltas_list in aluno_data.get('faltas', {}).items():
        # Conta o total para a matéria
        contagem = len(faltas_list)
        faltas_por_materia[materia] = contagem
        num_faltas_total += contagem
        
        # Conta quantas são justificadas
        for falta in faltas_list:
            if isinstance(falta, dict) and falta.get('justified', False):
                num_justificadas += 1

    # Regra de reprovação (mantida no total de faltas, sem contar justificadas)
    porcentagem_faltas = (num_faltas_total / TOTAL_AULAS_PADRAO) * 100 if TOTAL_AULAS_PADRAO > 0 else 0
    status_faltas = 'REPROVADO POR FALTAS' if num_faltas_total > MAX_FALTAS_PERMITIDAS else 'APROVADO'
    
    materia_mais_faltas = None
    maior_num_faltas = 0
    if faltas_por_materia:
        materia_mais_faltas = max(faltas_por_materia, key=faltas_por_materia.get)
        maior_num_faltas = faltas_por_materia[materia_mais_faltas]

    # ... (Restante do cálculo de notas inalterado)
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
    
    status_geral_notas = 'Reprovado' if materias_reprovadas else 'Aprovado'
    status_final = 'APROVADO'
    if 'REPROVADO' in status_faltas or status_geral_notas == 'Reprovado': 
        status_final = 'REPROVADO'
        
    return {
        'num_faltas': num_faltas_total, 
        'num_justificadas': num_justificadas, # Novo campo
        'faltas_por_materia': faltas_por_materia,
        'porcentagem_faltas': round(porcentagem_faltas, 2),
        'status_faltas': status_faltas, 'medias_materias': medias_materias,
        'materias_reprovadas': materias_reprovadas, 'status_geral_notas': status_geral_notas,
        'status_final_aluno': status_final,
        'materia_mais_faltas': materia_mais_faltas,
        'maior_num_faltas': maior_num_faltas
    }