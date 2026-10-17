"""Testes: cálculo, permissões (backend), folha congelada e filtros.
Rodar com:  python -m unittest discover -v
"""
import os
import re
import tempfile
import unittest

from werkzeug.security import generate_password_hash

from app import create_app, regras
from app.db import get_db


class CalculoTest(unittest.TestCase):
    def test_padrao_recebe_so_o_salario(self):
        r = regras.calcular("PADRAO", 300000)
        self.assertEqual((r["adicionais"], r["total"]), (0, 300000))

    def test_comissionado_meta_nao_batida_zera_adicional(self):
        r = regras.calcular("COMISSIONADO", 300000, meta=500000, vendas=499999, percentual_base=300)
        self.assertEqual(r["adicionais"], 0)
        self.assertFalse(r["atingiu"])

    def test_comissionado_meta_batida_usa_formula_do_pdf(self):
        # vendas 5.000,00 x 3% = 150,00
        r = regras.calcular("COMISSIONADO", 300000, meta=500000, vendas=500000, percentual_base=300)
        self.assertEqual(r["adicionais"], 15000)
        self.assertEqual(r["total"], 315000)

    def test_comissionado_sobe_1_ponto_a_cada_2_mil_e_para_em_10(self):
        # 9.000,00 = meta + 2 passos -> 3% + 2 = 5%
        r = regras.calcular("COMISSIONADO", 0, meta=500000, vendas=900000, percentual_base=300)
        self.assertEqual(r["pct"], 500)
        # vendas enormes -> teto de 10%
        r = regras.calcular("COMISSIONADO", 0, meta=500000, vendas=9_000_000, percentual_base=300)
        self.assertEqual(r["pct"], 1000)

    def test_producao(self):
        r = regras.calcular("PRODUCAO", 100000, meta=100, quantidade=99, valor_unidade=250)
        self.assertEqual(r["adicionais"], 0)
        r = regras.calcular("PRODUCAO", 100000, meta=100, quantidade=100, valor_unidade=250)
        self.assertEqual(r["adicionais"], 25000)
        r = regras.calcular("PRODUCAO", 100000, meta=100, quantidade=200, valor_unidade=250)
        self.assertEqual(r["pct"], 200)  # 2 passos de 50 un = +2%
        self.assertEqual(r["adicionais"], 50000 + 1000)

    def test_valores_negativos_sao_recusados(self):
        with self.assertRaises(ValueError):
            regras.calcular("PADRAO", -1)
        with self.assertRaises(ValueError):
            regras.parse_reais("-10")
        with self.assertRaises(ValueError):
            regras.parse_inteiro("-3")

    def test_meta_cresce_quando_bate_e_nunca_cai_abaixo_do_minimo(self):
        self.assertEqual(regras.proxima_meta("COMISSIONADO"), 500000)
        self.assertEqual(regras.proxima_meta("COMISSIONADO", 500000, 500000), 700000)
        self.assertEqual(regras.proxima_meta("COMISSIONADO", 700000, 100), 700000)

    def test_dinheiro(self):
        self.assertEqual(regras.parse_reais("1.234,56"), 123456)
        self.assertEqual(regras.reais(123456), "R$ 1.234,56")
        self.assertEqual(regras.senha_inicial("1990-03-15"), "15031990")


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "SECRET_KEY": "teste",
                               "DATABASE": os.path.join(self.pasta.name, "t.db")})
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.admin = self.novo("Ana RH", 1, "PADRAO", 500000)
        self.fin = self.novo("Fabio Financeiro", 2, "PADRAO", 400000)
        self.joao = self.novo("Joao Comum", 3, "COMISSIONADO", 300000, pct=300)
        self.maria = self.novo("Maria Comum", 3, "PRODUCAO", 200000, un=250)
        self.padrao = self.novo("Paulo Padrao", 3, "PADRAO", 250000)

    def tearDown(self):
        self.ctx.pop()
        self.pasta.cleanup()

    def novo(self, nome, nivel, tipo, salario, pct=0, un=0, inicio="2026-01-01"):
        db = get_db()
        cur = db.execute(
            """INSERT INTO colaborador (nome, data_nascimento, data_inicio_contrato, nivel_acesso,
                   senha_hash, tipo, salario_base_centavos, percentual_comissao_bp,
                   valor_unidade_centavos) VALUES (?,?,?,?,?,?,?,?,?)""",
            (nome, "1990-03-15", inicio, nivel, generate_password_hash("15031990"), tipo,
             salario, pct, un))
        db.commit()
        return cur.lastrowid

    def cliente(self, matricula=None, senha="15031990"):
        c = self.app.test_client()
        if matricula:
            r = c.get("/login")
            token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
            r = c.post("/login", data={"matricula": matricula, "senha": senha, "csrf_token": token})
            self.assertEqual(r.status_code, 302, "login deveria funcionar")
        return c

    def post(self, c, url, dados=None):
        with c.session_transaction() as s:
            s.setdefault("csrf", "tok")
            token = s["csrf"]
        return c.post(url, data={**(dados or {}), "csrf_token": token})

    def gerar_e_lancar(self, ano=2026, mes=3, vendas="5000,00", qtd="100"):
        adm = self.cliente(self.admin)
        self.post(adm, "/folha/gerar", {"ano": ano, "mes": mes})
        p = get_db().execute("SELECT id FROM periodo WHERE ano=? AND mes=?", (ano, mes)).fetchone()["id"]
        f = {r["matricula"]: r["id"] for r in get_db().execute("SELECT id, matricula FROM folha WHERE periodo_id=?", (p,))}
        self.post(adm, f"/folha/{p}/lancamentos",
                  {f"vendas_{f[self.joao]}": vendas, f"qtd_{f[self.maria]}": qtd})
        return adm, p, f


