package com.alunosaqua.service;

import com.alunosaqua.model.Aluno;
import com.alunosaqua.model.DadosCalculadosAluno;
import com.alunosaqua.model.Denuncia;
import com.alunosaqua.model.Usuario;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

// Anotação que indica que esta classe é um serviço Spring
@Service
public class AlunoSaquaService {

    // --- CONFIGURAÇÕES GLOBAIS DE REGRAS (Como no app.py) ---
    public static final int MAX_FALTAS_PERMITIDAS = 8;
    public static final int TOTAL_AULAS_PADRAO = 100;
    public static final double NOTA_MINIMA_APROVACAO_MATERIA = 14.0; // Usar double para consistência

    public static final List<String> MATERIAS_ENSINO_FUNDAMENTAL = Arrays.asList(
            "Português", "Matemática", "História", "Geografia",
            "Ciências", "Artes", "Educação Física", "Inglês"
    );
    // --- FIM DAS CONFIGURAÇÕES ---

    // --- "Banco de Dados" em Memória (Maps estáticos) ---
    private static final Map<String, Aluno> alunos = new HashMap<>();
    private static final Map<String, Usuario> pais = new HashMap<>();
    private static final Map<String, Usuario> professores = new HashMap<>();
    private static final Map<String, Usuario> psicopedagogos = new LinkedHashMap<>(); // LinkedHashMap para manter ordem de inserção
    private static final Map<String, Denuncia> denuncias = new LinkedHashMap<>();

