package com.alunosaqua.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Denuncia {
    private String id;
    private String alunoMatricula;
    private String descricao;
    private String urgencia; // Ex: "baixa", "média", "alta"
    private String status;   // Ex: "aberta", "fechada"
    private String alunoNome; // Adicionado para facilitar a exibição no dashboard do psicopedagogo
}