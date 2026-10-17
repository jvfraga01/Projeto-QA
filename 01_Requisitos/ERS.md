# 2. Especificação de Requisitos de Software (ERS)

## Introdução
 Objetivo:  especificar os requisitos do Sistema de Folha de Pagamento.
 Escopo:  conforme o Documento de Visão.
 Fontes:  Requisitos do Cliente (RF001–RF009, RN001–RN008, RNF001–RNF004), sistema anterior e decisões do responsável pelo projeto (RF010 em diante).

 Definições e siglas 
| Termo | Significado |
|---|---|
| RF / RN / RNF | Requisito funcional / Regra de negócio / Requisito não funcional |
| Período | Mês/ano de uma folha (ABERTO ou FECHADO) |
| Meta | Valor mínimo de vendas (R$) ou produção (un) do mês para ter direito ao adicional |
| Adicional | Comissão (comissionado) ou produtividade (produção) somada ao salário base |
| Nível 1/2/3 | Perfis Administrador-RH / Financeiro / Colaborador |
| Exclusão lógica | Mudar o status para Inativo, sem apagar o registro |

## Requisitos Funcionais
| ID | Descrição | Origem |
|---|---|---|
| RF001 | Cadastrar colaborador com matrícula (gerada pelo sistema), nome, salário base, tipo, data de nascimento e datas de contrato. | Cliente |
| RF002 | Cadastrar colaborador  Padrão  (recebe apenas o salário base). | Cliente |
| RF003 | Cadastrar colaborador  Comissionado  informando o percentual de comissão; as vendas são lançadas por mês (RF015). | Cliente |
| RF004 | Cadastrar colaborador  por Produção  informando o valor por unidade; a quantidade é lançada por mês (RF015). | Cliente |
| RF005 | Consultar a lista de colaboradores com dados cadastrais e remuneratórios. | Cliente |
| RF006 | Calcular automaticamente o salário final conforme o tipo de remuneração. | Cliente |
| RF007 | Gerar a folha (matrícula, nome, tipo, salário final) de todos os colaboradores do mês. | Cliente |
| RF008 | Emitir o resumo da folha: custo total, quantidade de colaboradores e total por categoria. | Cliente |
| RF009 | Manter cadastros: incluir, alterar, consultar e remover (a remoção é  lógica , ver RF013). | Cliente |
| RF010 | Autenticar por matrícula e senha; encerrar sessão (logout). Existe um administrador inicial criado com o banco. | Responsável |
| RF011 | Permitir que o usuário altere a própria senha. O RH pode redefinir a senha de outro usuário para a senha inicial. | Responsável |
| RF012 | Controlar o acesso por nível (1, 2 e 3)  no backend , inclusive por URL direta. | Responsável |
| RF013 | Desabilitar e reativar colaborador, preservando todo o histórico. | Responsável |
| RF014 | Gerar a folha de um mês (período), incluindo quem tinha contrato no mês, mesmo que hoje esteja desabilitado. | Responsável |
| RF015 | Lançar as vendas (R$) e a produção (un) do mês e recalcular a folha aberta. | Responsável |
| RF016 | Fechar o mês, congelando os valores calculados (sem reabertura). | Responsável |
| RF017 | Consultar as próprias folhas (meses fechados) e emitir/imprimir o recibo individual. | Responsável |
| RF018 | Filtrar colaboradores (nome, salário máximo, tipo, status) e folha (nome, salário máximo, tipo), de forma combinada. | Responsável |
| RF019 | Calcular metas mensais progressivas (RN009 a RN011). | Responsável |
| RF020 | Imprimir o relatório consolidado e o recibo. | Cliente (relatórios) |

## Regras de Negócio
| ID | Descrição | Origem |
|---|---|---|
| RN001 | Toda matrícula é única (gerada automaticamente pelo sistema). | Cliente |
| RN002 | O nome do colaborador é obrigatório. | Cliente |
| RN003 | O salário base não pode ser negativo. | Cliente |
| RN004 | O valor de vendas não pode ser negativo. | Cliente |
| RN005 | O percentual de comissão não pode ser negativo. | Cliente |
| RN006 | A quantidade produzida não pode ser negativa. | Cliente |
| RN007 | O valor por unidade produzida não pode ser negativo. | Cliente |
| RN008 | O salário final é calculado automaticamente pelo sistema. | Cliente |
| RN009 | Se a meta do mês não for atingida, o adicional é R$ 0,00 (o salário base é mantido). | Responsável |
| RN010 | Meta atingida: comissão = vendas × percentual; o percentual sobe 1 ponto a cada R$ 2.000,00 vendidos acima da meta, até o teto de 10%. Produção: unidades × valor da unidade, com bônus de 1% a cada 50 un acima da meta, até 10%. | Responsável / equipe* |
| RN011 | Meta mínima de vendas R$ 5.000,00 (produção: 100 un). A meta do mês seguinte sobe um passo (R$ 2.000,00 / 50 un) se a anterior foi batida; senão repete. Meta de folha já gerada não muda. | Responsável / equipe |
| RN012 | Folha de mês fechado é imutável (inclusive no banco) e não pode ser reaberta. | Responsável |
| RN013 | Existe uma única folha por colaborador por mês. | Responsável |
| RN014 | Entram na folha do mês os colaboradores com contrato vigente naquele mês. | Responsável |
| RN015 | O nível 3 só acessa as próprias folhas e somente de meses fechados. | Responsável |
| RN016 | Colaboradores nunca são excluídos fisicamente. | Responsável |
| RN017 | Senhas são guardadas com hash; a senha inicial é a data de nascimento em DDMMAAAA. | Responsável |
| RN018 | Não há descontos: salário final = salário base + adicionais. | Responsável |

