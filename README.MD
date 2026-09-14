# Sistema de Gestão de Veículos e Serviços

**Aluno:** Gabriel Sallesse de Oliveira
**Matrícula:** 202601007513

## Domínio escolhido

Sistema de gestão para um **lava-jato**, voltado ao cadastro e gerenciamento de veículos e dos serviços realizados.

A aplicação permite cadastrar veículos, consultar seus dados, editar e excluir registros, além de cadastrar, editar e excluir serviços vinculados aos veículos.

## Tecnologias utilizadas

* Python
* Flask
* SQLite
* HTML/CSS
* Ambiente virtual Python (`.venv`)

## Como rodar a aplicação

### 1. Clonar o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

### 2. Criar o ambiente virtual

No macOS/Linux:

```bash
python3 -m venv .venv
```

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

No Windows:

```bash
.venv\Scripts\activate
```

### 3. Instalar as dependências

Caso exista um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso ainda não exista:

```bash
pip install flask
```

### 4. Popular/criar o banco de dados

Execute o arquivo responsável pela criação/população do banco:

```bash
python cadastro_sqlite.py
```

### 5. Subir a aplicação

Execute:

```bash
python app.py
```

A aplicação será iniciada pelo Flask.

Depois, acesse no navegador:

```text
http://127.0.0.1:5000
```

## Rotas da aplicação

| Rota                    | Método   | Função                                          |
| ----------------------- | -------- | ----------------------------------------------- |
| `/`                     | GET      | Lista todos os veículos cadastrados             |
| `/veiculo/<id>`         | GET      | Exibe os detalhes de um veículo e seus serviços |
| `/buscar`               | GET      | Busca veículos pelo nome do cliente             |
| `/servicos`             | GET      | Lista todos os serviços cadastrados             |
| `/servico/novo`         | GET/POST | Exibe o formulário e cadastra um novo serviço   |
| `/servico/<id>/editar`  | GET/POST | Edita um serviço existente                      |
| `/servico/<id>/excluir` | POST     | Exclui um serviço                               |
| `/sobre`                | GET      | Exibe a página "Sobre"                          |
| `/novo`                 | GET/POST | Exibe o formulário e cadastra um novo veículo   |
| `/veiculo/<id>/editar`  | GET/POST | Edita um veículo existente                      |
| `/veiculo/<id>/excluir` | POST     | Exclui um veículo                               |

## Regras de validação implementadas

### Veículos

* O nome do cliente deve possuir pelo menos **2 caracteres**.
* A marca deve possuir pelo menos **2 caracteres**.
* O modelo deve possuir pelo menos **2 caracteres**.
* A placa deve seguir o formato válido:

  * `ABC1234` — modelo antigo;
  * `ABC1D23` — modelo Mercosul.
* A placa não pode estar cadastrada mais de uma vez.
* A cor deve possuir pelo menos **2 caracteres**.
* Ao editar um veículo, a própria placa do registro não é considerada uma duplicata.

### Serviços

* A descrição do serviço deve possuir pelo menos **2 caracteres**.
* O valor deve ser um número válido.
* O valor do serviço não pode ser negativo.
* É necessário selecionar um veículo para cadastrar o serviço.
* Não é possível cadastrar um serviço caso não exista nenhum veículo cadastrado.

### Exclusão

* A exclusão de veículos e serviços aceita somente requisições **POST**.
* Um veículo que possui serviços vinculados não pode ser excluído antes que seus serviços sejam excluídos.

### Tratamento de erros

* Caso um veículo informado não exista, a aplicação retorna uma página de erro com código **404**.
* Caso um serviço informado não exista, a aplicação também retorna **404**.
* URLs que não correspondem a nenhuma rota são tratadas por uma página personalizada de erro **404**.

## O que ficou faltando

* Integração com WhatsApp.
* Autenticação e sistema de usuários.
* Controle de permissões.
* Recursos de pagamento.
* Integração com equipamentos físicos do lava-jato.
* Deploy da aplicação em um servidor para acesso externo.

## Observações

A aplicação utiliza o padrão **POST-Redirect-GET** após operações de cadastro e alteração, evitando que o navegador tente reenviar o formulário ao atualizar a página.
