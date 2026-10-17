# 1. Documento de Visão
|---|---|---|
## Identificação
| Campo                 | Informação                                                        |
| Projeto               | Sistema de Folha de Pagamento                                     |
| Equipe                | João Vitor Fraga, Pedro Kolling, Yuri Soares e Luiggi Bortolini   |
| Data                  | 17/10/2026                                                        |
| Versão                | 1.0 (entrega A1)                                                  |
| Unidade Curricular    | Garantia da Qualidade de Software                                 |

## Objetivo
Desenvolver um sistema web que permita cadastrar colaboradores de diferentes categorias de remuneração
(padrão, comissionado e por produção), calcular automaticamente o salário de cada um, gerar a folha de
pagamento mensal individual e consolidada e apresentar o custo total da folha, com controle de acesso por perfil
e histórico preservado.

## Escopo
- Cadastro, consulta, alteração e desabilitação (exclusão lógica) de colaboradores.
- Três formas de remuneração: Padrão, Comissionado e Por Produção, com metas mensais progressivas.
- Lançamento mensal de vendas e produção, cálculo automático e geração da folha por mês.
- Fechamento do mês (folha congelada), recibo individual imprimível e relatório consolidado/resumido.
- Autenticação e três níveis de acesso: 1 Administrador/RH, 2 Financeiro, 3 Colaborador.

## Premissas
- A empresa fecha a folha uma vez por mês.
- O responsável pelo projeto (cliente) define as regras de negócio; a equipe cuida da análise, projeto, implementação e qualidade.
- O sistema roda em um computador com Python 3.10+ e navegador; o uso inicial é de uma única empresa.
- Vendas e produção são informadas pelo RH apenas pelo **total do mês** (sem registro de cancelamento/devolução individual).

## Restrições
- Prazos: A1 em 20/10/2026.
- Tecnologias: Python/Flask e SQLite (sem servidor de banco), mantendo a linguagem do sistema original.
- Dinheiro em reais, valores nunca negativos, sem descontos.
- Uma folha por colaborador por mês; folha fechada não pode ser reaberta.

## Benefícios Esperados
- Eliminar cálculo manual e erros de arredondamento (valores em centavos).
- Histórico confiável: cada mês guarda os valores e as metas daquele momento.
- Privacidade: cada colaborador vê somente a própria folha; Financeiro apenas consulta.
- Instalação simples (dois cliques) e baixo custo de manutenção.

## Stakeholders
| Stakeholder | Papel | Interesse |
|---|---|---|
| Cliente / responsável pelo projeto | Define regras de negócio e homologa | Sistema aderente aos requisitos |
| Administrador/RH (nível 1) | Usuário  | Cadastrar, lançar, gerar e fechar a folha |
| Financeiro (nível 2) | Usuário | Consultar folhas e relatórios, conhecer o custo total |
| Colaborador (nível 3) | Usuário | Consultar o próprio recibo e metas |
| Equipe de desenvolvimento e qualidade | Equipe  | Entregar com qualidade e evidências |
| Professor da unidade curricular | Avaliador | Verificar a aplicação das práticas de GQS |
