import sqlite3
from datetime import datetime
from flask import Flask, request, url_for, render_template, redirect
from cadastro_sqlite import conectar_banco
from validacoes import validar_placa
 
app = Flask(__name__)
 
 
def ler_formulario():
    """Le os campos enviados e devolve um dicionario ja limpo."""
    return {
        "cliente": request.form.get("cliente", "").strip(),
        "marca": request.form.get("marca", "").strip(),
        "modelo": request.form.get("modelo", "").strip(),
        "placa": request.form.get("placa", "").strip().upper(),
        "cor": request.form.get("cor", "").strip(),
    }
 
 
def validar_formulario(dados, conn, id_atual=None):
    """Valida os dados vindos do formulario.
 
    Devolve um dicionario de erros: {campo: mensagem}.
    Dicionario vazio significa que esta tudo certo.
    """
    erros = {}
 
    if len(dados["cliente"]) < 2:
        erros["cliente"] = "O cliente deve ter pelo menos 2 caracteres."
 
    if len(dados["marca"]) < 2:
        erros["marca"] = "A marca deve ter pelo menos 2 caracteres."
 
    if len(dados["modelo"]) < 2:
        erros["modelo"] = "Modelo deve ter pelo menos 2 caracteres."
 
    if not validar_placa(dados["placa"]):
        erros["placa"] = "Informe uma placa valida (ABC1234 ou ABC1D23)."
    else:
        # Regra que depende do banco: a placa nao pode se repetir.
        # Ao EDITAR, o proprio registro nao conta como duplicata.
        if id_atual is None:
            existente = conn.execute(
                'SELECT id FROM veiculos WHERE UPPER(placa) = ?',
                (dados["placa"],)).fetchone()
        else:
            existente = conn.execute(
                'SELECT id FROM veiculos WHERE UPPER(placa) = ? AND id <> ?',
                (dados["placa"], id_atual)).fetchone()
        if existente:
            erros["placa"] = "Esta placa ja esta cadastrada."
 
    if len(dados["cor"]) < 2:
        erros["cor"] = "A cor deve ter pelo menos 2 caracteres."
 
    return erros
 
 
@app.route("/")
def listar():
    """Página inicial: todos os veiculos cadastrados."""
    conn = conectar_banco()
    veiculos = conn.execute(
        'SELECT * FROM veiculos ORDER BY cliente').fetchall()
    conn.close()
    return render_template("lista.html", titulo="Veiculos cadastrados",
                            veiculos=veiculos,
                            msg=request.args.get("msg", ""))
 
 
@app.route("/veiculo/<int:id_veiculo>")
def detalhe(id_veiculo):
    """Página de um veiculo específico, identificado pelo id."""
    conn = conectar_banco()
    veiculo = conn.execute('SELECT * FROM veiculos WHERE id = ?',
                            (id_veiculo,)).fetchone()
 
    if veiculo is None:
        conn.close()
        return render_template(
            "erro.html", titulo="Veiculo nao encontrado",
            mensagem=f"Nao existe veiculo com id {id_veiculo}."
        ), 404
 
    # Serviços vinculados a este veiculo
    servicos = conn.execute(
        'SELECT * FROM servicos WHERE veiculo_id = ? ORDER BY data_servico',
        (id_veiculo,)
    ).fetchall()
    conn.close()
 
    return render_template("detalhes.html", titulo=veiculo["cliente"],
                            veiculo=veiculo, servicos=servicos)
 
 
@app.route("/buscar")
def buscar():
    """Busca por cliente. O termo vem na URL: /buscar?termo=ana"""
    termo = request.args.get("termo", "").strip().lower()
 
    encontrados = []
    if termo != "":
        conn = conectar_banco()
        encontrados = conn.execute(
            'SELECT * FROM veiculos WHERE LOWER(cliente) LIKE ? ORDER BY cliente',
            (f'%{termo}%',)
        ).fetchall()
        conn.close()
 
    return render_template("buscar.html", titulo="Buscar veiculo",
                            termo=termo, encontrados=encontrados)
 
 
@app.route("/servicos")
def listar_servicos():
    """Lista todos os serviços cadastrados, com dados do veiculo (JOIN)."""
    conn = conectar_banco()
    registros = conn.execute('''
        SELECT s.id, s.descricao, s.valor, s.data_servico,
               v.id AS veiculo_id, v.cliente, v.placa
        FROM servicos s
        JOIN veiculos v ON s.veiculo_id = v.id
        ORDER BY s.data_servico
    ''').fetchall()
 
    total = conn.execute('SELECT SUM(valor) FROM servicos').fetchone()[0] or 0
    conn.close()
 
    return render_template("servicos.html", titulo="Servicos cadastrados",
                            registros=registros, total=total)
 
