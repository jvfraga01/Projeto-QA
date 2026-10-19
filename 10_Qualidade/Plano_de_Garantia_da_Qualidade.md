# 6. Plano de Garantia da Qualidade (PGQ)

## Padrões de Desenvolvimento (codificação)
- Linguagem Python 3.10+, estilo **PEP 8** (linhas até ~100 colunas, 4 espaços).
- Nomes de funções, variáveis e tabelas em português, claros e sem abreviações obscuras.
- Regras de negócio **somente** em `regras.py`; rotas só validam, autorizam e chamam as regras; nenhuma regra nos templates.
- Todo SQL com parâmetros (`?`); nunca concatenar texto do usuário em comandos SQL.
- Dinheiro sempre em centavos inteiros; percentuais em pontos-base.
- Comentários e *docstrings* explicam o **porquê** das regras, não o óbvio.
- Toda rota protegida usa `@nivel_exigido` ou `@login_obrigatorio`.

## Controle de Versão
- Git, repositório único com a estrutura de entrega (`Projeto_FolhaPagamento/`).
- Ramo `main` sempre funcional; trabalho em ramos 
- Marcos com *tags*: `v1.2-A1` (entrega A1) e `v-A3` (entrega final).
- Não versionar: `__pycache__/`, `instance/` (banco e chave secreta), `.venv/`, `.coverage`.

## Revisões Técnicas
| Item | Descrição |
|---|---|
| Quando | Antes de cada *commit* em `main` e uma revisão formal por entrega (A1 e A3) |
| Quem | Autor + 1 revisor (outro integrante) |
| Registro | Ata de Revisão Técnica (data, participantes, itens, ações) |
| Checklist | Atende ao requisito? Segue o padrão de código? Valida entradas? Checa permissão no backend? Tem teste? Documentação atualizada? Sem dados sensíveis no código? |

## Critérios de Qualidade (ISO/IEC 25010)
| Característica | Como é verificada |
|---|---|
| Adequação funcional | Casos de teste ligados aos requisitos (matriz de rastreabilidade) |
| Segurança | Testes de autorização, CSRF, XSS e vazamento de hash |
| Usabilidade | Teste de aceitação com roteiro do manual; instalação com dois cliques |
| Confiabilidade / integridade | Valores em centavos, restrições do banco, folha fechada imutável |
| Manutenibilidade | Código modular, regras isoladas, cobertura ≥ 80% |
| Portabilidade | Execução em Windows e Linux |

## Métricas Adotadas
| Métrica | Fórmula | Meta |
|---|---|---|
| Cobertura de testes | linhas executadas ÷ linhas totais (coverage.py) | ≥ 80% |
| Requisitos atendidos | RF/RN com teste aprovado ÷ total | 100% |
| Casos de teste aprovados | aprovados ÷ executados | ≥ 95% |
| Defeitos críticos abertos | contagem | 0 |
| Defeitos corrigidos | corrigidos ÷ encontrados | 100% dos críticos e altos |
| Densidade de defeitos | defeitos ÷ nº de requisitos | acompanhar |

## Gestão de Defeitos
Fluxo: **Novo → Em_Correcao → Corrigido → Homologado → Fechado**.

| Severidade | Definição |
|---|---|
| Crítica | Impede o uso, perde dados ou expõe dados de outro usuário |
| Alta | Cálculo errado ou função principal falhando, sem contorno |
| Média | Função secundária falhando, com contorno |
| Baixa | Cosmético ou texto |

Prioridade: Alta (corrigir já), Média (próxima entrega), Baixa (se houver tempo). Cada defeito tem ID (BUG001...), descrição, severidade, prioridade, status, responsável e solução aplicada.

## Critérios de Aprovação
O sistema é aprovado quando: (1) 100% dos requisitos obrigatórios foram implementados e testados; (2) nenhum defeito crítico ou alto aberto; (3) cobertura ≥ 80%; (4) ≥ 95% dos casos de teste aprovados; (5) documentos revisados e Termo de Homologação assinado.
