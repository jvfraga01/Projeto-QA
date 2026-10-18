from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from . import regras
from .auth import login_obrigatorio, nivel_exigido
from .db import get_db

bp = Blueprint("colaboradores", __name__)


def _ler_formulario(f):
    """Valida o formulário (RNF002). Devolve (valores_para_o_banco, erros)."""
    erros, v = {}, {}
    v["nome"] = (f.get("nome") or "").strip()
    if not v["nome"] or len(v["nome"]) > 120:
        erros["nome"] = "Informe o nome (até 120 caracteres)."
    for campo, rotulo, obrigatorio in (("data_nascimento", "nascimento", True),
                                       ("data_inicio_contrato", "início do contrato", True),
                                       ("data_fim_contrato", "fim do contrato", False)):
        texto = (f.get(campo) or "").strip()
        if not texto and not obrigatorio:
            v[campo] = None
            continue
        try:
            v[campo] = regras.parse_data(texto)
        except ValueError:
            erros[campo] = f"Informe a data de {rotulo}."
    if (v.get("data_fim_contrato") and v.get("data_inicio_contrato")
            and v["data_fim_contrato"] < v["data_inicio_contrato"]):
        erros["data_fim_contrato"] = "O fim do contrato não pode ser antes do início."
    if v.get("data_nascimento") and v["data_nascimento"] > date.today().isoformat():
        erros["data_nascimento"] = "A data de nascimento não pode estar no futuro."
    try:
        v["nivel_acesso"] = int(f.get("nivel_acesso", ""))
        if v["nivel_acesso"] not in (1, 2, 3):
            raise ValueError
    except ValueError:
        erros["nivel_acesso"] = "Escolha o nível de acesso."
    v["tipo"] = f.get("tipo", "")
    if v["tipo"] not in regras.TIPOS:
        erros["tipo"] = "Escolha o tipo de colaborador."
    try:
        v["salario_base_centavos"] = regras.parse_reais(f.get("salario_base"))
    except ValueError as e:
        erros["salario_base"] = str(e)
    v["percentual_comissao_bp"] = 0
    v["valor_unidade_centavos"] = 0
    if v["tipo"] == "COMISSIONADO":
        try:
            v["percentual_comissao_bp"] = regras.parse_percentual(f.get("percentual_comissao"))
        except ValueError as e:
            erros["percentual_comissao"] = str(e)
    elif v["tipo"] == "PRODUCAO":
        try:
            v["valor_unidade_centavos"] = regras.parse_reais(f.get("valor_unidade"))
        except ValueError as e:
            erros["valor_unidade"] = str(e)
    return v, erros


def _valores_do_banco(c):
    return {"nome": c["nome"], "data_nascimento": c["data_nascimento"],
            "data_inicio_contrato": c["data_inicio_contrato"],
            "data_fim_contrato": c["data_fim_contrato"] or "",
            "nivel_acesso": str(c["nivel_acesso"]), "tipo": c["tipo"],
            "salario_base": regras.reais_campo(c["salario_base_centavos"]),
            "percentual_comissao": regras.pct_campo(c["percentual_comissao_bp"]),
            "valor_unidade": regras.reais_campo(c["valor_unidade_centavos"])}


def _outro_admin_ativo(db, matricula):
    return db.execute("SELECT COUNT(*) FROM colaborador WHERE nivel_acesso = 1 AND status = 'Ativo' "
                      "AND matricula != ?", (matricula,)).fetchone()[0] > 0


def _obter_ou_404(matricula):
    c = get_db().execute("SELECT * FROM colaborador WHERE matricula = ?", (matricula,)).fetchone()
    if c is None:
        abort(404)
    return c


@bp.route("/colaboradores")
@nivel_exigido(1, 2)
def lista():
    nome = request.args.get("nome", "").strip()
    tipo = request.args.get("tipo", "")
    status = request.args.get("status", "Ativo")
    salario_max = request.args.get("salario_max", "").strip()
    sql = ("SELECT matricula, nome, tipo, salario_base_centavos, status, nivel_acesso "
           "FROM colaborador WHERE 1=1")
    params = []
    if nome:
        escapado = nome.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        sql += " AND nome LIKE ? ESCAPE '\\'"
        params.append(f"%{escapado}%")
    if tipo in regras.TIPOS:
        sql += " AND tipo = ?"
        params.append(tipo)
    if status in ("Ativo", "Inativo"):
        sql += " AND status = ?"
        params.append(status)
    if salario_max:
        try:
            limite = regras.parse_reais(salario_max)
            sql += " AND salario_base_centavos <= ?"
            params.append(limite)
        except ValueError:
            flash("Salário máximo inválido; o filtro foi ignorado.", "erro")
    linhas = get_db().execute(sql + " ORDER BY nome COLLATE NOCASE", params).fetchall()
    return render_template("colaboradores_lista.html", linhas=linhas,
                           filtro={"nome": nome, "tipo": tipo, "status": status,
                                   "salario_max": salario_max})