def ler_formulario_servico():
    """Le os campos do formulario de servico."""
    return {
        "descricao": request.form.get("descricao", "").strip(),
        "valor": request.form.get("valor", "").strip().replace(",", "."),
    }


def validar_formulario_servico(dados):
    """Valida os dados do formulario de servico."""
    erros = {}

    if len(dados["descricao"]) < 2:
        erros["descricao"] = "A descrição deve ter pelo menos 2 caracteres."

    try:
        valor = float(dados["valor"])
        if valor < 0:
            erros["valor"] = "O valor não pode ser negativo."
    except ValueError:
        erros["valor"] = "Digite um valor válido (ex: 150.00)."

    return erros

@app.route("/servico/novo", methods=["GET", "POST"])
def novo_servico():
    """GET exibe o formulario; POST grava o novo servico."""
    conn = conectar_banco()
    veiculos = conn.execute(
        'SELECT id, cliente, placa FROM veiculos ORDER BY cliente').fetchall()

    if len(veiculos) == 0:
        conn.close()
        return render_template(
            "erro.html", titulo="Nenhum veiculo cadastrado",
            mensagem="Cadastre um veiculo antes de registrar um serviço."
        ), 400

    if request.method == "GET":
        conn.close()
        return render_template(
            "form_servico.html", titulo="Cadastrar servico",
            veiculos=veiculos, dados={}, erros={},
            acao=url_for("novo_servico")
        )

    veiculo_id = request.form.get("veiculo_id", "")
    dados = ler_formulario_servico()
    erros = validar_formulario_servico(dados)

    if not veiculo_id.isdigit():
        erros["veiculo_id"] = "Selecione um veiculo."

    if erros:
        conn.close()
        return render_template(
            "form_servico.html", titulo="Cadastrar servico",
            veiculos=veiculos, dados=dados, erros=erros,
            acao=url_for("novo_servico")
        ), 400

    conn.execute(
        'INSERT INTO servicos (veiculo_id, descricao, valor, data_servico)'
        ' VALUES (?, ?, ?, ?)',
        (int(veiculo_id), dados["descricao"], float(dados["valor"]),
         datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    conn.commit()
    conn.close()

    return redirect(url_for("listar_servicos", msg="Servico cadastrado com sucesso!"))

@app.route("/servico/<int:id_servico>/editar", methods=["GET", "POST"])
def editar_servico(id_servico):
    """GET exibe o formulario preenchido; POST grava a alteracao."""
    conn = conectar_banco()
    servico = conn.execute('''
        SELECT s.*, v.cliente, v.placa
        FROM servicos s
        JOIN veiculos v ON s.veiculo_id = v.id
        WHERE s.id = ?
    ''', (id_servico,)).fetchone()

    if servico is None:
        conn.close()
        return render_template(
            "erro.html", titulo="Servico nao encontrado",
            mensagem=f"Nao existe servico com id {id_servico}."
        ), 404

    if request.method == "GET":
        conn.close()
        return render_template(
            "form_servico.html",
            titulo=f"Editar servico — {servico['cliente']}",
            servico=dict(servico),
            dados={"descricao": servico["descricao"], "valor": servico["valor"]},
            erros={},
            acao=url_for("editar_servico", id_servico=id_servico)
        )

    dados = ler_formulario_servico()
    erros = validar_formulario_servico(dados)

    if erros:
        conn.close()
        return render_template(
            "form_servico.html",
            titulo=f"Editar servico — {servico['cliente']}",
            servico=dict(servico),
            dados=dados, erros=erros,
            acao=url_for("editar_servico", id_servico=id_servico)
        ), 400

    conn.execute(
        'UPDATE servicos SET descricao = ?, valor = ? WHERE id = ?',
        (dados["descricao"], float(dados["valor"]), id_servico)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("listar_servicos", msg="Servico atualizado com sucesso!"))

@app.route("/servico/<int:id_servico>/excluir", methods=["POST"])
def excluir_servico(id_servico):
    """Exclui o servico. Aceita SOMENTE POST — um link nao pode apagar dados."""
    conn = conectar_banco()
    servico = conn.execute('''
        SELECT s.*, v.cliente, v.placa
        FROM servicos s
        JOIN veiculos v ON s.veiculo_id = v.id
        WHERE s.id = ?
    ''', (id_servico,)).fetchone()

    if servico is None:
        conn.close()
        return render_template(
            "erro.html", titulo="Servico nao encontrado",
            mensagem=f"Nao existe servico com id {id_servico}."
        ), 404

    conn.execute('DELETE FROM servicos WHERE id = ?', (id_servico,))
    conn.commit()
    conn.close()

    return redirect(url_for(
        "listar_servicos",
        msg=f"Servico '{servico['descricao']}' excluido."))
 
@app.route("/sobre")
def sobre():
    """Página estática de exemplo — não consulta o banco."""
    return render_template("sobre.html", titulo="Sobre")
 
 
@app.route("/novo", methods=["GET", "POST"])
def novo():
    """GET exibe o formulario; POST grava o veiculo."""
    if request.method == "GET":
        return render_template("form.html", titulo="Cadastrar veiculo",
                                dados={}, erros={}, acao=url_for("novo"))
 
    dados = ler_formulario()
    conn = conectar_banco()
    erros = validar_formulario(dados, conn)
 
    if erros:
        conn.close()
        # devolve o formulario COM o que foi digitado e as mensagens
        return render_template("form.html", titulo="Cadastrar veiculo",
                                dados=dados, erros=erros,
                                acao=url_for("novo")), 400
 
    conn.execute(
        'INSERT INTO veiculos (cliente, placa, marca, modelo, cor, data_cadastro)'
        ' VALUES (?, ?, ?, ?, ?, ?)',
        (dados["cliente"].title(), dados["placa"], dados["marca"],
         dados["modelo"], dados["cor"].title(),
         datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    conn.commit()
    conn.close()
 
    # POST-Redirect-GET: nunca devolver a pagina direto depois de gravar
    return redirect(url_for("listar", msg="Veiculo cadastrado com sucesso!"))
 
 
@app.route("/veiculo/<int:id_veiculo>/editar", methods=["GET", "POST"])
def editar(id_veiculo):
    """GET exibe o formulario preenchido; POST grava a alteracao."""
    conn = conectar_banco()
    veiculo = conn.execute('SELECT * FROM veiculos WHERE id = ?',
                            (id_veiculo,)).fetchone()
 
    if veiculo is None:
        conn.close()
        return render_template(
            "erro.html", titulo="Veiculo nao encontrado",
            mensagem=f"Nao existe veiculo com id {id_veiculo}."
        ), 404
 
    if request.method == "GET":
        conn.close()
        # dict(veiculo) converte a linha do banco em dicionario
        return render_template("form.html", titulo=f"Editar {veiculo['cliente']}",
                                dados=dict(veiculo), erros={},
                                acao=url_for("editar", id_veiculo=id_veiculo))
 
    dados = ler_formulario()
    erros = validar_formulario(dados, conn, id_atual=id_veiculo)
 
    if erros:
        conn.close()
        return render_template("form.html", titulo=f"Editar {veiculo['cliente']}",
                                dados=dados, erros=erros,
                                acao=url_for("editar", id_veiculo=id_veiculo)), 400
 
    conn.execute(
        'UPDATE veiculos SET cliente = ?, placa = ?, marca = ?, modelo = ?, cor = ?'
        ' WHERE id = ?',
        (dados["cliente"].title(), dados["placa"], dados["marca"],
         dados["modelo"], dados["cor"].title(), id_veiculo))
    conn.commit()
    conn.close()
 
    return redirect(url_for("listar", msg="Dados atualizados com sucesso!"))
 
 
@app.route("/veiculo/<int:id_veiculo>/excluir", methods=["POST"])
def excluir(id_veiculo):
    """Exclui o veiculo. Aceita SOMENTE POST — um link nao pode apagar dados."""
    conn = conectar_banco()
    veiculo = conn.execute('SELECT * FROM veiculos WHERE id = ?',
                            (id_veiculo,)).fetchone()

    if veiculo is None:
        conn.close()
        return render_template(
            "erro.html", titulo="Veiculo nao encontrado",
            mensagem=f"Nao existe veiculo com id {id_veiculo}."
        ), 404

    try:
        conn.execute('DELETE FROM veiculos WHERE id = ?', (id_veiculo,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template(
            "erro.html", titulo="Nao foi possivel excluir",
            mensagem=(f"O veiculo de {veiculo['cliente']} possui serviços "
                      "vinculados. Exclua os serviços primeiro.")
        ), 400
    finally:
        conn.close()

    return redirect(url_for(
        "listar", msg=f"Registro de {veiculo['cliente']} excluido."))
 
@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    """Chamada automaticamente quando a URL não corresponde a nenhuma rota."""
    return render_template(
        "erro.html", titulo="Pagina nao encontrada",
        mensagem="Confira o endereco digitado."
    ), 404
 
 
if __name__ == "__main__":
    app.run(debug=True)
