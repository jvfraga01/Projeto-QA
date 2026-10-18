from calendar import monthrange
from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from . import regras
from .auth import login_obrigatorio, nivel_exigido
from .db import get_db

bp = Blueprint("folha", __name__)


# ---------------------------------------------------------------- auxiliares
def _periodo_ou_404(periodo_id):
    p = get_db().execute("SELECT * FROM periodo WHERE id = ?", (periodo_id,)).fetchone()
    if p is None:
        abort(404)
    return p


def _meta_do_mes(db, c, ano, mes):
    """Meta nova do colaborador no mês, a partir do resultado do mês anterior dele."""
    anterior = db.execute(
        """SELECT f.tipo, f.meta, f.vendas_centavos, f.quantidade_produzida
           FROM folha f JOIN periodo p ON p.id = f.periodo_id
           WHERE f.matricula = ? AND (p.ano < ? OR (p.ano = ? AND p.mes < ?))
           ORDER BY p.ano DESC, p.mes DESC LIMIT 1""", (c["matricula"], ano, ano, mes)).fetchone()
    if anterior is None or anterior["tipo"] != c["tipo"]:
        return regras.proxima_meta(c["tipo"])
    resultado = (anterior["vendas_centavos"] if c["tipo"] == "COMISSIONADO"
                 else anterior["quantidade_produzida"])
    return regras.proxima_meta(c["tipo"], anterior["meta"], resultado)


def _calcular_linha(c, meta, vendas, quantidade):
    return regras.calcular(c["tipo"], c["salario_base_centavos"], meta=meta, vendas=vendas,
                           quantidade=quantidade,
                           percentual_base=c["percentual_comissao_bp"],
                           valor_unidade=c["valor_unidade_centavos"])


def _periodos():
    return get_db().execute("SELECT * FROM periodo ORDER BY ano DESC, mes DESC").fetchall()


def _escolher_periodo(periodos):
    escolhido = request.args.get("periodo", "")
    if escolhido.isdigit():
        for p in periodos:
            if p["id"] == int(escolhido):
                return p
    return periodos[0] if periodos else None


# ---------------------------------------------------------------- telas de consulta
@bp.route("/folha")
@nivel_exigido(1, 2)
def lista():
    periodos = _periodos()
    periodo = _escolher_periodo(periodos)
    nome = request.args.get("nome", "").strip()
    tipo = request.args.get("tipo", "")
    salario_max = request.args.get("salario_max", "").strip()
    linhas, total = [], 0
    if periodo:
        sql, params = "SELECT * FROM folha WHERE periodo_id = ?", [periodo["id"]]
        if nome:
            escapado = nome.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql += " AND nome LIKE ? ESCAPE '\\'"
            params.append(f"%{escapado}%")
        if tipo in regras.TIPOS:
            sql += " AND tipo = ?"
            params.append(tipo)
        if salario_max:
            try:
                limite = regras.parse_reais(salario_max)
                sql += " AND salario_base_centavos <= ?"
                params.append(limite)
            except ValueError:
                flash("Salário máximo inválido; o filtro foi ignorado.", "erro")
        linhas = get_db().execute(sql + " ORDER BY nome COLLATE NOCASE", params).fetchall()
        total = sum(l["total_centavos"] for l in linhas)
    hoje = date.today()
    return render_template("folha_lista.html", periodos=periodos, periodo=periodo, linhas=linhas,
                           total=total, hoje=hoje,
                           filtro={"nome": nome, "tipo": tipo, "salario_max": salario_max})


@bp.route("/minha-folha")
@login_obrigatorio
def minha_folha():
    # Sempre a matrícula da SESSÃO. Nenhum parâmetro da URL altera de quem são os dados.
    linhas = get_db().execute(
        """SELECT f.*, p.ano, p.mes FROM folha f JOIN periodo p ON p.id = f.periodo_id
           WHERE f.matricula = ? AND p.status = 'FECHADO'
           ORDER BY p.ano DESC, p.mes DESC""", (g.usuario["matricula"],)).fetchall()
    return render_template("minha_folha.html", linhas=linhas)