## Requisitos Não Funcionais
| ID | Descrição | Origem |
|---|---|---|
| RNF001 | Interface amigável e intuitiva (menu por perfil, tema claro/escuro). | Cliente |
| RNF002 | Validar os dados de entrada antes de qualquer cálculo. | Cliente |
| RNF003 | Armazenar os registros de forma persistente (SQLite). | Cliente |
| RNF004 | Permitir novos tipos de remuneração sem alterar os cálculos existentes (calculadores registrados em `CALCULADORES`). | Cliente |
| RNF005 | Segurança: hash de senha, proteção CSRF, escape de saída (XSS), cabeçalho CSP, cookie HttpOnly/SameSite, SQL parametrizado. | Responsável |
| RNF006 | Instalação e uso simples: iniciar com dois cliques; banco e administrador criados automaticamente. | Responsável |
| RNF007 | Precisão monetária: valores em centavos inteiros, arredondamento meio-para-cima. | Equipe |
| RNF008 | Testabilidade: regras de negócio isoladas em módulo puro; cobertura de testes ≥ 80%. | PGQ |
| RNF009 | Portabilidade: Windows, Linux e macOS com Python 3.10+. | Equipe |

## Desvios em relação ao documento do cliente (para validação)
1.  Comissão/produtividade com meta  (RN009–RN011): o cliente define apenas `Vendas × %` e `Quantidade × Valor`. Esses cálculos são mantidos como base quando a meta é atingida, e a progressão foi acrescentada por decisão do responsável pelo projeto.
2.  Vendas/produção lançadas por mês  (RF015) em vez de informadas apenas no cadastro (RF003/RF004).
3.  Remoção lógica  no lugar de exclusão física (RF009 → RF013).
4.  Folha mensal  apenas de quem tem contrato no mês (RF007 → RN014).

## Critérios de Aceitação
| Requisito | Critério |
|---|---|
| RF001–RF004 | Cadastrar os três tipos; matrícula gerada e exibida na lista; campos obrigatórios validados. |
| RF005, RF018 | Lista exibe nome, tipo, salário e status; filtros combinados retornam somente o esperado. |
| RF006, RF019 | Padrão: 3.000,00 → 3.000,00. Comissionado (3%) com vendas 5.000,00 e meta 5.000,00 → total 3.150,00 (base 3.000,00). Vendas abaixo da meta → adicional 0,00. Percentual nunca passa de 10%. Produção: 100 un × 2,50 com meta 100 → adicional 250,00. |
| RF007, RF014 | Folha do mês lista todos com contrato vigente e o total confere com a soma dos salários finais. |
| RF008, RF020 | Resumo mostra total, quantidade e total por categoria; relatório pode ser impresso. |
| RF009, RF013 | Alterar atualiza o cadastro sem afetar meses fechados; desabilitar impede login e mantém o histórico; reativar devolve o acesso. |
| RF010, RF011 | Login com credenciais válidas entra; inválidas são recusadas; troca de senha exige a senha atual. |
| RF012, RN015 | Nível 3 recebe 403 (sem dados) ao acessar a folha de outro ou áreas de gestão; Financeiro não altera nada. |
| RF015, RF016, RN012 | Lançamentos recalculam a folha aberta; após fechar, qualquer alteração é recusada (aplicação e banco). |
| RN001–RN007 | Valores inválidos ou negativos são recusados com mensagem. |
| RNF004 | Um novo calculador pode ser incluído sem modificar os existentes. |

## Matriz de Rastreabilidade
Casos de uso (UC) em `02_Analise/Casos_de_Uso.md`; casos de teste (CT) em `04_Testes/Casos_de_Teste.md`.

| Requisito             | Caso de Uso   | Classe / Módulo                   | Caso de Teste                 | Status        |
|---|---|---|---|---|
| RF001, RF002          | UC001         | Colaborador (`colaboradores.py`)  | CT001, CT004, CT005, CT008    | Implementado  |
| RF003                 | UC001         | Colaborador, CalculoComissionado  | CT002                         | Implementado  |
| RF004                 | UC001         | Colaborador, CalculoProducao      | CT003                         | Implementado  |
| RF005, RF018          | UC002         | Colaborador (lista/filtros)       | CT009, CT010, CT011           | Implementado  |
| RF006, RF019          | UC003         | `regras.py` (calculadores)        | CT015–CT019, CT035            | Implementado  |
| RF007, RF014          | UC003         | Folha, Periodo (`folha.py`)       | CT020, CT034                  | Implementado  |
| RF008, RF020          | UC004         | Folha (relatório)                 | CT021, CT030                  | Implementado  |
| RF009                 | UC005         | Colaborador                       | CT012                         | Implementado  |
| RF013                 | UC006         | Colaborador                       | CT013, CT014, CT036           | Implementado  |
| RF010                 | UC008         | Autenticação (`auth.py`)          | CT022, CT037                  | Implementado  |
| RF011                 | UC007, UC009  | Autenticação                      | CT023                         | Implementado  |
| RF012, RN015          | UC008         | Autorização (`@nivel_exigido`)    | CT024, CT025, CT026           | Implementado  |
| RF015                 | UC010         | Folha (lançamentos)               | CT006, CT007, CT020           | Implementado  |
| RF016, RN012, RN013   | UC011         | Periodo, Folha                    | CT027, CT028                  | Implementado  |
| RF017                 | UC012         | Folha (recibo)                    | CT029                         | Implementado  |
| RN001–RN007           | UC001, UC010  | Validação (`regras.py`)           | CT004–CT008                   | Implementado  |
| RNF004                | —             | `CALCULADORES`                    | CT031                         | Implementado  |
| RNF005                | UC008         | Segurança (`__init__.py`)         | CT024, CT025, CT032, CT033    | Implementado  |