    // Inicialização dos dados de teste (Bloco estático, executado uma vez ao carregar a classe)
    static {
        // Alunos (com todas as matérias padrão inicializadas, mesmo que com notas vazias)
        alunos.put("12345", new Aluno("12345", "aluno", "Rosonatt Ferreira Ramos", "9A", new HashMap<String, List<Double>>() {{
            put("Matemática", Arrays.asList(8.0, 7.0));
            put("Português", Arrays.asList(9.0, 8.0));
            put("História", Arrays.asList(7.0, 7.0));
            put("Geografia", Arrays.asList(0.0,0.0));
            put("Ciências", Arrays.asList(8.0, 9.0));
            put("Artes", Arrays.asList(0.0,0.0));
            put("Educação Física", Arrays.asList(0.0,0.0));
            put("Inglês", Arrays.asList(0.0,0.0));
        }}, 2));
        alunos.put("67890", new Aluno("67890", "aluno", "Ryan Guiwison", "8B", new HashMap<String, List<Double>>() {{
            put("Matemática", Arrays.asList(5.0, 4.0)); // Reprovado em Matemática
            put("Português", Arrays.asList(0.0, 0.0));
            put("História", Arrays.asList(6.0, 7.5));
            put("Geografia", Arrays.asList(0.0, 0.0));
            put("Ciências", Arrays.asList(9.0, 9.5));
            put("Artes", Arrays.asList(0.0, 0.0));
            put("Educação Física", Arrays.asList(0.0, 0.0));
            put("Inglês", Arrays.asList(0.0, 0.0));
        }}, 9)); // Reprovado por falta
        alunos.put("11223", new Aluno("11223", "aluno", "Bruno Alves", "7C", new HashMap<String, List<Double>>() {{
            put("Matemática", Arrays.asList(0.0, 0.0));
            put("Português", Arrays.asList(7.0, 6.5)); // Reprovado em Português
            put("História", Arrays.asList(0.0, 0.0));
            put("Geografia", Arrays.asList(7.5, 9.0));
            put("Ciências", Arrays.asList(0.0, 0.0));
            put("Artes", Arrays.asList(5.0, 4.0)); // Reprovado em Artes
            put("Educação Física", Arrays.asList(0.0, 0.0));
            put("Inglês", Arrays.asList(0.0, 0.0));
        }}, 1));

        alunos.put("22334", new Aluno("22334", "aluno", "Natalia Crys Cardoso", "9A", new HashMap<String, List<Double>>() {{
            MATERIAS_ENSINO_FUNDAMENTAL.forEach(m -> put(m, Arrays.asList(0.0, 0.0))); // Todas padrão com 0
            put("Inglês", Arrays.asList(8.5, 9.0));
            put("Física", Arrays.asList(6.5, 7.5)); // Exemplo de matéria extra
        }}, 0));
        alunos.put("33445", new Aluno("33445", "aluno", "Kevin Paula", "6D", new HashMap<String, List<Double>>() {{
            MATERIAS_ENSINO_FUNDAMENTAL.forEach(m -> put(m, Arrays.asList(0.0, 0.0)));
            put("Química", Arrays.asList(7.0, 7.0));
            put("Literatura", Arrays.asList(8.0, 6.0)); // Exemplo de matéria extra
        }}, 3));
        alunos.put("44556", new Aluno("44556", "aluno", "Raissa Leite", "5E", new HashMap<String, List<Double>>() {{
            MATERIAS_ENSINO_FUNDAMENTAL.forEach(m -> put(m, Arrays.asList(0.0, 0.0)));
            put("Sociologia", Arrays.asList(9.0, 8.5));
            put("Filosofia", Arrays.asList(7.0, 7.0)); // Exemplo de matéria extra
        }}, 1));
        alunos.put("55667", new Aluno("55667", "aluno", "João Candia", "4F", new HashMap<String, List<Double>>() {{
            MATERIAS_ENSINO_FUNDAMENTAL.forEach(m -> put(m, Arrays.asList(0.0, 0.0)));
            put("Educação Física", Arrays.asList(9.5, 9.0));
            put("Biologia", Arrays.asList(6.0, 6.5)); // Reprovado em Biologia (Exemplo de matéria extra)
        }}, 0));
        alunos.put("66778", new Aluno("66778", "aluno", "Ronald Carvalho", "3G", new HashMap<String, List<Double>>() {{
            MATERIAS_ENSINO_FUNDAMENTAL.forEach(m -> put(m, Arrays.asList(0.0, 0.0)));
            put("Matemática", Arrays.asList(7.0, 7.0));
            put("Português", Arrays.asList(7.5, 7.5));
        }}, 2));


        // Pais (AGORA COM CAMPO filhoMatricula no construtor de Usuario)
        pais.put("pai_rosanatt", new Usuario("pai_rosanatt", "pai", "pais", "Pai da Rosonatt", null, "12345"));

        // Professores (AGORA COM CAMPO disciplina no construtor de Usuario)
        professores.put("prof_mat", new Usuario("prof_mat", "prof", "professor", "Prof. de Matemática", "Matemática", null));
        psicopedagogos.put("psi_joana", new Usuario("psi_joana", "psi", "psicopedagogo", "Joana Psicopedagoga", null, null));


        // Novos Logins
        professores.put("prof_port", new Usuario("prof_port", "prof2", "professor", "Prof. de Português", "Português", null));
        professores.put("prof_hist", new Usuario("prof_hist", "prof3", "professor", "Prof. de História", "História", null));
        professores.put("prof_cienc", new Usuario("prof_cienc", "prof4", "professor", "Prof. de Ciências", "Ciências", null));
        professores.put("prof_edfis", new Usuario("prof_edfis", "prof5", "professor", "Prof. de Educação Física", "Educação Física", null));
        professores.put("prof_geo", new Usuario("prof_geo", "prof6", "professor", "Prof. de Geografia", "Geografia", null));
        professores.put("prof_artes", new Usuario("prof_artes", "prof7", "professor", "Prof. de Artes", "Artes", null));
        professores.put("prof_ingles", new Usuario("prof_ingles", "prof8", "professor", "Prof. de Inglês", "Inglês", null));


        pais.put("pai_ryan", new Usuario("pai_ryan", "pai2", "pais", "Pai do Ryan", null, "67890"));
        pais.put("pai_bruno", new Usuario("pai_bruno", "mae", "pais", "Pai do Bruno", null, "11223"));
        pais.put("mae_natalia", new Usuario("mae_natalia", "pais", "pais", "Mãe da Natalia", null, "22334"));
        pais.put("pai_kevin", new Usuario("pai_kevin", "pais2", "pais", "Pai do Kevin", null, "33445"));
        pais.put("mae_raissa", new Usuario("mae_raissa", "pais3", "pais", "Mãe da Raissa", null, "44556"));
        pais.put("pai_joao", new Usuario("pai_joao", "pais4", "pais", "Pai do João", null, "55667"));
        pais.put("mae_ronald", new Usuario("mae_ronald", "pais5", "pais", "Mãe do Ronald", null, "66778"));


        psicopedagogos.put("psi_pedro", new Usuario("psi_pedro", "psi2", "psicopedagogo", "Pedro Psicopedagogo", null, null));
        psicopedagogos.put("coord_educ", new Usuario("coord_educ", "coord", "psicopedagogo", "Coordenador de Educação", null, null));
        psicopedagogos.put("sup_psi", new Usuario("sup_psi", "sup", "psicopedagogo", "Supervisor Psicopedagogo", null, null));


        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "12345", "Rosonatt está sendo excluído nos trabalhos em grupo.", "média", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "67890", "Ryan foi alvo de piadas sobre sua aparência na aula de educação física.", "alta", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "11223", "Bruno tem sido ignorado pelos colegas durante o recreio.", "baixa", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "22334", "Natalia recebeu mensagens ofensivas em um grupo de chat da turma.", "alta", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "33445", "Kevin se queixou de objetos escondidos em sua mochila por colegas.", "média", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "44556", "Raissa está sendo constantemente interrompida e desacreditada nas apresentações.", "baixa", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "55667", "João teve seus materiais escolares danificados no armário.", "alta", "aberta", null));
        denuncias.put(UUID.randomUUID().toString(), new Denuncia(UUID.randomUUID().toString(), "66778", "Ronald tem sido alvo de apelidos pejorativos por parte de um grupo de alunos.", "média", "aberta", null));
    }
    // --- FIM DOS DADOS DE TESTE ---

    // --- Métodos de Autenticação e Usuário ---

    public String checkLogin(String userType, String username, String password) {
        switch (userType) {
            case "aluno":
                if (alunos.containsKey(username) && alunos.get(username).getPassword().equals(password)) {
                    return "aluno";
                }
                break;
            case "pais":
                if (pais.containsKey(username) && pais.get(username).getPassword().equals(password)) {
                    return "pais";
                }
                break;
            case "professor":
                if (professores.containsKey(username) && professores.get(username).getPassword().equals(password)) {
                    return "professor";
                }
                break;
            case "psicopedagogo":
                if (psicopedagogos.containsKey(username) && psicopedagogos.get(username).getPassword().equals(password)) {
                    return "psicopedagogo";
                }
                break;
        }
        return null; // Login falhou
    }

    public boolean registerAluno(String matricula, String password, String nome, String turma) {
        if (alunos.containsKey(matricula)) {
            return false; // Matrícula já existe
        }
        Map<String, List<Double>> initialNotas = new HashMap<>();
        MATERIAS_ENSINO_FUNDAMENTAL.forEach(materia -> initialNotas.put(materia, new ArrayList<>()));
        alunos.put(matricula, new Aluno(matricula, password, nome, turma, initialNotas, 0));
        return true;
    }

    // --- Métodos para Alunos ---
    public Aluno getAlunoByMatricula(String matricula) {
        return alunos.get(matricula);
    }

    // --- Métodos para Pais ---
    public Usuario getPaiByUsername(String username) {
        return pais.get(username);
    }

    // Método auxiliar para obter a matrícula do filho a partir do pai
    public String getFilhoMatriculaByPaiUsername(String paiUsername) {
        Usuario pai = pais.get(paiUsername);
        return (pai != null) ? pai.getFilhoMatricula() : null;
    }


    // --- Métodos para Professores ---
    public Usuario getProfessorByUsername(String username) {
        return professores.get(username);
    }

    public Map<String, Aluno> getAllAlunos() {
        return alunos;
    }

    // Atualizar dados de aluno por professor
    public void updateAlunoData(String matricula, int faltas, String disciplinaProfessor,
                                Double nota1, Double nota2, String novaDisciplinaNome,
                                Double novaDisciplinaNota1, Double novaDisciplinaNota2) {
        Aluno aluno = alunos.get(matricula);
        if (aluno == null) return;

        aluno.setFaltas(faltas);

        if (disciplinaProfessor != null && !disciplinaProfessor.isEmpty()) {
            // Professor com disciplina específica, só atualiza a dele
            // Garante que a disciplina do professor exista para o aluno.
            // Se o aluno ainda não tem essa disciplina, ela é criada com as notas fornecidas.
            if (!aluno.getNotas().containsKey(disciplinaProfessor)) {
                aluno.getNotas().put(disciplinaProfessor, new ArrayList<>()); // Inicializa se não existir
            }
            if (nota1 != null && nota2 != null) {
                aluno.getNotas().put(disciplinaProfessor, Arrays.asList(nota1, nota2));
            } else {
                // Se as notas foram limpas no formulário, limpa no modelo também
                aluno.getNotas().put(disciplinaProfessor, new ArrayList<>());
            }
        } else {
            // Professor geral, atualiza todas as notas que vierem do formulário (precisa ser tratado no Controller)
            // A lógica de processamento do formulário para professor geral está no Controller.
            // Aqui no Service, apenas se passar o nome da disciplina e as duas notas, atualiza.
            // Para simplificar, esta parte específica para "professor geral" é mais complexa via argumentos.
            // O Controller vai chamar Aluno.setNotas() diretamente para o caso geral.
        }

        // Adicionar nova disciplina (se for o caso e não existir)
        if (novaDisciplinaNome != null && !novaDisciplinaNome.isEmpty() &&
                !aluno.getNotas().containsKey(novaDisciplinaNome)) {
            if (novaDisciplinaNota1 != null && novaDisciplinaNota2 != null) {
                aluno.getNotas().put(novaDisciplinaNome, Arrays.asList(novaDisciplinaNota1, novaDisciplinaNota2));
            } else {
                // Inicializa a nova disciplina com notas vazias se as notas não foram fornecidas no momento da adição
                aluno.getNotas().put(novaDisciplinaNome, new ArrayList<>());
            }
        }
    }

    // --- Métodos para Psicopedagogos e Denúncias ---
    public Map<String, Denuncia> getAllDenuncias() {
        return denuncias;
    }

    public Denuncia getDenunciaById(String id) {
        return denuncias.get(id);
    }

    public void addDenuncia(String alunoMatricula, String descricao, String urgencia) {
        String id = UUID.randomUUID().toString();
        String alunoNome = alunos.containsKey(alunoMatricula) ? alunos.get(alunoMatricula).getNome() : "Aluno Desconhecido";
        denuncias.put(id, new Denuncia(id, alunoMatricula, descricao, urgencia, "aberta", alunoNome));
    }

    public void updateDenunciaStatus(String id, String status) {
        Denuncia denuncia = denuncias.get(id);
        if (denuncia != null) {
            denuncia.setStatus(status);
        }
    }

    // --- Lógica de Cálculo de Dados do Aluno (Replicado do Python) ---
    public DadosCalculadosAluno calcularDadosAluno(Aluno aluno) {
        // Cálculo de faltas
        double porcentagemFaltas = (aluno.getFaltas() / (double) TOTAL_AULAS_PADRAO) * 100;
        String statusFaltas = aluno.getFaltas() > MAX_FALTAS_PERMITIDAS ? "REPROVADO POR FALTAS" : "APROVADO POR FALTAS";

        // Dados para gráfico de faltas (presente/ausente)
        DadosCalculadosAluno.GraficoData faltasGrafico = new DadosCalculadosAluno.GraficoData(0.0, porcentagemFaltas, 100 - porcentagemFaltas, porcentagemFaltas);

        // Cálculo de notas por matéria e status
        Map<String, DadosCalculadosAluno.MateriaInfo> mediasMaterias = new HashMap<>();
        List<String> materiasReprovadas = new ArrayList<>();
        int totalDisciplinasComNotas = 0;
        int disciplinasAprovadasCount = 0;

        for (Map.Entry<String, List<Double>> entry : aluno.getNotas().entrySet()) {
            String disciplina = entry.getKey();
            List<Double> notasList = entry.getValue();

            if (notasList != null && notasList.size() == 2) {
                totalDisciplinasComNotas++;
                double somaNotas = notasList.get(0) + notasList.get(1);
                String statusMateria = somaNotas >= NOTA_MINIMA_APROVACAO_MATERIA ? "APROVADO" : "REPROVADO";

                mediasMaterias.put(disciplina, new DadosCalculadosAluno.MateriaInfo(disciplina, notasList.get(0), notasList.get(1), somaNotas, statusMateria));
                if ("REPROVADO".equals(statusMateria)) {
                    materiasReprovadas.add(disciplina);
                } else {
                    disciplinasAprovadasCount++;
                }
            } else if (notasList != null && notasList.size() < 2) {
                totalDisciplinasComNotas++;
                mediasMaterias.put(disciplina, new DadosCalculadosAluno.MateriaInfo(disciplina, notasList.size() > 0 ? notasList.get(0) : "N/A", "N/A", "N/A", "FALTAM NOTAS"));
                materiasReprovadas.add(disciplina);
            } else {
                totalDisciplinasComNotas++;
                mediasMaterias.put(disciplina, new DadosCalculadosAluno.MateriaInfo(disciplina, "N/A", "N/A", "N/A", "ERRO NO FORMATO"));
                materiasReprovadas.add(disciplina);
            }
        }

        String statusGeralNotas = materiasReprovadas.isEmpty() ? "APROVADO POR NOTA" : "REPROVADO POR NOTA";

        double aprovadasPercent = (totalDisciplinasComNotas > 0) ? ((double) disciplinasAprovadasCount / totalDisciplinasComNotas) * 100 : 0.0;
        double reprovadasPercent = (totalDisciplinasComNotas > 0) ? ((double) materiasReprovadas.size() / totalDisciplinasComNotas) * 100 : 0.0;

        DadosCalculadosAluno.GraficoData notasGrafico = new DadosCalculadosAluno.GraficoData(reprovadasPercent, aprovadasPercent, 0.0, 0.0);

        String statusFinal;
        if ("REPROVADO POR FALTAS".equals(statusFaltas) && "REPROVADO POR NOTA".equals(statusGeralNotas)) {
            statusFinal = "REPROVADO (Faltas e Notas)";
        } else if ("REPROVADO POR FALTAS".equals(statusFaltas)) {
            statusFinal = "REPROVADO (Faltas)";
        } else if ("REPROVADO POR NOTA".equals(statusGeralNotas)) {
            statusFinal = "REPROVADO (Notas)";
        } else {
            statusFinal = "APROVADO";
        }

        return new DadosCalculadosAluno(
                porcentagemFaltas, statusFaltas, statusFinal, mediasMaterias,
                materiasReprovadas, statusGeralNotas, faltasGrafico, notasGrafico
        );
    }
}