@bp.route("/folha/<int:folha_id>")
@login_obrigatorio
def recibo(folha_id):
    f = get_db().execute(
        """SELECT f.*, p.ano, p.mes, p.status AS status_periodo
           FROM folha f JOIN periodo p ON p.id = f.periodo_id WHERE f.id = ?""",
        (folha_id,)).fetchone()
    if g.usuario["nivel_acesso"] == 3:
        # Nível 3: só a própria folha e só de mês fechado. Qualquer outra coisa = 403 sem dados.
        if f is None or f["matricula"] != g.usuario["matricula"] or f["status_periodo"] != "FECHADO":
            abort(403)
    elif f is None:
        abort(404)
    return render_template("recibo.html", f=f)


@bp.route("/relatorio")
@nivel_exigido(1, 2)
def relatorio():
    periodos = _periodos()
    periodo = _escolher_periodo(periodos)
    resumo, linhas, total = [], [], 0
    if periodo:
        db = get_db()
        linhas = db.execute("SELECT * FROM folha WHERE periodo_id = ? ORDER BY nome COLLATE NOCASE",
                            (periodo["id"],)).fetchall()
        resumo = db.execute(
            "SELECT tipo, COUNT(*) AS qtd, SUM(total_centavos) AS total FROM folha "
            "WHERE periodo_id = ? GROUP BY tipo ORDER BY tipo", (periodo["id"],)).fetchall()
        total = sum(l["total_centavos"] for l in linhas)
    return render_template("relatorio.html", periodos=periodos, periodo=periodo,
                           linhas=linhas, resumo=resumo, total=total)


