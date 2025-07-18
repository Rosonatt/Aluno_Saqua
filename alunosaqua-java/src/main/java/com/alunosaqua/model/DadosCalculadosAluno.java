package com.alunosaqua.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DadosCalculadosAluno {
    private double porcentagemFaltas;
    private String statusFaltas;
    private String statusFinalAluno;
    private Map<String, MateriaInfo> mediasMaterias; // Map<Disciplina, MateriaInfo>
    private List<String> materiasReprovadas;
    private String statusGeralNotas;
    private GraficoData faltasGrafico; // Dados para o gráfico de faltas
    private GraficoData notasGrafico;  // Dados para o gráfico de notas

    // Classe interna para informações de matéria
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MateriaInfo {
        private String disciplina;
        private Object nota1; // Usar Object para permitir "N/A" ou Double
        private Object nota2;
        private Object soma;
        private String status;
    }

    // Classe interna para dados de gráfico (presente/ausente ou aprovadas/reprovadas)
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class GraficoData {
        private double reprovadas;
        private double aprovadas;
        private double presente;
        private double ausente;
    }
}