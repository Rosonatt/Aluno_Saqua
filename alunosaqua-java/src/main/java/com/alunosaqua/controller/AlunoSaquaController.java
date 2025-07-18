package com.alunosaqua.controller;

import com.alunosaqua.model.Aluno;
import com.alunosaqua.model.DadosCalculadosAluno;
import com.alunosaqua.model.Denuncia;
import com.alunosaqua.model.Usuario;
import com.alunosaqua.service.AlunoSaquaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import jakarta.servlet.http.HttpSession;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/")
public class AlunoSaquaController {

    @Autowired
    private AlunoSaquaService service;

    // Constantes para passar para os templates
    private void addConfigToModel(Model model) {
        model.addAttribute("MAX_FALTAS_PERMITIDAS", AlunoSaquaService.MAX_FALTAS_PERMITIDAS);
        model.addAttribute("TOTAL_AULAS_PADRAO", AlunoSaquaService.TOTAL_AULAS_PADRAO);
        model.addAttribute("NOTA_MINIMA_APROVACAO_MATERIA", AlunoSaquaService.NOTA_MINIMA_APROVACAO_MATERIA);
        model.addAttribute("MATERIAS_ENSINO_FUNDAMENTAL", AlunoSaquaService.MATERIAS_ENSINO_FUNDAMENTAL);
    }

    // --- Rotas Comuns ---
    @GetMapping("/")
    public String index() {
        return "index";
    }

    @GetMapping("/login")
    public String showLoginForm() {
        return "login";
    }

    @PostMapping("/login")
    public String processLogin(@RequestParam String user_type,
                               @RequestParam String username,
                               @RequestParam String password,
                               HttpSession session,
                               RedirectAttributes redirectAttributes) {
        String loginResult = service.checkLogin(user_type, username, password);

        if (loginResult != null) {
            session.setAttribute("userType", user_type);
            session.setAttribute("username", username);
            redirectAttributes.addFlashAttribute("message", "Login de " + user_type + " realizado com sucesso!");
            redirectAttributes.addFlashAttribute("messageType", "success");

            switch (user_type) {
                case "aluno":
                    return "redirect:/aluno/dashboard";
                case "pais":
                    return "redirect:/pais/dashboard";
                case "professor":
                    return "redirect:/professor/dashboard";
                case "psicopedagogo":
                    return "redirect:/psicopedagogo/dashboard";
            }
        }

        redirectAttributes.addFlashAttribute("message", "Usuário ou senha incorretos. Tente novamente.");
        redirectAttributes.addFlashAttribute("messageType", "danger");
        return "redirect:/login";
    }

    @GetMapping("/register")
    public String showRegisterForm() {
        return "register";
    }

    @PostMapping("/register")
    public String processRegister(@RequestParam String matricula,
                                  @RequestParam String password,
                                  @RequestParam String nome,
                                  RedirectAttributes redirectAttributes) {
        String turma = "Turma Padrão"; // Alunos novos tem turma padrão, pode ser ajustado depois
        boolean registered = service.registerAluno(matricula, password, nome, turma);

        if (registered) {
            redirectAttributes.addFlashAttribute("message", "Cadastro de aluno realizado com sucesso! Faça login.");
            redirectAttributes.addFlashAttribute("messageType", "success");
            return "redirect:/login";
        } else {
            redirectAttributes.addFlashAttribute("message", "Matrícula já cadastrada. Por favor, faça login.");
            redirectAttributes.addFlashAttribute("messageType", "warning");
            return "redirect:/register";
        }
    }

    @GetMapping("/logout")
    public String logout(HttpSession session, RedirectAttributes redirectAttributes) {
        session.invalidate();
        redirectAttributes.addFlashAttribute("message", "Você foi desconectado.");
        redirectAttributes.addFlashAttribute("messageType", "info");
        return "redirect:/";
    }

    // --- Rotas de Dashboard (Verificação de sessão replicada) ---

