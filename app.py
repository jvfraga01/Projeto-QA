from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def conectar_banco():
    conexao = sqlite3.connect('folha_pagamento.db')
    conexao.row_factory = sqlite3.Row
    return conexao

# ==========================================
# RNF004: Estrutura Orientada a Objetos para Cálculos
# ==========================================
class CalculoRemuneracao:
    def calcular(self, salario_base, dados_extras):
        return 0, salario_base

class CalculoComissionado(CalculoRemuneracao):
    def calcular(self, salario_base, dados_extras):
        vendas = float(dados_extras.get('valor_vendas', 0))
        comissao = float(dados_extras.get('percentual_comissao', 0))
        adicionais = vendas * (comissao / 100.0)
        return adicionais, salario_base + adicionais

class CalculoProducao(CalculoRemuneracao):
    def calcular(self, salario_base, dados_extras):
        qtd = int(dados_extras.get('quantidade_produzida', 0))
        valor_un = float(dados_extras.get('valor_unidade', 0))
        adicionais = qtd * valor_un
        return adicionais, salario_base + adicionais

def processar_salario(tipo, base, extras):
    estrategias = {
        'Padrão': CalculoRemuneracao(),
        'Comissionado': CalculoComissionado(),
        'Producao': CalculoProducao()
    }
    estrategia = estrategias.get(tipo, CalculoRemuneracao())
    return estrategia.calcular(base, extras)

# ==========================================
# Rotas de Interface (Páginas HTML)
# ==========================================
@app.route('/')
def index():
    return render_template('lista.html')

@app.route('/cadastro')
def pagina_cadastro():
    return render_template('cadastro.html')

@app.route('/alterar/<int:matricula>')
def pagina_alteracao(matricula):
    return render_template('alterar.html', matricula=matricula)

@app.route('/folha/<int:matricula>')
def pagina_folha_individual(matricula):
    return render_template('folha_individual.html', matricula=matricula)

@app.route('/relatorios')
def pagina_relatorios():
    return render_template('relatorios.html')

# ==========================================
# Rotas da API (Dados e Validações)
# ==========================================
@app.route('/api/colaboradores', methods=['GET', 'POST'])
def colaboradores():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'POST':
        dados = request.json
        nome = str(dados.get('nome', '')).strip()
        
        if not nome:
            return jsonify({'erro': 'O nome é obrigatório.'}), 400
            
        salario_base = dados.get('salario_base')
        tipo = dados.get('tipo_colaborador')
        
        if salario_base is None or str(salario_base).strip() == '':
            return jsonify({'erro': 'Salário base é obrigatório.'}), 400

        try:
            cursor.execute('INSERT INTO Colaborador (nome, salario_base, tipo_colaborador) VALUES (?, ?, ?)', 
                           (nome, float(salario_base), tipo))
            matricula = cursor.lastrowid

            # Validações Específicas
            if tipo == 'Comissionado':
                vendas = float(dados.get('valor_vendas', 0))
                comissao = float(dados.get('percentual_comissao', 0))
                if vendas < 0 or comissao <= 0:
                    return jsonify({'erro': 'Vendas não podem ser negativas e a comissão deve ser maior que zero.'}), 400
                
                cursor.execute('INSERT INTO Colaborador_Comissionado (matricula_colaborador, valor_vendas, percentual_comissao) VALUES (?, ?, ?)',
                               (matricula, vendas, comissao))
                               
            elif tipo == 'Producao':
                qtd = int(dados.get('quantidade_produzida', 0))
                valor_un = float(dados.get('valor_unidade', 0))
                if qtd < 0 or valor_un <= 0:
                    return jsonify({'erro': 'Quantidade não pode ser negativa e o valor por unidade deve ser maior que zero.'}), 400
                    
                cursor.execute('INSERT INTO Colaborador_Producao (matricula_colaborador, quantidade_produzida, valor_unidade) VALUES (?, ?, ?)',
                               (matricula, qtd, valor_un))

            conexao.commit()
            return jsonify({'mensagem': 'Cadastrado com sucesso!'}), 201
            
        except Exception as e:
            conexao.rollback()
            return jsonify({'erro': str(e)}), 400
        finally:
            conexao.close()

    elif request.method == 'GET':
        cursor.execute('SELECT * FROM Colaborador')
        lista = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        return jsonify(lista)


