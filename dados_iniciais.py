import sqlite3
 
def criar_banco(caminho='dados/cadastro.db'):
    """Cria as tabelas veiculos e servicos, caso não existam."""
    conn = sqlite3.connect(caminho)
    cursor = conn.cursor()
 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Marca TEXT NOT NULL,
            Modelo TEXT NOT NULL,
            cliente TEXT NOT NULL,
            placa TEXT NOT NULL UNIQUE,
            Cor TEXT
        )
    ''')
 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            veiculo_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL,
            data_servico TEXT,
            FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
        )
    ''')
 
    conn.commit()
    conn.close()
 
 
def popular_dados_iniciais(caminho='dados/cadastro.db'):
    """Insere os dados iniciais de exemplo nas tabelas (não duplica se já existirem)."""
    conn = sqlite3.connect(caminho)
    cursor = conn.cursor()
 
    veiculos_iniciais = [
        (1, 'Volks', 'Tera', 'Carlos', 'ASF1234', 'Preta'),
        (4, 'Porshe', 'Cayenne', 'Pedro', 'POR3D43', 'Marrom'),
        (5, 'BYD', 'Song Plus', 'Marcos', 'BYD3456', 'Preto'),
        (6, 'fiat', 'uno', 'Victor', 'QUE7777', 'Azul'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO veiculos (id, Marca, Modelo, cliente, placa, Cor)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', veiculos_iniciais)
 
    servicos_iniciais = [
        (2, 4, 'Concertar', 70, '13/09/2026 18:36:53'),
        (3, 6, 'pneu', 100, '14/09/2026 15:49:28'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO servicos (id, veiculo_id, descricao, valor, data_servico)
        VALUES (?, ?, ?, ?, ?)
    ''', servicos_iniciais)
 
    conn.commit()
    conn.close()
 
 
if __name__ == '__main__':
    criar_banco()
    popular_dados_iniciais()
    print('Banco de dados criado e populado com sucesso.')
 
