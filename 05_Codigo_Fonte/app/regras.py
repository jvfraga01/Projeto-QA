"""Regras de negócio puras: valores em dinheiro, metas e cálculo da remuneração.

Dinheiro é guardado em CENTAVOS (inteiro) para não ter erro de arredondamento.
Percentuais são guardados em PONTOS-BASE: 5,50% = 550.
"""
import re
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# ---------------------------------------------------------------- parâmetros
# >>> Ajuste aqui se a regra de metas mudar. <<<
META_MINIMA_VENDAS = 500_000       # R$ 5.000,00
PASSO_VENDAS = 200_000             # a cada R$ 2.000,00 acima da meta...
META_MINIMA_PRODUCAO = 100         # unidades  (valor ASSUMIDO - confirmar)
PASSO_PRODUCAO = 50                # a cada 50 unidades acima da meta... (ASSUMIDO)
PASSO_PERCENTUAL_BP = 100          # ...sobe 1 ponto percentual
PERCENTUAL_MAXIMO_BP = 1000        # teto de 10%

TIPOS = {"PADRAO": "Padrão", "COMISSIONADO": "Comissionado", "PRODUCAO": "Por Produção"}
NIVEIS = {1: "Admin/RH", 2: "Financeiro", 3: "Comum"}
ADMIN_NASCIMENTO = "2000-01-01"   # senha inicial do admin = 01012000


# ---------------------------------------------------------------- dinheiro
def _decimal(texto):
    t = str(texto or "").strip().replace("R$", "").replace(" ", "")
    if not t:
        raise ValueError("Informe um valor.")
    if t.startswith("-"):
        raise ValueError("O valor não pode ser negativo.")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        d = Decimal(t)
    except InvalidOperation:
        raise ValueError("Valor inválido. Exemplo: 1500,00")
    if not d.is_finite() or d > Decimal("999999999"):
        raise ValueError("Valor inválido.")
    return d


def parse_reais(texto) -> int:
    return int((_decimal(texto) * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def parse_percentual(texto) -> int:
    d = _decimal(texto)
    if d > 100:
        raise ValueError("O percentual não pode passar de 100%.")
    return int((d * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def parse_inteiro(texto) -> int:
    t = str(texto or "").strip()
    if t.startswith("-"):
        raise ValueError("Não pode ser negativo.")
    if not t.isdigit() or int(t) > 1_000_000_000:
        raise ValueError("Informe um número inteiro.")
    return int(t)


def parse_data(texto) -> str:
    try:
        return date.fromisoformat(str(texto or "").strip()).isoformat()
    except ValueError:
        raise ValueError("Data inválida.")


def reais(c) -> str:
    c = int(c)
    r, cent = divmod(abs(c), 100)
    return f"{'-' if c < 0 else ''}R$ {r:,}".replace(",", ".") + f",{cent:02d}"


def reais_campo(c) -> str:
    r, cent = divmod(int(c), 100)
    return f"{r},{cent:02d}"


def pct(bp) -> str:
    return f"{int(bp) // 100},{int(bp) % 100:02d}%"


def pct_campo(bp) -> str:
    return f"{int(bp) // 100},{int(bp) % 100:02d}"


def senha_inicial(data_nascimento_iso: str) -> str:
    """Senha inicial = data de nascimento no formato DDMMAAAA (ex.: 15031990)."""
    a, m, d = data_nascimento_iso.split("-")
    return f"{d}{m}{a}"


# ---------------------------------------------------------------- metas
def proxima_meta(tipo, meta_anterior=None, resultado_anterior=None) -> int:
    """Meta do mês. Começa no mínimo; cresce um passo quando o colaborador bateu a meta
    do mês anterior; se não bateu, repete a anterior. Nunca fica abaixo do mínimo."""
    if tipo == "COMISSIONADO":
        minimo, passo = META_MINIMA_VENDAS, PASSO_VENDAS
    elif tipo == "PRODUCAO":
        minimo, passo = META_MINIMA_PRODUCAO, PASSO_PRODUCAO
    else:
        return 0
    if meta_anterior is None or resultado_anterior is None:
        return minimo
    if resultado_anterior >= meta_anterior:
        return max(minimo, meta_anterior + passo)
    return max(minimo, meta_anterior)


# ---------------------------------------------------------------- cálculo
def _arredonda(numerador, denominador):
    return (numerador * 2 + denominador) // (denominador * 2)  # meio para cima


def _padrao(d):
    return {"atingiu": False, "pct": 0, "adicionais": 0}


def _comissionado(d):
    """Comissão = vendas × percentual (fórmula do PDF). Meta não batida -> adicional 0.
    Batida: o percentual sobe 1 ponto a cada passo de vendas acima da meta, até 10%."""
    if d["vendas"] < d["meta"]:
        return {"atingiu": False, "pct": 0, "adicionais": 0}
    passos = (d["vendas"] - d["meta"]) // PASSO_VENDAS
    p = min(PERCENTUAL_MAXIMO_BP, d["percentual_base"] + passos * PASSO_PERCENTUAL_BP)
    return {"atingiu": True, "pct": p, "adicionais": _arredonda(d["vendas"] * p, 10000)}


def _producao(d):
    """Produtividade = quantidade × valor da unidade (fórmula do PDF). Meta não batida -> 0.
    Batida: bônus de 1% a cada passo de unidades acima da meta, até 10%."""
    if d["quantidade"] < d["meta"]:
        return {"atingiu": False, "pct": 0, "adicionais": 0}
    passos = (d["quantidade"] - d["meta"]) // PASSO_PRODUCAO
    bonus = min(PERCENTUAL_MAXIMO_BP, passos * PASSO_PERCENTUAL_BP)
    base = d["quantidade"] * d["valor_unidade"]
    return {"atingiu": True, "pct": bonus, "adicionais": base + _arredonda(base * bonus, 10000)}


# Para criar um novo tipo de remuneração: escreva a função e registre aqui (RNF004).
CALCULADORES = {"PADRAO": _padrao, "COMISSIONADO": _comissionado, "PRODUCAO": _producao}


def calcular(tipo, salario_base, meta=0, vendas=0, quantidade=0,
             percentual_base=0, valor_unidade=0) -> dict:
    if min(salario_base, meta, vendas, quantidade, percentual_base, valor_unidade) < 0:
        raise ValueError("Valores negativos não são permitidos.")
    r = CALCULADORES[tipo]({"meta": meta, "vendas": vendas, "quantidade": quantidade,
                            "percentual_base": percentual_base, "valor_unidade": valor_unidade})
    r["total"] = salario_base + r["adicionais"]
    return r
