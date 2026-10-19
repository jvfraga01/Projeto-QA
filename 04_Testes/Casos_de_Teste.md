# 8. Especificação de Casos de Teste

Total: **37 casos** (mínimo exigido: 20). Legenda de tipo: **Auto** = já coberto pela suíte `tests/test_sistema.py` (29 testes aprovados em 17/10/2026); **Manual** = executado por roteiro; **A3** = será automatizado/executado na entrega A3.

Resultado esperado vs. obtido e situação final serão preenchidos na execução (A3).

| Código | Requisito | Objetivo | Passos | Resultado esperado | Tipo | Teste automatizado |
|---|---|---|---|---|---|---|
| CT001 | RF001, RF002 | Cadastrar colaborador Padrão válido | Entrar como RH; Novo colaborador; preencher nome, nascimento, início, nível 3, salário 2000,00, tipo Padrão; confirmar | Colaborador criado com matrícula gerada; aparece na lista; senha inicial = DDMMAAAA | Auto | FiltrosTest.test_cadastro_valida_e_cria_com_senha_de_nascimento |
| CT002 | RF003 | Cadastrar colaborador Comissionado | Novo colaborador; tipo Comissionado; informar comissão base 3,00 | Cadastro salvo; campo de comissão aparece só para esse tipo | Manual (A3: automatizar) | — |
| CT003 | RF004 | Cadastrar colaborador por Produção | Novo colaborador; tipo Por Produção; valor por unidade 2,50 | Cadastro salvo; campo de valor por unidade aparece só para esse tipo | Manual (A3: automatizar) | — |
| CT004 | RN002 | Recusar nome vazio | Novo colaborador com nome em branco; confirmar | Não grava; mensagem de erro no campo nome (HTTP 400) | Auto | FiltrosTest.test_cadastro_valida_e_cria_com_senha_de_nascimento |
| CT005 | RN003 | Recusar salário negativo | Novo colaborador com salário -5; confirmar | Não grava; erro no campo salário | Auto | FiltrosTest.test_cadastro_valida...; CalculoTest.test_valores_negativos_sao_recusados |
| CT006 | RN004, RN005 | Recusar vendas e percentual negativos | Lançamentos: vendas -5; cadastro: comissão -1 | Nada é salvo; erro exibido | Auto (vendas) / Manual (percentual) | FolhaTest.test_valores_invalidos_nos_lancamentos_nao_salvam |
| CT007 | RN006, RN007 | Recusar quantidade e valor por unidade negativos | Lançamentos: quantidade -3; cadastro: valor unidade -1 | Recusado com mensagem | Auto (quantidade) / Manual (valor) | CalculoTest.test_valores_negativos_sao_recusados |
| CT008 | RN001 | Matrícula única e gerada pelo sistema | Cadastrar dois colaboradores seguidos | Matrículas diferentes e sequenciais; banco impede duplicidade (UNIQUE) | Manual (A3: automatizar) | — |
| CT009 | RF005 | Consultar a lista de colaboradores | Entrar como RH ou Financeiro; abrir Colaboradores | Lista com matrícula, nome, tipo, salário e status | Manual (A3: automatizar) | — |
| CT010 | RF018 | Filtros combinados | Filtrar nome 'comum' + tipo Comissionado; depois salário máximo 2500,00 | Somente os colaboradores que atendem a todos os filtros | Auto | FiltrosTest.test_filtros_de_colaboradores_combinados |
| CT011 | RF018 | Filtro de status | Desabilitar um colaborador; listar Ativos e depois Inativos | Ativos não mostra o desabilitado; Inativos mostra | Auto | FiltrosTest.test_filtro_de_status |
| CT012 | RF009 | Alterar colaborador | RH abre Alterar, muda nome e salário, salva | Dados atualizados; folhas fechadas continuam iguais | Manual (A3: automatizar) | — |
| CT013 | RF013 | Desabilitar colaborador | RH desabilita um usuário logado em outra sessão | Sessão cai na hora; login recusado; histórico preservado | Auto | LoginTest.test_usuario_desabilitado_perde_acesso_na_hora_e_pode_voltar |
| CT014 | RF013 | Reativar colaborador | RH reativa o usuário desabilitado | Usuário volta a conseguir entrar | Auto | LoginTest.test_usuario_desabilitado_perde_acesso_na_hora_e_pode_voltar |
| CT015 | RF006 | Cálculo do tipo Padrão | Calcular salário 3.000,00 tipo Padrão | Adicional 0,00; total 3.000,00 | Auto | CalculoTest.test_padrao_recebe_so_o_salario |
| CT016 | RF006, RN010 | Comissão com meta batida (valor-limite) | Salário 3.000,00; comissão 3%; meta 5.000,00; vendas 5.000,00 | Adicional 150,00; total 3.150,00 | Auto | CalculoTest.test_comissionado_meta_batida_usa_formula_do_pdf |
| CT017 | RN009 | Meta não batida zera o adicional | Mesmos dados, vendas 4.999,99 | Adicional 0,00; total 3.000,00 | Auto | CalculoTest.test_comissionado_meta_nao_batida_zera_adicional |
| CT018 | RN010 | Progressão e teto de 10% | Vendas 9.000,00 (2 passos) e vendas muito altas | Percentual 5% e depois limitado a 10% | Auto | CalculoTest.test_comissionado_sobe_1_ponto_a_cada_2_mil_e_para_em_10 |
| CT019 | RF006, RN010 | Cálculo por Produção | Meta 100 un; valor 2,50; produzir 99, 100 e 200 un | 99: 0,00; 100: 250,00; 200: 500,00 + bônus 2% (10,00) | Auto | CalculoTest.test_producao |
| CT020 | RF007, RF014, RF015 | Gerar folha, lançar e totalizar | RH gera folha de março/2026; lança vendas 5.000,00 e produção 100 | Totais: comissionado 3.150,00; produção 2.250,00; padrão 2.500,00 | Auto | FolhaTest.test_gera_calcula_e_totaliza |
| CT021 | RF008 | Resumo da folha | Abrir Relatório do mês | Total, quantidade e total por categoria corretos | Auto (parcial) / Manual (valores) | FolhaTest.test_gera_calcula_e_totaliza |
| CT022 | RF010 | Login válido, inválido e logout | Entrar com senha errada; depois correta; sair | Errada: 401 e mensagem; correta: entra; após sair, páginas redirecionam ao login | Auto | LoginTest.test_login_logout_e_senha_errada; LoginTest.test_rotas_exigem_login |
| CT023 | RF011 | Trocar e redefinir senha | Usuário troca a própria senha; RH redefine a de outro | Troca exige senha atual; redefinição volta ao DDMMAAAA | Manual (A3: automatizar) | — |
| CT024 | RF012 | Nível 3 sem acesso à gestão | Colaborador tenta abrir /colaboradores, /folha, /relatorio e ações POST | HTTP 403 em todos, sem dados | Auto | PermissaoTest.test_nivel3_nao_acessa_areas_de_gestao |
| CT025 | RN015 | Nível 3 não vê folha de outro | Colaborador abre /folha/<id de outro>; abre /minha-folha?matricula=outro; tenta mês aberto | 403 sem nome do outro; parâmetro ignorado; mês aberto negado | Auto | PermissaoTest.test_nivel3_nao_ve_folha_de_outro_nem_recebe_dados; test_minha_folha_ignora_parametros_da_url; test_nivel3_so_ve_folha_de_mes_fechado |
| CT026 | RF012 | Financeiro só consulta | Financeiro abre listas/relatório e tenta criar, lançar, fechar | Leitura 200; alterações 403 | Auto | PermissaoTest.test_financeiro_le_mas_nao_altera |
| CT027 | RF016, RN012 | Folha fechada fica congelada | Fechar o mês; alterar o salário no cadastro; tentar lançar e regerar; UPDATE direto no banco | Valores do mês não mudam; lançamento 403; banco recusa | Auto | FolhaTest.test_folha_fechada_fica_congelada_mesmo_mudando_o_cadastro |
| CT028 | RN013 | Sem reabertura e uma folha por mês | Tentar reabrir; gerar o mesmo mês duas vezes | Sem rota de reabertura (404); apenas 1 folha por colaborador | Auto | FolhaTest.test_nao_ha_reabertura_nem_segunda_folha_no_mes |
| CT029 | RF017 | Recibo individual | Colaborador abre Minhas folhas e o recibo de um mês fechado | Recibo com os valores do mês; botão Imprimir | Auto (acesso) / Manual (visual) | PermissaoTest.test_nivel3_nao_ve_folha_de_outro_nem_recebe_dados |
| CT030 | RF020 | Imprimir relatório e recibo | Clicar em Imprimir e ver a pré-visualização | Menu e botões ocultos; texto legível em preto no branco | Manual | — |
| CT031 | RNF004 | Novo tipo de remuneração sem alterar os existentes | Registrar um calculador novo em CALCULADORES (teste temporário) | Novo tipo calcula; os três existentes seguem iguais | Manual (A3: automatizar) | — |
| CT032 | RNF005 | Proteção CSRF | Enviar POST sem token | HTTP 400, nada executado | Auto | LoginTest.test_post_sem_csrf_e_recusado |
| CT033 | RNF005 | Escape de HTML e sigilo do hash | Cadastrar nome '<script>...'; abrir páginas e procurar o hash | Script aparece como texto; hash nunca exibido | Auto | FiltrosTest.test_nome_com_html_e_escapado; LoginTest.test_nao_vaza_hash_de_senha |
| CT034 | RN014 | Desabilitado aparece nos meses em que trabalhou | Desabilitar colaborador com fim de contrato em março; ver folha de março e de maio | Aparece em março; não aparece em maio | Auto | FolhaTest.test_desabilitado_aparece_nos_meses_em_que_trabalhou |
| CT035 | RN011 | Meta cresce no mês seguinte | Bater a meta em março e gerar abril | Meta de abril: comissionado 7.000,00; produção 150 un | Auto | FolhaTest.test_meta_cresce_no_mes_seguinte_se_bateu |
| CT036 | RF013 | Não desabilitar a si mesmo nem o último admin | Admin tenta desabilitar a própria conta | Recusado; status continua Ativo | Auto | LoginTest.test_nao_desabilita_a_si_mesmo_nem_o_ultimo_admin |
| CT037 | RF010, RNF006 | Primeira execução cria banco e admin | Apagar a pasta instance/; dar dois cliques em iniciar.bat; entrar com 1 / 01012000 | Banco criado; login do admin funciona; aviso de primeiro acesso na tela | Manual (A3: automatizar) | — |

## Resumo por requisito (cobertura de casos)
Todos os RF001–RF020, RN001–RN018 e RNF001–RNF009 aplicáveis possuem ao menos um caso associado na Matriz de Rastreabilidade (`01_Requisitos/ERS.md`). RNF001, RNF002, RNF003, RNF007, RNF008 e RNF009 são verificados indiretamente (usabilidade na aceitação, validação nos CT004–CT007, persistência em todos os fluxos, centavos no CT016/CT019, cobertura pelo relatório do coverage e portabilidade na execução em Windows/Linux).

