# Sistema de Folha de Pagamento (Flask + SQLite)

## Como rodar (sem terminal) — detalhes e comandos de terminal em `INSTALACAO.md`
1. Instale o Python (python.org) uma vez, marcando "Add Python to PATH".
2. Dê **dois cliques em `iniciar.bat`** (Windows) ou `iniciar.sh` (Linux/Mac), ou em `run.py`.
   Na primeira vez ele instala o Flask sozinho, cria o banco e abre o navegador.
3. Para encerrar, feche a janela preta.

O banco (`instance/folha.db`) é criado automaticamente na primeira execução, junto com o **administrador inicial**:
**matrícula 1, senha 01012000**. A tela de login mostra esse aviso até a senha ser trocada (menu "Senha").
As demais senhas iniciais são a data de nascimento em DDMMAAAA.

Testes (opcional): `python -m unittest discover -v`

## Estrutura
| Arquivo | Para quê |
|---|---|
| `run.py`, `iniciar.bat`, `iniciar.sh` | iniciam o sistema com dois cliques |
| `app/__init__.py` | cria o app, sessão, proteção CSRF, filtros e tratamento de erros |
| `app/schema.sql` | as 3 tabelas |
| `app/db.py` | conexão com o banco, criação das tabelas e do admin inicial |
| `app/regras.py` | **regras de negócio**: dinheiro, metas e cálculo (parâmetros no topo do arquivo) |
| `app/auth.py` | login, logout, troca de senha, decorators de permissão |
| `app/colaboradores.py` | cadastro, alteração, desabilitar/reativar, redefinir senha, meus dados |
| `app/folha.py` | gerar folha do mês, lançamentos, fechar, recibo, relatório |
| `app/templates/`, `app/static/` | telas, CSS e JS |
| `tests/test_sistema.py` | testes de cálculo, permissões, folha e filtros |

## Banco (3 tabelas)
- `colaborador`: dados pessoais + login (usuário e colaborador são a mesma entidade), nível, status, tipo, salário e parâmetros.
- `periodo`: mês da folha (`ABERTO` / `FECHADO`).
- `folha`: uma linha por colaborador por mês, guardando os valores daquele momento (fotografia). Única por (mês, colaborador).
  Depois de fechada, nem o banco deixa alterar ou apagar.
Dinheiro em **centavos** (inteiro); percentual em pontos-base (5,50% = 550).

## Níveis de acesso (verificados no backend)
| Função | 1 Admin/RH | 2 Financeiro | 3 Comum |
|---|---|---|---|
| Login, alterar a própria senha, meus dados, minhas folhas | sim | sim | sim |
| Ver colaboradores / folha de todos / relatório | sim | sim | **não** (403) |
| Cadastrar, alterar, desabilitar, reativar, redefinir senha | sim | não | não |
| Gerar folha, lançar vendas/produção, fechar mês | sim | não | não |
Nível 3 só enxerga as próprias folhas **de meses fechados**. A matrícula vem sempre da sessão, nunca da URL.

## Regras de remuneração
- **Padrão**: salário base.
- **Comissionado**: meta mensal começa em R$ 5.000,00. Meta não batida → adicional R$ 0,00.
  Batida → comissão = vendas × percentual, e o percentual sobe 1 ponto a cada R$ 2.000,00 vendidos acima da meta, até **10%**.
- **Produção**: meta mensal em unidades. Meta não batida → adicional 0. Batida → unidades × valor da unidade,
  com bônus de 1% a cada passo de unidades acima da meta, até **10%**.
- **Meta do mês seguinte**: se bateu a meta, sobe um passo (R$ 2.000,00 ou 50 un); se não bateu, repete. Nunca abaixo do mínimo.
  A meta de uma folha já gerada não muda.
Para criar um novo tipo: escrever uma função em `regras.py`, registrá-la em `CALCULADORES` e incluir o tipo em `schema.sql` e `TIPOS`.

## Fluxo da folha
1. RH: **Folha → Gerar** (mês/ano). Entram todos que tinham contrato no mês (inclusive desabilitados depois).
2. RH: **Lançar vendas / produção** (recalcula; usa o salário atual do cadastro enquanto o mês está aberto).
3. RH: **Fechar mês** (congela; não reabre).
4. Financeiro e RH consultam folha e relatório; cada colaborador vê seu recibo.
