import sqlite3

def inicializar_banco():
    # Cria o arquivo do banco de dados (ou conecta se já existir) na mesma pasta do script
    conexao = sqlite3.connect('folha_pagamento.db')
    cursor = conexao.cursor()

    # Tabela principal de Colaboradores (RF001)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Colaborador (
            matricula INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            salario_base REAL NOT NULL CHECK(salario_base >= 0),
            tipo_colaborador TEXT NOT NULL CHECK(tipo_colaborador IN ('Padrão', 'Comissionado', 'Producao'))
        )
    ''')

    # Tabela para dados de Comissão (RF003)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Colaborador_Comissionado (
            id_comissao INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_colaborador INTEGER,
            valor_vendas REAL NOT NULL CHECK(valor_vendas >= 0),
            percentual_comissao REAL NOT NULL CHECK(percentual_comissao >= 0),
            FOREIGN KEY(matricula_colaborador) REFERENCES Colaborador(matricula) ON DELETE CASCADE
        )
    ''')

    # Tabela para dados de Produção (RF004)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Colaborador_Producao (
            id_producao INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_colaborador INTEGER,
            quantidade_produzida INTEGER NOT NULL CHECK(quantidade_produzida >= 0),
            valor_unidade REAL NOT NULL CHECK(valor_unidade >= 0),
            FOREIGN KEY(matricula_colaborador) REFERENCES Colaborador(matricula) ON DELETE CASCADE
        )
    ''')

    # Salva as alterações e fecha a conexão
    conexao.commit()
    conexao.close()
    print("Banco de dados 'folha_pagamento.db' e tabelas criados com sucesso!")

if __name__ == '__main__':
    inicializar_banco()