import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

from . import db, regras

MESES = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def _chave_local(pasta):
    """Sem SECRET_KEY no ambiente, gera uma chave aleatória e guarda em instance/."""
    arquivo = Path(pasta) / "secret.key"
    if not arquivo.exists():
        arquivo.write_text(secrets.token_hex(32))
    return arquivo.read_text().strip()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(exist_ok=True)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "folha.db"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    if test_config:
        app.config.update(test_config)
    app.config["SECRET_KEY"] = (os.environ.get("SECRET_KEY") or app.config.get("SECRET_KEY")
                                or _chave_local(app.instance_path))

    db.init_app(app)
    with app.app_context():
        db.init_db()  # cria as tabelas se ainda não existirem

    from . import auth, colaboradores, folha
    app.register_blueprint(auth.bp)
    app.register_blueprint(colaboradores.bp)
    app.register_blueprint(folha.bp)

    # ------------------------------------------------------------ segurança
    @app.before_request
    def carregar_usuario():
        g.usuario = None
        matricula = session.get("matricula")
        if matricula is not None:
            # Revalida a cada requisição: quem foi desabilitado perde o acesso na hora.
            linha = db.get_db().execute(
                "SELECT matricula, nome, nivel_acesso FROM colaborador "
                "WHERE matricula = ? AND status = 'Ativo'", (matricula,)).fetchone()
            if linha is None:
                session.clear()
            else:
                g.usuario = dict(linha)

    @app.before_request
    def validar_csrf():
        if request.method == "POST":
            enviado = request.form.get("csrf_token", "")
            esperado = session.get("csrf", "")
            if not esperado or not hmac.compare_digest(enviado, esperado):
                abort(400, "Token de segurança inválido. Recarregue a página e tente de novo.")

    @app.after_request
    def cabecalhos(resposta):
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        if g.get("usuario"):
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    app.jinja_env.globals.update(csrf_token=csrf_token, MESES=MESES, TIPOS=regras.TIPOS)

    @app.context_processor
    def contexto():
        from .auth import pode
        return {"usuario": g.get("usuario"), "pode": lambda acao: pode(g.get("usuario"), acao)}

    # ------------------------------------------------------------ filtros de template
    app.add_template_filter(regras.reais, "brl")
    app.add_template_filter(regras.pct, "pct")
    app.add_template_filter(lambda c: regras.TIPOS.get(c, c), "tipo_nome")
    app.add_template_filter(lambda n: regras.NIVEIS.get(n, n), "nivel_nome")
    app.add_template_filter(lambda m: MESES[int(m)], "mes_nome")

    @app.template_filter("data_br")
    def data_br(v):
        return "—" if not v else f"{v[8:10]}/{v[5:7]}/{v[0:4]}"

    @app.template_filter("meta_fmt")
    def meta_fmt(folha):
        if folha["tipo"] == "COMISSIONADO":
            return regras.reais(folha["meta"])
        if folha["tipo"] == "PRODUCAO":
            return f"{folha['meta']} un"
        return "—"

    # ------------------------------------------------------------ rotas gerais e erros
    from .auth import login_obrigatorio

    @app.route("/")
    @login_obrigatorio
    def inicio():
        if g.usuario["nivel_acesso"] == 3:
            return redirect(url_for("folha.minha_folha"))
        return redirect(url_for("colaboradores.lista"))

    for codigo, titulo in ((400, "Requisição inválida"), (403, "Acesso negado"),
                           (404, "Página não encontrada")):
        app.register_error_handler(
            codigo, lambda e, c=codigo, t=titulo: (render_template("erro.html", codigo=c, titulo=t), c))

    return app