    private String checkAuth(HttpSession session, RedirectAttributes redirectAttributes, String expectedType) {
        if (session.getAttribute("userType") == null || !session.getAttribute("userType").equals(expectedType)) {
            redirectAttributes.addFlashAttribute("message", "Acesso não autorizado.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            return "redirect:/login";
        }
        return null;
    }

    @GetMapping("/aluno/dashboard")
    public String alunoDashboard(HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "aluno");
        if (authCheck != null) return authCheck;

        String matricula = (String) session.getAttribute("username");
        Aluno aluno = service.getAlunoByMatricula(matricula);
        if (aluno == null) {
            redirectAttributes.addFlashAttribute("message", "Dados do aluno não encontrados.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            session.invalidate();
            return "redirect:/login";
        }

        DadosCalculadosAluno dadosCalculados = service.calcularDadosAluno(aluno);
        model.addAttribute("aluno", aluno);
        model.addAttribute("dadosCalculados", dadosCalculados);
        addConfigToModel(model);
        return "aluno_dashboard";
    }

    @GetMapping("/aluno/denunciar")
    public String showDenunciarForm(HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "aluno");
        if (authCheck != null) return authCheck;
        return "aluno_denunciar";
    }

    @PostMapping("/aluno/denunciar")
    public String processDenuncia(@RequestParam String descricao,
                                  @RequestParam String urgencia,
                                  HttpSession session,
                                  RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "aluno");
        if (authCheck != null) return authCheck;