class LoginTest(BaseTest):
    def test_login_logout_e_senha_errada(self):
        c = self.cliente()
        r = c.get("/login")
        token = re.search(r'name="csrf_token" value="([^"]+)"', r.get_data(as_text=True)).group(1)
        r = c.post("/login", data={"matricula": self.joao, "senha": "errada", "csrf_token": token})
        self.assertEqual(r.status_code, 401)
        c = self.cliente(self.joao)
        self.assertEqual(c.get("/meus-dados").status_code, 200)
        self.post(c, "/logout")
        self.assertEqual(c.get("/meus-dados").status_code, 302)

    def test_rotas_exigem_login(self):
        c = self.cliente()
        for url in ("/colaboradores", "/folha", "/relatorio", "/minha-folha", "/colaboradores/novo"):
            self.assertEqual(c.get(url).status_code, 302, url)

    def test_post_sem_csrf_e_recusado(self):
        c = self.cliente(self.admin)
        self.assertEqual(c.post("/folha/gerar", data={"ano": 2026, "mes": 3}).status_code, 400)

    def test_usuario_desabilitado_perde_acesso_na_hora_e_pode_voltar(self):
        joao = self.cliente(self.joao)
        adm = self.cliente(self.admin)
        self.post(adm, f"/colaboradores/{self.joao}/desabilitar")
        self.assertEqual(joao.get("/meus-dados").status_code, 302)  # sessão derrubada
        r = self.cliente().post("/login")  # sem token
        self.assertEqual(r.status_code, 400)
        self.post(adm, f"/colaboradores/{self.joao}/reativar")
        self.cliente(self.joao)  # consegue entrar de novo

    def test_nao_vaza_hash_de_senha(self):
        for m in (self.admin, self.fin, self.joao):
            c = self.cliente(m)
            for url in ("/meus-dados", "/minha-folha", "/colaboradores", "/folha"):
                self.assertNotIn("scrypt", c.get(url).get_data(as_text=True))

    def test_nao_desabilita_a_si_mesmo_nem_o_ultimo_admin(self):
        adm = self.cliente(self.admin)
        self.post(adm, f"/colaboradores/{self.admin}/desabilitar")
        st = get_db().execute("SELECT status FROM colaborador WHERE matricula=?", (self.admin,)).fetchone()
        self.assertEqual(st["status"], "Ativo")


