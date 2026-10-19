# 7. Plano de Testes

## Escopo
**Será testado:** cadastro e manutenção de colaboradores, filtros, cálculo de remuneração (3 tipos e metas), geração/lançamento/fechamento da folha, relatórios, autenticação, autorização por nível, validações (RN001–RN007) e segurança básica (CSRF, XSS, vazamento de hash).
**Não será testado:** desempenho com grande volume, compatibilidade com navegadores antigos, itens fora do escopo do Documento de Visão.

## Estratégia
Testes automatizados para regras e rotas, mais roteiro manual para itens visuais (impressão, aparência).

| Nível | Objetivo | Alvo | Técnica |
|---|---|---|---|
| Unitário | Validar cada regra isolada | `regras.py` (cálculo, metas, dinheiro) | `unittest`, sem banco |
| Integração | Validar rotas + banco juntos | Fluxos: cadastro → folha → fechamento, permissões, filtros | Flask test client + SQLite temporário |
| Sistema | Validar o sistema completo | Instalação, login e uso pelas telas | Execução manual guiada |
| Aceitação | Confirmar que atende o cliente | Critérios de aceitação da ERS | Roteiro com o responsável pelo projeto |

Técnicas: caixa-preta (partição de equivalência e valores-limite, por exemplo vendas = meta, meta − 1 centavo, percentual no teto de 10%) e caixa-branca (cobertura de desvios das rotas).

## Ambiente
| Item | Descrição |
|---|---|
| SO | Windows 10/11 e Ubuntu 22.04 |
| Banco | SQLite 3 (arquivo temporário nos testes automatizados) |
| Framework | Python 3.12, Flask 3.1, Werkzeug |
| Navegador (manual) | Chrome ou Edge atual |
| Dados de teste | Administrador inicial e colaboradores criados pelos próprios testes |

## Ferramentas
`unittest` (execução), Flask test client (requisições), `coverage.py` (cobertura), Git (versionamento), planilha/tabela do Registro de Defeitos.

Comandos:
```bash
python -m unittest discover -v
python -m coverage run -m unittest discover
python -m coverage report -m
```

## Critérios de Entrada
- Requisitos (ERS) aprovados e casos de teste escritos.
- Sistema compila/inicia sem erro e banco criado.
- Ambiente de teste disponível.

## Critérios de Saída
- Todos os casos planejados executados.
- Nenhum defeito crítico ou alto aberto.
- Cobertura ≥ 80%.
- Relatório de Testes e Registro de Defeitos atualizados.

## Critérios de Aprovação
Ver PGQ: ≥ 95% dos casos aprovados, 0 defeitos críticos e 100% dos requisitos atendidos.

## Situação atual (17/10/2026)
Suíte automatizada com **29 testes**, todos aprovados. Cobertura ainda não medida (meta para o A3). Casos manuais e os itens "A3" do arquivo de Casos de Teste serão automatizados/executados na A3.

## Responsabilidades e riscos
Responsável pela execução: Analista de testes (QA). Riscos: regra de metas ainda sujeita a validação; ver `03_Projeto/Planejamento_do_Projeto.md`.

