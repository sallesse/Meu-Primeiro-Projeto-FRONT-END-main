import sqlite3
import os
from datetime import datetime
from validacoes import validar_placa, placa_ja_cadastrada
 
 
def conectar_banco():
    """Conecta ao banco SQLite e cria as tabelas se não existirem."""
    os.makedirs('dados', exist_ok=True)
    conn = sqlite3.connect('dados/cadastro.db')
    conn.row_factory = sqlite3.Row
 
    # Ativa a checagem de chaves estrangeiras (no SQLite vem desligado por padrão)
    conn.execute('PRAGMA foreign_keys = ON')
 
    conn.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente          TEXT    NOT NULL,
            placa         TEXT   NOT NULL UNIQUE,
            marca         TEXT   NOT NULL,
            modelo        TEXT    NOT NULL ,
            cor        TEXT    NOT NULL,
            data_cadastro TEXT    NOT NULL
        )
    ''')
 
    conn.execute('''
        CREATE TABLE IF NOT EXISTS servicos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            veiculo_id      INTEGER NOT NULL,
            descricao       TEXT    NOT NULL,
            valor           REAL    NOT NULL,
            data_servico    TEXT    NOT NULL,
            FOREIGN KEY (veiculo_id) REFERENCES veiculos (id)
        )
    ''')
 
    conn.commit()
    return conn
 
def mostrar_menu():
    """Exibe o menu principal do sistema."""
    print("\n" + "=" * 50)
    print("  OFICINA DO BIEL (SQLite)")
    print("=" * 50)
    print("1. Cadastrar Veiculo")
    print("2. Listar Veiculos")
    print("3. Buscar Veiculo")
    print("4. Editar Veiculo")
    print("5. Excluir Veiculo")
    print("6. Cadastrar Servico")
    print("7. Listar Servicos")
    print("8. Editar Servico")
    print("9. Sair")
    print("=" * 50)
 
 
def pausar():
    """Pausa a execução aguardando ENTER."""
    input("\nPressione ENTER para continuar...")
 
def cadastrar_veiculo():
    """Cadastra um novo veiculo no banco SQLite com validações."""
    print("\n" + "-" * 40)
    print("  CADASTRO DE NOVO VEICULO (SQLite)")
    print("-" * 40)
 
    conn = conectar_banco()
 
    while True:
        cliente = input("Cliente: ").strip()
        if len(cliente) >= 2:
            break
        print("Erro: cliente deve ter pelo menos 2 caracteres!")
 
    while True:
        placa = input("Placa: ").strip().upper()
        if not validar_placa(placa):
            print("Erro: placa deve ter formato válido ABD1234 ou ABC1D23!")
            continue
        # Agora a duplicata é verificada no banco, não em uma lista
        existente = conn.execute(
            'SELECT id FROM veiculos WHERE LOWER(placa) = ?',
            (placa,)
            ).fetchone()
        if existente:
            print("Erro: Este placa já está cadastrado!")
            continue
        break
 
    while True:
        marca = input("Marca: ").strip()
        if len(marca) >= 2:
            break
        print("Erro: marca deve ter pelo menos 2 caracteres!")
 
    while True:
        modelo = input("modelo: ").strip()
        if len(modelo) >= 2:
            break
        print("Erro: modelo deve ter pelo menos 2 caracteres!")
        
 
    while True:
        cor = input("Cor: ").strip()
        if len(cor) >= 2:
            break
        print("Erro: cor deve ter pelo menos 2 caracteres!")
 
    data_cadastro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
 
    try:
        conn.execute(
            'INSERT INTO veiculos (cliente, placa, marca, modelo, cor, data_cadastro)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (cliente.title(), placa.upper(), marca, modelo, cor, data_cadastro)
        )
        conn.commit()
        print(f"  Cliente: {cliente.title()}")
        print(f"  Placa: {placa.upper()}")
        print(f"  Marca: {marca}")
        print(f"  Modelo: {modelo}")
        print(f"  Cor: {cor}")
 
    except sqlite3.IntegrityError:
        print("\nErro: placa já existe no banco (violação da restrição UNIQUE)!")
    finally:
        conn.close()
 
    pausar()
 
def listar_veiculos():
    """Lista todos os veiculos do banco SQLite."""
    conn = conectar_banco()
 
    registros = conn.execute('SELECT * FROM veiculos ORDER BY Modelo').fetchall()
 
    if len(registros) == 0:
        print("\nNenhum veiculo cadastrado ainda.")
        conn.close()
        pausar()
        return
 
    print("\n" + "-" * 60)
    print(f"  LISTA DE VEICULOS CADASTRADOS ({len(registros)} registros)")
    print("-" * 60)
 
    for reg in registros:
        
        print(f"\n  ID: {reg['id']} | Cliente: {reg['cliente']}")
        print(f"  Placa: {reg['placa']}  | Modelo: {reg['modelo']} | Marca: {reg['marca']}")
        print(f"  Cor: {reg['cor']} | Cadastrado por:: {reg['data_cadastro']}")
        print("-" * 40)
 
    # As estatísticas agora são calculadas pelo banco
    total = conn.execute('SELECT COUNT(*) FROM veiculos').fetchone()[0]
    print("\nEstatísticas:")
    print(f"  Total: {total} veiculos")
 
 
    conn.close()
    pausar()
 
 
def buscar_veiculo():
    """Busca veiculos no banco por nome, email ou cidade."""
    conn = conectar_banco()
 
    total = conn.execute('SELECT COUNT(*) AS FROM veiculos').fetchone()[0]
    if total == 0:
        print("\nNenhum veiculo cadastrado para buscar.")
        conn.close()
        pausar()
        return
 
    print("\n" + "-" * 40)
    print("  BUSCAR VEICULO (SQLite)")
    print("-" * 40)
    print("1. Buscar por marca")
    print("2. Buscar por placa")
    print("3. Buscar por cliente")
 
    while True:
        opcao = input("\nEscolha (1-3): ").strip()
        if opcao in ['1', '2', '3']:
            break
        print("Opção inválida! Escolha 1, 2 ou 3.")
 
    termo = input("Digite o termo para buscar: ").strip()
 
    campos = {'1': 'marca', '2': 'placa', '3': 'cliente'}
    campo = campos[opcao]
 
 
    encontrados = conn.execute(
        f'SELECT * FROM veiculos WHERE LOWER({campo}) LIKE ? ORDER BY cliente',
        (f'%{termo}%',)
    ).fetchall()
 
    if len(encontrados) == 0:
        print(f"\nNenhum veiculo encontrada com '{termo}'")
    else:
        print(f"\n{len(encontrados)} veiculo(s) encontrado(s):")
        print("-" * 50)
        for reg in encontrados:
            print(f"  ID: {reg['id']} | Cliente: {reg['cliente']}")
            print(f"  Placa: {reg['placa']} | Marca: {reg['marca']} | Modelo: {reg['modelo']}")
            print("-" * 30)
 
    conn.close()
    pausar()
 
def escolher_id(conn, acao):
    """Mostra os registros e devolve o id escolhido (ou None se cancelar)."""
    registros = conn.execute(
        'SELECT id, cliente, placa FROM veiculos ORDER BY id').fetchall()
 
    if len(registros) == 0:
        print("\nNenhum veiculo cadastrado.")
        return None
 
    print(f"\nEscolha quem deseja {acao}:")
    print("-" * 50)
    for reg in registros:
        print(f"  {reg['id']} — {reg['cliente']} ({reg['placa']})")
    print("-" * 50)
 
    escolha = input("\nDigite o ID (ou ENTER para cancelar): ").strip()
    if escolha == "":
        print("Operação cancelada.")
        return None
    if not escolha.isdigit():
        print("ID inválido!")
        return None
 
    id_escolhido = int(escolha)
    existe = conn.execute('SELECT id FROM veiculos WHERE id = ?',
                          (id_escolhido,)).fetchone()
    if existe is None:
        print(f"Não existe registro com ID {id_escolhido}!")
        return None
 
    return id_escolhido
 
def editar_veiculo():
    """Altera os dados de um veiculo já cadastrado. (Update)"""
    conn = conectar_banco()
 
    id_escolhido = escolher_id(conn, "editar")
    if id_escolhido is None:
        conn.close()
        pausar()
        return
 
    veiculo = conn.execute('SELECT * FROM veiculos WHERE id = ?',
                          (id_escolhido,)).fetchone()
 
    print("\n" + "-" * 40)
    print(f"  EDITANDO: {veiculo['cliente']}")
    print("-" * 40)
    print("Deixe em branco para manter o valor atual.\n")
 
    novo_cliente = input(f"Cliente [{veiculo['cliente']}]: ").strip()
    novo_cliente = novo_cliente.title() if len(novo_cliente) >= 2 else veiculo['cliente']
 
    while True:
        novo_modelo = input(f"Modelo [{veiculo['modelo']}]: ").strip()
        if novo_modelo == "":
            novo_modelo = veiculo['modelo']
            break
    
    while True:
        nova_marca= input(f"Marca [{veiculo['marca']}]: ").strip()
        if nova_marca == "":
            nova_marca = veiculo['marca']
            break
 
    while True:
        nova_placa = input(f"Placa [{veiculo['placa']}]: ").strip().upper()
        if nova_placa == "":
            nova_placa = veiculo['placa']
            break
        if not validar_placa(nova_placa):
            print("Erro: placa deve ter formato válido!")
            continue
        # O próprio registro não conta como duplicata
        existente = conn.execute(
            'SELECT id FROM veiculos WHERE LOWER(placa) = ? AND id <> ?',
            (nova_placa, id_escolhido)
        ).fetchone()
        if existente:
            print("Erro: Este placa já pertence a outro veiculo!")
            continue
        break
 
    nova_cor = input(f"Cor [{veiculo['cor']}]: ").strip()
    nova_cor = nova_cor.title() if len(nova_cor) >= 2 else veiculo['cor']
 
    try:
        conn.execute(
            'UPDATE veiculos SET cliente = ?, modelo = ?, marca = ?, placa = ?, cor = ?'
            ' WHERE id = ?',
            (novo_cliente, novo_modelo, nova_marca, nova_placa, nova_cor, id_escolhido)
        )
        conn.commit()
        print(f"\nDados de '{novo_cliente}' atualizados com sucesso!")
    except sqlite3.IntegrityError:
        print("\nErro: placa já existe no banco!")
    finally:
        conn.close()
 
    pausar()
 
def excluir_veiculo():
    """Remove um veiculo do banco, com confirmação. (Delete)"""
    conn = conectar_banco()
 
    id_escolhido = escolher_id(conn, "excluir")
    if id_escolhido is None:
        conn.close()
        pausar()
        return
 
    veiculo = conn.execute('SELECT * FROM veiculos WHERE id = ?',
                          (id_escolhido,)).fetchone()
 
    print("\n" + "-" * 40)
    print("  ATENÇÃO — você vai EXCLUIR o registro:")
    print("-" * 40)
    print(f"  ID: {veiculo['id']} | {veiculo['cliente']} | Marca: {veiculo['marca']}")
    print(f"  Placa: {veiculo['placa']} | Modelo: {veiculo['modelo']} | Cor: {veiculo['cor']}")
    print("-" * 40)
    print("Esta ação NÃO pode ser desfeita.")
 
    confirmacao = input("\nConfirma a exclusão? (s/N): ").strip().lower()
 
    if confirmacao != "s":
        print("\nOperação cancelada. Nada foi excluído.")
    else:
        conn.execute('DELETE FROM veiculos WHERE id = ?', (id_escolhido,))
        conn.commit()
        print(f"\nRegistro de '{veiculo['cliente']}' excluído.")
 
    conn.close()
    pausar()
 
 
def ler_valor(mensagem):
    """Lê um valor em R$ do usuário, validando que é um número >= 0."""
    while True:
        valor_texto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(valor_texto)
            if valor >= 0:
                return valor
            print("Erro: valor não pode ser negativo!")
        except ValueError:
            print("Erro: digite um número válido!")
 
 
def cadastrar_servico():
    """Cadastra um novo serviço vinculado a um veiculo já existente."""
    conn = conectar_banco()
 
    print("\n" + "-" * 40)
    print("  CADASTRO DE SERVICO")
    print("-" * 40)
 
    veiculo_id = escolher_id(conn, "cadastrar serviço para")
    if veiculo_id is None:
        conn.close()
        pausar()
        return
 
    while True:
        descricao = input("Descrição do serviço: ").strip()
        if len(descricao) >= 2:
            break
        print("Erro: descrição deve ter pelo menos 2 caracteres!")
 
    valor = ler_valor("Valor (R$): ")
 
    data_servico = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
 
    try:
        conn.execute(
            'INSERT INTO servicos (veiculo_id, descricao, valor, data_servico)'
            ' VALUES (?, ?, ?, ?)',
            (veiculo_id, descricao, valor, data_servico)
        )
        conn.commit()
        print(f"\nServiço '{descricao}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\nErro: veículo não encontrado!")
    finally:
        conn.close()
 
    pausar()
 
 
def listar_servicos():
    """Lista todos os serviços cadastrados, com dados do veiculo (JOIN)."""
    conn = conectar_banco()
 
    registros = conn.execute('''
        SELECT s.id, s.descricao, s.valor, s.data_servico,
               v.cliente, v.placa, v.modelo
        FROM servicos s
        JOIN veiculos v ON s.veiculo_id = v.id
        ORDER BY s.data_servico
    ''').fetchall()
 
    if len(registros) == 0:
        print("\nNenhum serviço cadastrado ainda.")
        conn.close()
        pausar()
        return
 
    print("\n" + "-" * 60)
    print(f"  LISTA DE SERVICOS CADASTRADOS ({len(registros)} registros)")
    print("-" * 60)
 
    for reg in registros:
        print(f"\n  ID: {reg['id']} | Cliente: {reg['cliente']} | Veiculo: {reg['modelo']} ({reg['placa']})")
        print(f"  Serviço: {reg['descricao']} | Valor: R$ {reg['valor']:.2f}")
        print(f"  Data: {reg['data_servico']}")
        print("-" * 40)
 
    total = conn.execute('SELECT SUM(valor) FROM servicos').fetchone()[0]
    print("\nEstatísticas:")
    print(f"  Total faturado: R$ {total:.2f}")
 
    conn.close()
    pausar()
 
 
def escolher_id_servico(conn):
    """Mostra os serviços cadastrados (com o veiculo de cada um) e devolve o id escolhido."""
    registros = conn.execute('''
        SELECT s.id, s.descricao, s.valor, v.cliente, v.placa
        FROM servicos s
        JOIN veiculos v ON s.veiculo_id = v.id
        ORDER BY s.id
    ''').fetchall()
 
    if len(registros) == 0:
        print("\nNenhum serviço cadastrado.")
        return None
 
    print("\nEscolha qual serviço deseja editar:")
    print("-" * 60)
    for reg in registros:
        print(f"  {reg['id']} — {reg['descricao']} | R$ {reg['valor']:.2f} | {reg['cliente']} ({reg['placa']})")
    print("-" * 60)
 
    escolha = input("\nDigite o ID (ou ENTER para cancelar): ").strip()
    if escolha == "":
        print("Operação cancelada.")
        return None
    if not escolha.isdigit():
        print("ID inválido!")
        return None
 
    id_escolhido = int(escolha)
    existe = conn.execute('SELECT id FROM servicos WHERE id = ?',
                          (id_escolhido,)).fetchone()
    if existe is None:
        print(f"Não existe serviço com ID {id_escolhido}!")
        return None
 
    return id_escolhido
 
 
def editar_servico():
    """Altera os dados de um serviço já cadastrado. (Update)"""
    conn = conectar_banco()
 
    id_escolhido = escolher_id_servico(conn)
    if id_escolhido is None:
        conn.close()
        pausar()
        return
 
    servico = conn.execute('SELECT * FROM servicos WHERE id = ?',
                           (id_escolhido,)).fetchone()
 
    print("\n" + "-" * 40)
    print(f"  EDITANDO SERVICO: {servico['descricao']}")
    print("-" * 40)
    print("Deixe em branco para manter o valor atual.\n")
 
    nova_descricao = input(f"Descrição [{servico['descricao']}]: ").strip()
    nova_descricao = nova_descricao if len(nova_descricao) >= 2 else servico['descricao']
 
    valor_texto = input(f"Valor [R$ {servico['valor']:.2f}]: ").strip().replace(",", ".")
    if valor_texto == "":
        novo_valor = servico['valor']
    else:
        try:
            novo_valor = float(valor_texto)
            if novo_valor < 0:
                print("Valor inválido, mantendo o valor atual.")
                novo_valor = servico['valor']
        except ValueError:
            print("Valor inválido, mantendo o valor atual.")
            novo_valor = servico['valor']
 
    trocar_veiculo = input("Deseja trocar o veiculo vinculado a este serviço? (s/N): ").strip().lower()
    if trocar_veiculo == "s":
        novo_veiculo_id = escolher_id(conn, "vincular a este serviço")
        if novo_veiculo_id is None:
            novo_veiculo_id = servico['veiculo_id']
    else:
        novo_veiculo_id = servico['veiculo_id']
 
    try:
        conn.execute(
            'UPDATE servicos SET descricao = ?, valor = ?, veiculo_id = ?'
            ' WHERE id = ?',
            (nova_descricao, novo_valor, novo_veiculo_id, id_escolhido)
        )
        conn.commit()
        print(f"\nServiço '{nova_descricao}' atualizado com sucesso!")
    except sqlite3.IntegrityError:
        print("\nErro: veículo não encontrado!")
    finally:
        conn.close()
 
    pausar()
 