class PermissaoTest(BaseTest):
    def test_nivel3_nao_acessa_areas_de_gestao(self):
        c = self.cliente(self.joao)
        for url in ("/colaboradores", "/colaboradores/novo", f"/colaboradores/{self.maria}/editar",
                    "/folha", "/relatorio", f"/folha/1/lancamentos"):
            self.assertEqual(c.get(url).status_code, 403, url)
        for url in ("/folha/gerar", f"/colaboradores/{self.maria}/desabilitar",
                    f"/colaboradores/{self.maria}/redefinir-senha", "/folha/1/fechar"):
            self.assertEqual(self.post(c, url).status_code, 403, url)

    def test_nivel3_nao_ve_folha_de_outro_nem_recebe_dados(self):
        adm, p, f = self.gerar_e_lancar()
        self.post(adm, f"/folha/{p}/fechar")
        joao = self.cliente(self.joao)
        r = joao.get(f"/folha/{f[self.maria]}")
        self.assertEqual(r.status_code, 403)
        self.assertNotIn("Maria", r.get_data(as_text=True))
        self.assertEqual(joao.get(f"/folha/{f[self.joao]}").status_code, 200)
        # id inexistente também não revela nada
        self.assertEqual(joao.get("/folha/99999").status_code, 403)

    def test_minha_folha_ignora_parametros_da_url(self):
        adm, p, f = self.gerar_e_lancar()
        self.post(adm, f"/folha/{p}/fechar")
        joao = self.cliente(self.joao)
        html = joao.get(f"/minha-folha?matricula={self.maria}&nome=Maria").get_data(as_text=True)
        self.assertNotIn("Maria", html)
        self.assertIn("Março/2026", html)

    def test_nivel3_so_ve_folha_de_mes_fechado(self):
        adm, p, f = self.gerar_e_lancar()
        joao = self.cliente(self.joao)
        self.assertEqual(joao.get(f"/folha/{f[self.joao]}").status_code, 403)
        self.post(adm, f"/folha/{p}/fechar")
        self.assertEqual(joao.get(f"/folha/{f[self.joao]}").status_code, 200)

    def test_financeiro_le_mas_nao_altera(self):
        adm, p, f = self.gerar_e_lancar()
        fin = self.cliente(self.fin)
        for url in ("/colaboradores", "/folha", "/relatorio", f"/folha/{f[self.maria]}"):
            self.assertEqual(fin.get(url).status_code, 200, url)
        for url in ("/colaboradores/novo", f"/folha/{p}/lancamentos"):
            self.assertEqual(fin.get(url).status_code, 403, url)
        for url in ("/folha/gerar", f"/folha/{p}/fechar", f"/colaboradores/{self.joao}/desabilitar"):
            self.assertEqual(self.post(fin, url).status_code, 403, url)