@bp.route("/colaboradores/novo", methods=["GET", "POST"])
@nivel_exigido(1)
def novo():
    v, erros = {"nivel_acesso": "3", "tipo": "PADRAO",
                "data_inicio_contrato": date.today().isoformat()}, {}
    if request.method == "POST":
        v = dict(request.form)
        dados, erros = _ler_formulario(request.form)
        if not erros:
            db = get_db()
            cur = db.execute(
                """INSERT INTO colaborador (nome, data_nascimento, data_inicio_contrato,
                       data_fim_contrato, nivel_acesso, senha_hash, tipo, salario_base_centavos,
                       percentual_comissao_bp, valor_unidade_centavos)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (dados["nome"], dados["data_nascimento"], dados["data_inicio_contrato"],
                 dados["data_fim_contrato"], dados["nivel_acesso"],
                 generate_password_hash(regras.senha_inicial(dados["data_nascimento"])),
                 dados["tipo"], dados["salario_base_centavos"],
                 dados["percentual_comissao_bp"], dados["valor_unidade_centavos"]))
            db.commit()
            flash(f"Colaborador cadastrado. Matrícula {cur.lastrowid}. "
                  f"Senha inicial: data de nascimento (DDMMAAAA).", "ok")
            return redirect(url_for("colaboradores.lista"))
    return render_template("colaborador_form.html", v=v, erros=erros, editar=False), \
        (400 if erros else 200)


@bp.route("/colaboradores/<int:matricula>/editar", methods=["GET", "POST"])
@nivel_exigido(1)
def editar(matricula):
    c = _obter_ou_404(matricula)
    v, erros = _valores_do_banco(c), {}
    if request.method == "POST":
        v = dict(request.form)
        dados, erros = _ler_formulario(request.form)
        db = get_db()
        if (not erros and c["nivel_acesso"] == 1 and dados["nivel_acesso"] != 1
                and not _outro_admin_ativo(db, matricula)):
            erros["nivel_acesso"] = "Este é o último administrador ativo."
        if not erros:
            db.execute(
                """UPDATE colaborador SET nome=?, data_nascimento=?, data_inicio_contrato=?,
                       data_fim_contrato=?, nivel_acesso=?, tipo=?, salario_base_centavos=?,
                       percentual_comissao_bp=?, valor_unidade_centavos=? WHERE matricula=?""",
                (dados["nome"], dados["data_nascimento"], dados["data_inicio_contrato"],
                 dados["data_fim_contrato"], dados["nivel_acesso"], dados["tipo"],
                 dados["salario_base_centavos"], dados["percentual_comissao_bp"],
                 dados["valor_unidade_centavos"], matricula))
            db.commit()
            flash("Colaborador atualizado. Folhas já fechadas não são afetadas.", "ok")
            return redirect(url_for("colaboradores.lista"))
    return render_template("colaborador_form.html", v=v, erros=erros, editar=True,
                           matricula=matricula), (400 if erros else 200)


@bp.route("/colaboradores/<int:matricula>/desabilitar", methods=["POST"])
@nivel_exigido(1)
def desabilitar(matricula):
    c = _obter_ou_404(matricula)
    db = get_db()
    if matricula == g.usuario["matricula"]:
        flash("Você não pode desabilitar o seu próprio acesso.", "erro")
    elif c["nivel_acesso"] == 1 and not _outro_admin_ativo(db, matricula):
        flash("Este é o último administrador ativo.", "erro")
    else:
        hoje = date.today().isoformat()
        fim = c["data_fim_contrato"]
        if fim is None or fim > hoje:
            fim = max(hoje, c["data_inicio_contrato"])
        db.execute("UPDATE colaborador SET status='Inativo', data_fim_contrato=? WHERE matricula=?",
                   (fim, matricula))
        db.commit()
        flash("Colaborador desabilitado. O histórico foi preservado.", "ok")
    return redirect(url_for("colaboradores.lista"))


@bp.route("/colaboradores/<int:matricula>/reativar", methods=["POST"])
@nivel_exigido(1)
def reativar(matricula):
    _obter_ou_404(matricula)
    db = get_db()
    db.execute("UPDATE colaborador SET status='Ativo', data_fim_contrato=NULL WHERE matricula=?",
               (matricula,))
    db.commit()
    flash("Colaborador reativado.", "ok")
    return redirect(url_for("colaboradores.lista", status="Todos"))


@bp.route("/colaboradores/<int:matricula>/redefinir-senha", methods=["POST"])
@nivel_exigido(1)
def redefinir_senha(matricula):
    c = _obter_ou_404(matricula)
    db = get_db()
    db.execute("UPDATE colaborador SET senha_hash=? WHERE matricula=?",
               (generate_password_hash(regras.senha_inicial(c["data_nascimento"])), matricula))
    db.commit()
    flash("Senha redefinida para a data de nascimento (DDMMAAAA).", "ok")
    return redirect(url_for("colaboradores.lista"))


@bp.route("/meus-dados")
@login_obrigatorio
def meus_dados():
    # A matrícula vem da sessão, nunca da URL: ninguém consegue pedir dados de outro.
    c = get_db().execute(
        "SELECT matricula, nome, data_nascimento, data_cadastro, data_inicio_contrato, "
        "data_fim_contrato, nivel_acesso, tipo, salario_base_centavos, percentual_comissao_bp, "
        "valor_unidade_centavos FROM colaborador WHERE matricula = ?",
        (g.usuario["matricula"],)).fetchone()
    return render_template("meus_dados.html", c=c)
