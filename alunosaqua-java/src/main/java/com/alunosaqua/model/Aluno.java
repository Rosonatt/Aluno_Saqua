package com.alunosaqua.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Aluno {
    private String matricula;
    private String password;
    private String nome;
    private String turma;
    private Map<String, List<Double>> notas; // Map<Disciplina, List<Nota1, Nota2>>
    private int faltas;
}