class FolhaTest(BaseTest):
    def test_gera_calcula_e_totaliza(self):
        adm, p, f = self.gerar_e_lancar(vendas="5000,00", qtd="100")
        linhas = {r["matricula"]: r for r in get_db().execute("SELECT * FROM folha WHERE periodo_id=?", (p,))}
        self.assertEqual(linhas[self.joao]["total_centavos"], 300000 + 15000)   # 3% de 5.000
        self.assertEqual(linhas[self.maria]["total_centavos"], 200000 + 25000)  # 100 x 2,50
        self.assertEqual(linhas[self.padrao]["total_centavos"], 250000)
        html = adm.get(f"/relatorio?periodo={p}").get_data(as_text=True)
        self.assertIn("Total pago por categoria", html)

    def test_folha_fechada_fica_congelada_mesmo_mudando_o_cadastro(self):
        adm, p, f = self.gerar_e_lancar()
        self.post(adm, f"/folha/{p}/fechar")
        db = get_db()
        db.execute("UPDATE colaborador SET salario_base_centavos = 999999 WHERE matricula=?", (self.joao,))
        db.commit()
        # não dá para recalcular, regerar nem editar
        self.assertEqual(self.post(adm, f"/folha/{p}/lancamentos", {f"vendas_{f[self.joao]}": "9999,00"}).status_code, 403)
        self.post(adm, "/folha/gerar", {"ano": 2026, "mes": 3})
        r = db.execute("SELECT salario_base_centavos, total_centavos FROM folha WHERE matricula=? AND periodo_id=?",
                       (self.joao, p)).fetchone()
        self.assertEqual(r["salario_base_centavos"], 300000)
        # nem direto no banco
        with self.assertRaises(Exception):
            db.execute("UPDATE folha SET total_centavos = 1 WHERE periodo_id=?", (p,))

    def test_nao_ha_reabertura_nem_segunda_folha_no_mes(self):
        adm, p, f = self.gerar_e_lancar()
        self.assertEqual(adm.get("/folha/%d/reabrir" % p).status_code, 404)
        self.post(adm, "/folha/gerar", {"ano": 2026, "mes": 3})
        n = get_db().execute("SELECT COUNT(*) FROM folha WHERE periodo_id=? AND matricula=?", (p, self.joao)).fetchone()[0]
        self.assertEqual(n, 1)

    def test_meta_cresce_no_mes_seguinte_se_bateu(self):
        adm, p, f = self.gerar_e_lancar(mes=3, vendas="5000,00", qtd="100")
        self.post(adm, f"/folha/{p}/fechar")
        self.post(adm, "/folha/gerar", {"ano": 2026, "mes": 4})
        p2 = get_db().execute("SELECT id FROM periodo WHERE mes=4").fetchone()["id"]
        meta = lambda m: get_db().execute("SELECT meta FROM folha WHERE periodo_id=? AND matricula=?", (p2, m)).fetchone()["meta"]
        self.assertEqual(meta(self.joao), 700000)  # 5.000 + 2.000
        self.assertEqual(meta(self.maria), 150)    # 100 + 50

    def test_desabilitado_aparece_nos_meses_em_que_trabalhou(self):
        adm, p, f = self.gerar_e_lancar(mes=3)
        self.post(adm, f"/folha/{p}/fechar")
        self.post(adm, f"/colaboradores/{self.padrao}/desabilitar")
        db = get_db()
        db.execute("UPDATE colaborador SET data_fim_contrato='2026-03-31' WHERE matricula=?", (self.padrao,))
        db.commit()
        self.assertIn("Paulo", adm.get(f"/folha?periodo={p}").get_data(as_text=True))
        self.post(adm, "/folha/gerar", {"ano": 2026, "mes": 5})
        p5 = db.execute("SELECT id FROM periodo WHERE mes=5").fetchone()["id"]
        self.assertNotIn("Paulo", adm.get(f"/folha?periodo={p5}").get_data(as_text=True))

    def test_valores_invalidos_nos_lancamentos_nao_salvam(self):
        adm, p, f = self.gerar_e_lancar(vendas="1000,00")
        self.post(adm, f"/folha/{p}/lancamentos", {f"vendas_{f[self.joao]}": "-5"})
        v = get_db().execute("SELECT vendas_centavos FROM folha WHERE id=?", (f[self.joao],)).fetchone()[0]
        self.assertEqual(v, 100000)


class FiltrosTest(BaseTest):
    def test_filtros_de_colaboradores_combinados(self):
        adm = self.cliente(self.admin)
        html = adm.get("/colaboradores?nome=comum&tipo=COMISSIONADO").get_data(as_text=True)
        self.assertIn("Joao", html)
        self.assertNotIn("Maria", html)
        html = adm.get("/colaboradores?salario_max=2500,00&status=Ativo").get_data(as_text=True)
        self.assertIn("Maria", html)
        self.assertNotIn("Joao", html)

    def test_filtro_de_status(self):
        adm = self.cliente(self.admin)
        self.post(adm, f"/colaboradores/{self.maria}/desabilitar")
        self.assertNotIn("Maria", adm.get("/colaboradores").get_data(as_text=True))
        self.assertIn("Maria", adm.get("/colaboradores?status=Inativo").get_data(as_text=True))

    def test_nome_com_html_e_escapado(self):
        adm = self.cliente(self.admin)
        self.novo("<script>alert(1)</script>", 3, "PADRAO", 100)
        html = adm.get("/colaboradores").get_data(as_text=True)
        self.assertNotIn("<script>alert(1)", html)

    def test_cadastro_valida_e_cria_com_senha_de_nascimento(self):
        adm = self.cliente(self.admin)
        r = self.post(adm, "/colaboradores/novo", {"nome": "", "salario_base": "-5"})
        self.assertEqual(r.status_code, 400)
        r = self.post(adm, "/colaboradores/novo", {
            "nome": "Novo Fulano", "data_nascimento": "2000-12-01", "data_inicio_contrato": "2026-01-01",
            "nivel_acesso": "3", "tipo": "PADRAO", "salario_base": "2000,00"})
        self.assertEqual(r.status_code, 302)
        m = get_db().execute("SELECT matricula FROM colaborador WHERE nome='Novo Fulano'").fetchone()[0]
        self.cliente(m, senha="01122000")  # senha inicial = DDMMAAAA


if __name__ == "__main__":
    unittest.main()
