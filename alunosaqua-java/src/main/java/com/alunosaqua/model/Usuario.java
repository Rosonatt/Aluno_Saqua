package com.alunosaqua.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data // Gera getters, setters, toString, equals e hashCode
@NoArgsConstructor // Gera construtor sem argumentos
@AllArgsConstructor // Gera construtor com todos os argumentos
public class Usuario {
    private String username;
    private String password;
    private String userType; // Ex: "aluno", "pais", "professor", "psicopedagogo"
    private String nome; // Nome completo do usuário
    private String disciplina; // Campo para professores (disciplina que leciona)
    private String filhoMatricula; // Campo para pais (matrícula do filho associado)
}