# ---------------------------------------------------------------- ações do RH (nível 1)
@bp.route("/folha/gerar", methods=["POST"])
@nivel_exigido(1)
def gerar():
    try:
        ano, mes = int(request.form.get("ano", "")), int(request.form.get("mes", ""))
        if not (2000 <= ano <= 2100 and 1 <= mes <= 12):
            raise ValueError
    except ValueError:
        flash("Informe um mês e um ano válidos.", "erro")
        return redirect(url_for("folha.lista"))

    db = get_db()
    p = db.execute("SELECT * FROM periodo WHERE ano = ? AND mes = ?", (ano, mes)).fetchone()
    if p and p["status"] == "FECHADO":
        flash("Esse mês já está fechado e não pode ser alterado.", "erro")
        return redirect(url_for("folha.lista", periodo=p["id"]))
    periodo_id = p["id"] if p else db.execute(
        "INSERT INTO periodo (ano, mes) VALUES (?, ?)", (ano, mes)).lastrowid

    primeiro = date(ano, mes, 1).isoformat()
    ultimo = date(ano, mes, monthrange(ano, mes)[1]).isoformat()
    # Quem trabalhou no mês entra na folha, mesmo que hoje esteja desabilitado.
    elegiveis = db.execute(
        "SELECT * FROM colaborador WHERE data_inicio_contrato <= ? "
        "AND (data_fim_contrato IS NULL OR data_fim_contrato >= ?)", (ultimo, primeiro)).fetchall()
    ja_existem = {r["matricula"] for r in db.execute(
        "SELECT matricula FROM folha WHERE periodo_id = ?", (periodo_id,))}
    novos = 0
    for c in elegiveis:
        if c["matricula"] in ja_existem:
            continue  # a meta de quem já tem folha no mês não muda
        meta = _meta_do_mes(db, c, ano, mes)
        r = _calcular_linha(c, meta, 0, 0)
        db.execute(
            """INSERT INTO folha (periodo_id, matricula, nome, tipo, salario_base_centavos,
                   percentual_comissao_bp, valor_unidade_centavos, meta, meta_atingida,
                   percentual_aplicado_bp, adicionais_centavos, total_centavos)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (periodo_id, c["matricula"], c["nome"], c["tipo"], c["salario_base_centavos"],
             c["percentual_comissao_bp"], c["valor_unidade_centavos"], meta,
             int(r["atingiu"]), r["pct"], r["adicionais"], r["total"]))
        novos += 1
    db.commit()
    flash(f"Folha de {regras_mes(mes)}/{ano}: {novos} colaborador(es) adicionado(s).", "ok")
    return redirect(url_for("folha.lista", periodo=periodo_id))


def regras_mes(mes):
    from . import MESES
    return MESES[mes]


@bp.route("/folha/<int:periodo_id>/lancamentos", methods=["GET", "POST"])
@nivel_exigido(1)
def lancamentos(periodo_id):
    """RH informa as vendas / a produção do mês; o sistema recalcula cada folha aberta."""
    periodo = _periodo_ou_404(periodo_id)
    db = get_db()
    linhas = db.execute("SELECT * FROM folha WHERE periodo_id = ? ORDER BY nome COLLATE NOCASE",
                        (periodo_id,)).fetchall()
    if request.method == "POST":
        if periodo["status"] == "FECHADO":
            abort(403)
        novos, erros = [], []
        for f in linhas:
            vendas, qtd = f["vendas_centavos"], f["quantidade_produzida"]
            try:
                if f["tipo"] == "COMISSIONADO":
                    vendas = regras.parse_reais(request.form.get(f"vendas_{f['id']}") or "0")
                elif f["tipo"] == "PRODUCAO":
                    qtd = regras.parse_inteiro(request.form.get(f"qtd_{f['id']}") or "0")
            except ValueError as e:
                erros.append(f"{f['nome']}: {e}")
            novos.append((f, vendas, qtd))
        if erros:
            for e in erros:
                flash(e, "erro")
            return redirect(url_for("folha.lancamentos", periodo_id=periodo_id))
        for f, vendas, qtd in novos:
            c = db.execute("SELECT * FROM colaborador WHERE matricula = ?", (f["matricula"],)).fetchone()
            meta = f["meta"] if c["tipo"] == f["tipo"] else _meta_do_mes(db, c, periodo["ano"], periodo["mes"])
            r = _calcular_linha(c, meta, vendas, qtd)
            db.execute(
                """UPDATE folha SET nome=?, tipo=?, salario_base_centavos=?, percentual_comissao_bp=?,
                       valor_unidade_centavos=?, meta=?, vendas_centavos=?, quantidade_produzida=?,
                       meta_atingida=?, percentual_aplicado_bp=?, adicionais_centavos=?,
                       total_centavos=? WHERE id=?""",
                (c["nome"], c["tipo"], c["salario_base_centavos"], c["percentual_comissao_bp"],
                 c["valor_unidade_centavos"], meta, vendas, qtd, int(r["atingiu"]), r["pct"],
                 r["adicionais"], r["total"], f["id"]))
        db.commit()
        flash("Lançamentos salvos e folha recalculada.", "ok")
        return redirect(url_for("folha.lista", periodo=periodo_id))
    return render_template("lancamentos.html", periodo=periodo, linhas=linhas)


@bp.route("/folha/<int:periodo_id>/fechar", methods=["POST"])
@nivel_exigido(1)
def fechar(periodo_id):
    periodo = _periodo_ou_404(periodo_id)
    db = get_db()
    qtd = db.execute("SELECT COUNT(*) FROM folha WHERE periodo_id = ?", (periodo_id,)).fetchone()[0]
    if periodo["status"] == "FECHADO":
        flash("Esse mês já está fechado.", "erro")
    elif qtd == 0:
        flash("Não há folhas para fechar neste mês.", "erro")
    else:
        db.execute("UPDATE periodo SET status = 'FECHADO' WHERE id = ?", (periodo_id,))
        db.commit()
        flash("Folha fechada. Os valores agora estão congelados e não podem ser reabertos.", "ok")
    return redirect(url_for("folha.lista", periodo=periodo_id))
