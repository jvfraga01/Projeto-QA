
# 5.8 Planejamento do Projeto

## EAP (Estrutura Analítica do Projeto)
```mermaid
flowchart TD
    P["1 Projeto Folha de Pagamento"] --> G["1.1 Gerência"]
    P --> A["1.2 Análise e Projeto"]
    P --> D["1.3 Desenvolvimento"]
    P --> Q["1.4 Qualidade e Testes"]
    P --> M["1.5 Documentação"]
    P --> H["1.6 Homologação e Entrega"]
    G --> G1["Planejamento e cronograma"]
    G --> G2["Reuniões e controle de versão"]
    A --> A1["Visão e ERS"]
    A --> A1["Casos de uso e UML"]
    A --> A3["Arquitetura e modelo de dados"]
    D --> D1["Autenticação e permissões"]
    D --> D2["Cadastro de colaboradores"]
    D --> D3["Cálculo e metas"]
    D --> D4["Folha, fechamento e relatórios"]
    Q --> Q1["PGQ e Plano de Testes"]
    Q --> Q2["Casos de teste"]
    Q --> Q3["Testes unitários, integração e aceitação"]
    Q --> Q4["Defeitos e métricas"]
    M --> M1["Manual do usuário"]
    M --> M2["Manual técnico"]
    H --> H1["Revisão técnica e relatório final"]
    H --> H2["Termo de homologação"]
    H --> H3["Apresentação"]
```
## Cronograma

```mermaid
gantt
    title Cronograma do Projeto
    dateFormat YYYY-MM-DD

    section Entrega A1
    Documentação A1 (visão, ERS, UML, PGQ, testes) :tarefa1, 2026-10-17, 2026-10-20

    section Desenvolvimento e Entrega A3
    Ajustes e evolução do sistema :tarefa2, 2026-10-20, 2026-11-11
    Testes unitários e cobertura 80% :tarefa3, 2026-10-27, 2026-11-17
    Testes de integração :tarefa4, 2026-11-03, 2026-11-18
    Testes de aceitação e defeitos :tarefa5, 2026-11-11, 2026-11-24
    Manuais e relatórios de qualidade :tarefa6, 2026-11-17, 2026-11-25
    Homologação e apresentação :tarefa7, 2026-11-25, 2026-12-01
```


| Marco | Data |
|---|---|
| Entrega A1 | 20/10/2026 |
| Cobertura ≥ 80% atingida | 11/11/2026 |
| Fim da execução dos testes de aceitação | 24/11/2026 |
| Entrega A3 | 01/12/2026 |

## Distribuição de responsabilidades
Preencher com os nomes da equipe (ajustar o número de papéis ao tamanho do grupo).

| Papel | Responsável | Atividades |
|---|---|---|
| Gerente do projeto / Analista de requisitos | [nome] | Cronograma, ERS, rastreabilidade, ata de revisão |
| Arquiteto / Desenvolvedor | [nome] | Arquitetura, implementação, manual técnico |
| Analista de testes (QA) | [nome] | Plano de testes, casos de teste, execução, registro de defeitos, métricas |
| Documentação / Homologação | [nome] | Manual do usuário, termo de homologação, apresentação |

## Riscos
| Risco | Probabilidade | Ação |
|---|---|---|
| Regras de meta/produção divergirem do esperado pelo cliente | Média | Validar RN010/RN011 com o responsável antes do A3 |
| Cobertura de testes abaixo de 80% | Média | Medir cedo com `coverage` e priorizar rotas sem teste |
| Prazo curto no A1 | Alta | Reaproveitar os artefatos e priorizar os obrigatórios |

