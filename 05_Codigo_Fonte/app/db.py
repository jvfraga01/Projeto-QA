import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    _criar_admin_inicial(db)
    db.commit()


def _criar_admin_inicial(db):
    """Na primeira vez (banco vazio) cria o Administrador: matrícula 1, senha 01012000."""
    from datetime import date
    from werkzeug.security import generate_password_hash
    from .regras import ADMIN_NASCIMENTO, senha_inicial

    if db.execute("SELECT COUNT(*) FROM colaborador").fetchone()[0] == 0:
        db.execute(
            """INSERT INTO colaborador (nome, data_nascimento, data_inicio_contrato, nivel_acesso,
                                        senha_hash, tipo, salario_base_centavos)
               VALUES ('Administrador', ?, ?, 1, ?, 'PADRAO', 0)""",
            (ADMIN_NASCIMENTO, date.today().isoformat(),
             generate_password_hash(senha_inicial(ADMIN_NASCIMENTO))))


def init_app(app):
    app.teardown_appcontext(close_db)