        String alunoMatricula = (String) session.getAttribute("username");
        service.addDenuncia(alunoMatricula, descricao, urgencia);
        redirectAttributes.addFlashAttribute("message", "Denúncia enviada com sucesso! Ela é anônima para a equipe de psicopedagogia.");
        redirectAttributes.addFlashAttribute("messageType", "success");
        return "redirect:/aluno/dashboard";
    }

    @GetMapping("/pais/dashboard")
    public String paisDashboard(HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "pais");
        if (authCheck != null) return authCheck;

        String paiUsername = (String) session.getAttribute("username");
        String filhoMatricula = service.getFilhoMatriculaByPaiUsername(paiUsername);

        if (filhoMatricula == null || filhoMatricula.isEmpty()) {
            redirectAttributes.addFlashAttribute("message", "Filho não associado a esta conta de pais.");
            redirectAttributes.addFlashAttribute("messageType", "warning");
            return "redirect:/login";
        }

        Aluno filho = service.getAlunoByMatricula(filhoMatricula);
        if (filho == null) {
            redirectAttributes.addFlashAttribute("message", "Dados do filho não encontrados. Verifique a associação.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            session.invalidate();
            return "redirect:/login";
        }

        DadosCalculadosAluno dadosCalculadosFilho = service.calcularDadosAluno(filho);
        model.addAttribute("filho", filho);
        model.addAttribute("dadosCalculados", dadosCalculadosFilho);
        addConfigToModel(model);
        return "pais_dashboard";
    }

    @GetMapping("/professor/dashboard")
    public String professorDashboard(HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "professor");
        if (authCheck != null) return authCheck;

        String professorUsername = (String) session.getAttribute("username");
        Usuario professor = service.getProfessorByUsername(professorUsername);
        String disciplinaProfessor = (professor != null) ? professor.getDisciplina() : null;

        Map<String, Aluno> allAlunos = service.getAllAlunos();
        List<Map<String, Object>> alunosParaProfessorTabela = new ArrayList<>();

        for (Aluno aluno : allAlunos.values()) {
            if (disciplinaProfessor == null || aluno.getNotas().containsKey(disciplinaProfessor)) {
                DadosCalculadosAluno dadosCalculados = service.calcularDadosAluno(aluno);
                Map<String, Object> alunoMap = new HashMap<>();
                alunoMap.put("matricula_aluno", aluno.getMatricula());
                alunoMap.put("nome", aluno.getNome());
                alunoMap.put("turma", aluno.getTurma());
                alunoMap.put("faltas", aluno.getFaltas());
                alunoMap.put("porcentagem_faltas", dadosCalculados.getPorcentagemFaltas());
                alunoMap.put("status_faltas", dadosCalculados.getStatusFaltas());
                alunoMap.put("status_geral_notas", dadosCalculados.getStatusGeralNotas());
                alunoMap.put("status_final_aluno", dadosCalculados.getStatusFinalAluno());

                if (disciplinaProfessor != null) {
                    DadosCalculadosAluno.MateriaInfo infoDisciplinaProf = dadosCalculados.getMediasMaterias().get(disciplinaProfessor);
                    alunoMap.put("nota_disciplina_professor_soma", infoDisciplinaProf != null ? infoDisciplinaProf.getSoma() : "N/A");
                    alunoMap.put("status_disciplina_professor", infoDisciplinaProf != null ? infoDisciplinaProf.getStatus() : "N/A");
                }
                alunosParaProfessorTabela.add(alunoMap);
            }
        }

        // CORREÇÃO AQUI: Usar lambda expressions para o Comparator
        alunosParaProfessorTabela.sort(Comparator
                .comparing((Map<String, Object> a) -> (String) a.getOrDefault("turma", ""))
                .thenComparing((Map<String, Object> a) -> (String) a.getOrDefault("nome", ""))
        );

        model.addAttribute("alunos", alunosParaProfessorTabela);
        model.addAttribute("disciplinaProfessor", disciplinaProfessor);
        addConfigToModel(model);
        return "professor_dashboard";
    }

    @GetMapping("/professor/atualizar_dados/{matricula}")
    public String showUpdateAlunoForm(@PathVariable String matricula, HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "professor");
        if (authCheck != null) return authCheck;

        Aluno aluno = service.getAlunoByMatricula(matricula);
        if (aluno == null) {
            redirectAttributes.addFlashAttribute("message", "Aluno não encontrado.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            return "redirect:/professor/dashboard";
        }

        Usuario professor = service.getProfessorByUsername((String) session.getAttribute("username"));
        String disciplinaProfessor = (professor != null) ? professor.getDisciplina() : null;

        model.addAttribute("aluno", aluno);
        model.addAttribute("disciplinaProfessor", disciplinaProfessor);
        addConfigToModel(model);
        return "professor_atualizar_dados";
    }

    @PostMapping("/professor/atualizar_dados/{matricula}")
    public String processUpdateAluno(@PathVariable String matricula,
                                     @RequestParam int faltas,
                                     @RequestParam Map<String, String> allRequestParams,
                                     HttpSession session,
                                     RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "professor");
        if (authCheck != null) return authCheck;

        Usuario professor = service.getProfessorByUsername((String) session.getAttribute("username"));
        String disciplinaProfessor = (professor != null) ? professor.getDisciplina() : null;

        Aluno aluno = service.getAlunoByMatricula(matricula);
        if (aluno == null) {
            redirectAttributes.addFlashAttribute("message", "Aluno não encontrado.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            return "redirect:/professor/dashboard";
        }

        aluno.setFaltas(faltas);

        if (disciplinaProfessor != null) {
            String nota1_str = allRequestParams.get("nota_" + disciplinaProfessor + "_1");
            String nota2_str = allRequestParams.get("nota_" + disciplinaProfessor + "_2");

            if (nota1_str != null && nota2_str != null && !nota1_str.isEmpty() && !nota2_str.isEmpty()) {
                try {
                    Double n1 = Double.parseDouble(nota1_str);
                    Double n2 = Double.parseDouble(nota2_str);
                    aluno.getNotas().put(disciplinaProfessor, Arrays.asList(n1, n2));
                    redirectAttributes.addFlashAttribute("message", "Notas de " + disciplinaProfessor + " para " + aluno.getNome() + " atualizadas com sucesso!");
                    redirectAttributes.addFlashAttribute("messageType", "success");
                } catch (NumberFormatException e) {
                    redirectAttributes.addFlashAttribute("message", "Notas inválidas para " + disciplinaProfessor + ". Certifique-se de que são números.");
                    redirectAttributes.addFlashAttribute("messageType", "warning");
                }
            } else if (aluno.getNotas().containsKey(disciplinaProfessor)) {
                aluno.getNotas().put(disciplinaProfessor, new ArrayList<>());
            }
        } else { // Professor geral
            for (String materia : AlunoSaquaService.MATERIAS_ENSINO_FUNDAMENTAL) {
                String nota1_str = allRequestParams.get("nota_" + materia + "_1");
                String nota2_str = allRequestParams.get("nota_" + materia + "_2");

                if (nota1_str != null && nota2_str != null && !nota1_str.isEmpty() && !nota2_str.isEmpty()) {
                    try {
                        Double n1 = Double.parseDouble(nota1_str);
                        Double n2 = Double.parseDouble(nota2_str);
                        aluno.getNotas().put(materia, Arrays.asList(n1, n2));
                    } catch (NumberFormatException e) {
                        redirectAttributes.addFlashAttribute("message", "Notas inválidas para " + materia + ".");
                        redirectAttributes.addFlashAttribute("messageType", "warning");
                    }
                } else if (aluno.getNotas().containsKey(materia)) {
                    aluno.getNotas().put(materia, new ArrayList<>());
                }
            }
            for (Map.Entry<String, List<Double>> entry : new HashMap<>(aluno.getNotas()).entrySet()) {
                String disciplina = entry.getKey();
                if (!AlunoSaquaService.MATERIAS_ENSINO_FUNDAMENTAL.contains(disciplina)) {
                    String nota1_str = allRequestParams.get("nota_" + disciplina + "_1");
                    String nota2_str = allRequestParams.get("nota_" + disciplina + "_2");
                    if (nota1_str != null && nota2_str != null && !nota1_str.isEmpty() && !nota2_str.isEmpty()) {
                        try {
                            Double n1 = Double.parseDouble(nota1_str);
                            Double n2 = Double.parseDouble(nota2_str);
                            aluno.getNotas().put(disciplina, Arrays.asList(n1, n2));
                        } catch (NumberFormatException e) {
                            redirectAttributes.addFlashAttribute("message", "Notas inválidas para " + disciplina + " (Extra).");
                            redirectAttributes.addFlashAttribute("messageType", "warning");
                        }
                    } else if (aluno.getNotas().containsKey(disciplina)) {
                        aluno.getNotas().put(disciplina, new ArrayList<>());
                    }
                }
            }

            redirectAttributes.addFlashAttribute("message", "Dados do aluno " + aluno.getNome() + " atualizados com sucesso!");
            redirectAttributes.addFlashAttribute("messageType", "success");
        }

        String nova_disciplina_nome = allRequestParams.get("nova_disciplina_nome");
        String nova_disciplina_nota1_str = allRequestParams.get("nova_disciplina_nota1");
        String nova_disciplina_nota2_str = allRequestParams.get("nova_disciplina_nota2");

        if (nova_disciplina_nome != null && !nova_disciplina_nome.isEmpty()) {
            if (!aluno.getNotas().containsKey(nova_disciplina_nome)) {
                if (nova_disciplina_nota1_str != null && !nova_disciplina_nota1_str.isEmpty() &&
                        nova_disciplina_nota2_str != null && !nova_disciplina_nota2_str.isEmpty()) {
                    try {
                        Double nova_n1 = Double.parseDouble(nova_disciplina_nota1_str);
                        Double nova_n2 = Double.parseDouble(nova_disciplina_nota2_str);
                        aluno.getNotas().put(nova_disciplina_nome, Arrays.asList(nova_n1, nova_n2));
                        redirectAttributes.addFlashAttribute("message", "Disciplina '" + nova_disciplina_nome + "' adicionada.");
                        redirectAttributes.addFlashAttribute("messageType", "success");
                    } catch (NumberFormatException e) {
                        redirectAttributes.addFlashAttribute("message", "Notas da nova disciplina devem ser números.");
                        redirectAttributes.addFlashAttribute("messageType", "warning");
                    }
                } else {
                    redirectAttributes.addFlashAttribute("message", "Por favor, insira as duas notas para a nova disciplina.");
                    redirectAttributes.addFlashAttribute("messageType", "warning");
                }
            } else {
                redirectAttributes.addFlashAttribute("message", "Disciplina '" + nova_disciplina_nome + "' já existe.");
                redirectAttributes.addFlashAttribute("messageType", "info");
            }
        }

        return "redirect:/professor/dashboard";
    }

    @GetMapping("/psicopedagogo/dashboard")
    public String psicopedagogoDashboard(HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "psicopedagogo");
        if (authCheck != null) return authCheck;

        Map<String, Denuncia> allDenuncias = service.getAllDenuncias();
        List<Denuncia> denunciasAbertas = allDenuncias.values().stream()
                .filter(d -> "aberta".equals(d.getStatus()))
                .collect(Collectors.toList());

        Map<String, List<Denuncia>> denunciasUrgencia = new LinkedHashMap<>();
        denunciasUrgencia.put("alta", new ArrayList<>());
        denunciasUrgencia.put("média", new ArrayList<>());
        denunciasUrgencia.put("baixa", new ArrayList<>());

        for (Denuncia denuncia : denunciasAbertas) {
            Aluno aluno = service.getAlunoByMatricula(denuncia.getAlunoMatricula());
            if (aluno != null) {
                denuncia.setAlunoNome(aluno.getNome());
            } else {
                denuncia.setAlunoNome("Aluno Desconhecido");
            }

            denunciasUrgencia.get(denuncia.getUrgencia()).add(denuncia);
        }

        model.addAttribute("denuncias", denunciasUrgencia);
        addConfigToModel(model);
        return "psicopedagogo_dashboard";
    }

    @GetMapping("/psicopedagogo/denuncia/{denunciaId}")
    public String denunciaDetalhe(@PathVariable String denunciaId, HttpSession session, Model model, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "psicopedagogo");
        if (authCheck != null) return authCheck;

        Denuncia denuncia = service.getDenunciaById(denunciaId);
        if (denuncia == null) {
            redirectAttributes.addFlashAttribute("message", "Denúncia não encontrada.");
            redirectAttributes.addFlashAttribute("messageType", "danger");
            return "redirect:/psicopedagogo/dashboard";
        }

        Aluno aluno = service.getAlunoByMatricula(denuncia.getAlunoMatricula());
        DadosCalculadosAluno dadosCalculadosAluno = null;
        if (aluno != null) {
            denuncia.setAlunoNome(aluno.getNome());
            dadosCalculadosAluno = service.calcularDadosAluno(aluno);
        } else {
            denuncia.setAlunoNome("Aluno Desconhecido");
        }

        model.addAttribute("denuncia", denuncia);
        model.addAttribute("alunoNome", denuncia.getAlunoNome());
        model.addAttribute("alunoNotasCalculadas", dadosCalculadosAluno != null ? dadosCalculadosAluno.getMediasMaterias() : Collections.emptyMap());
        addConfigToModel(model);
        return "denuncia_detalhe";
    }

    @PostMapping("/psicopedagogo/fechar_denuncia/{denunciaId}")
    public String fecharDenuncia(@PathVariable String denunciaId, HttpSession session, RedirectAttributes redirectAttributes) {
        String authCheck = checkAuth(session, redirectAttributes, "psicopedagogo");
        if (authCheck != null) return authCheck;

        service.updateDenunciaStatus(denunciaId, "fechada");
        redirectAttributes.addFlashAttribute("message", "Denúncia marcada como fechada.");
        redirectAttributes.addFlashAttribute("messageType", "success");
        return "redirect:/psicopedagogo/dashboard";
    }
}