# API Única para Gerenciar (Ler, Atualizar, Excluir) um Colaborador
@app.route('/api/colaboradores/<int:matricula>', methods=['GET', 'PUT', 'DELETE'])
def gerenciar_colaborador(matricula):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM Colaborador WHERE matricula = ?', (matricula,))
        colab = cursor.fetchone()
        if not colab:
            return jsonify({'erro': 'Colaborador não encontrado'}), 404
        
        dados = dict(colab)
        if dados['tipo_colaborador'] == 'Comissionado':
            cursor.execute('SELECT * FROM Colaborador_Comissionado WHERE matricula_colaborador = ?', (matricula,))
            extra = cursor.fetchone()
            if extra: dados.update(dict(extra))
        elif dados['tipo_colaborador'] == 'Producao':
            cursor.execute('SELECT * FROM Colaborador_Producao WHERE matricula_colaborador = ?', (matricula,))
            extra = cursor.fetchone()
            if extra: dados.update(dict(extra))
        
        conexao.close()
        return jsonify(dados)

    elif request.method == 'PUT':
        dados = request.json
        nome = str(dados.get('nome', '')).strip()
        salario_base = dados.get('salario_base')

        if not nome or salario_base is None or str(salario_base).strip() == '':
            return jsonify({'erro': 'Nome e Salário base são obrigatórios.'}), 400

        try:
            tipo = dados.get('tipo_colaborador')
            
            # Nova trava de segurança Backend: Impede valores zerados ou negativos
            # Nova trava de segurança Backend para Edição
            if tipo == 'Comissionado':
                vendas = float(dados.get('valor_vendas', 0))
                comissao = float(dados.get('percentual_comissao', 0))
                if vendas < 0 or comissao <= 0:
                    return jsonify({'erro': 'Vendas não podem ser negativas e a comissão deve ser maior que zero.'}), 400
                    
            elif tipo == 'Producao':
                qtd = int(dados.get('quantidade_produzida', 0))
                valor_un = float(dados.get('valor_unidade', 0))
                if qtd < 0 or valor_un <= 0:
                    return jsonify({'erro': 'Quantidade não pode ser negativa e o valor por unidade deve ser maior que zero.'}), 400

            # Executa os Updates no banco se passar pelas travas
            cursor.execute('UPDATE Colaborador SET nome = ?, salario_base = ? WHERE matricula = ?', 
                           (nome, float(salario_base), matricula))
            
            if tipo == 'Comissionado':
                cursor.execute('UPDATE Colaborador_Comissionado SET valor_vendas = ?, percentual_comissao = ? WHERE matricula_colaborador = ?',
                               (vendas, comissao, matricula))
            elif tipo == 'Producao':
                cursor.execute('UPDATE Colaborador_Producao SET quantidade_produzida = ?, valor_unidade = ? WHERE matricula_colaborador = ?',
                               (qtd, valor_un, matricula))
            
            conexao.commit()
            return jsonify({'mensagem': 'Cadastro atualizado com sucesso!'})
        except Exception as e:
            conexao.rollback()
            return jsonify({'erro': str(e)}), 400
        finally:
            conexao.close()

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM Colaborador WHERE matricula = ?', (matricula,))
        conexao.commit()
        conexao.close()
        return jsonify({'mensagem': 'Excluído com sucesso!'})


# API para Folha Individual
@app.route('/api/folha/<int:matricula>')
def dados_folha_individual(matricula):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM Colaborador WHERE matricula = ?', (matricula,))
    colab = cursor.fetchone()
    
    if not colab:
        return jsonify({'erro': 'Colaborador não encontrado'}), 404
        
    tipo = colab['tipo_colaborador']
    base = float(colab['salario_base'] or 0.0)
    extras = {}
    detalhes_calculo = ""
    
    if tipo == 'Comissionado':
        cursor.execute('SELECT * FROM Colaborador_Comissionado WHERE matricula_colaborador = ?', (matricula,))
        dados = dict(cursor.fetchone() or {})
        extras = dados
        vendas = float(dados.get('valor_vendas') or 0.0)
        comissao = float(dados.get('percentual_comissao') or 0.0)
        detalhes_calculo = f"Vendas: R$ {vendas:.2f} | Comissão: {comissao}%"
        
    elif tipo == 'Producao':
        cursor.execute('SELECT * FROM Colaborador_Producao WHERE matricula_colaborador = ?', (matricula,))
        dados = dict(cursor.fetchone() or {})
        extras = dados
        qtd = int(dados.get('quantidade_produzida') or 0)
        valor_un = float(dados.get('valor_unidade') or 0.0)
        detalhes_calculo = f"Produzido: {qtd} un. | Valor por un.: R$ {valor_un:.2f}"
    
    adicionais, salario_final = processar_salario(tipo, base, extras)
    conexao.close()
    
    return jsonify({
        'matricula': colab['matricula'],
        'nome': colab['nome'],
        'tipo': tipo,
        'salario_base': base,
        'detalhes_calculo': detalhes_calculo,
        'adicionais': adicionais,
        'salario_final': salario_final
    })


# API para Folha Consolidada
@app.route('/api/folha_consolidada')
def folha_consolidada():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute('SELECT * FROM Colaborador')
    colaboradores_db = cursor.fetchall()
    
    folha = []
    total_folha = 0
    totais_categoria = {'Padrão': 0, 'Comissionado': 0, 'Producao': 0}
    
    for colab in colaboradores_db:
        matricula = colab['matricula']
        tipo = colab['tipo_colaborador']
        base = float(colab['salario_base'] or 0.0)
        extras = {}
        
        if tipo == 'Comissionado':
            cursor.execute('SELECT * FROM Colaborador_Comissionado WHERE matricula_colaborador = ?', (matricula,))
            extras = dict(cursor.fetchone() or {})
        elif tipo == 'Producao':
            cursor.execute('SELECT * FROM Colaborador_Producao WHERE matricula_colaborador = ?', (matricula,))
            extras = dict(cursor.fetchone() or {})
            
        adicionais, salario_final = processar_salario(tipo, base, extras)
        
        folha.append({
            'matricula': matricula,
            'nome': colab['nome'],
            'tipo': tipo,
            'salario_base': base,
            'adicionais': adicionais,
            'salario_final': salario_final
        })
        
        total_folha += salario_final
        totais_categoria[tipo] += salario_final
        
    conexao.close()
    
    return jsonify({
        'detalhes': folha,
        'total_folha': total_folha,
        'quantidade_colaboradores': len(folha),
        'totais_categoria': totais_categoria
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)