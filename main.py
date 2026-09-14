from cadastro_sqlite import (
    mostrar_menu as menu_sqlite,
    cadastrar_veiculo as cadastrar_sqlite,
    listar_veiculos as listar_sqlite,
    buscar_veiculo as buscar_sqlite,
    editar_veiculo as editar_sqlite,
    excluir_veiculo as excluir_sqlite,
    cadastrar_servico as cadastrar_servico_sqlite,
    listar_servicos as listar_servicos_sqlite,
    editar_servico as editar_servico_sqlite,
)
 
 
def escolher_modo():
    """Menu inicial para escolher entre JSON e SQLite."""
    print("\n" + "=" * 50)
    print("  OFICINA DO BIEL")
    print("  Sistema de Cadastro de Veiculos")
    print("=" * 50)
    print("\nEscolha o modo de armazenamento:")
    print("1. JSON   (arquivo texto)")
    print("2. SQLite (banco de dados)")
    print("3. Sair")
 
    while True:
        opcao = input("\nEscolha (1-3): ").strip()
        if opcao in ['1', '2']:
            return opcao
        print("Opção inválida!")
 
 
def modo_sqlite():
    """Loop do modo SQLite."""
    while True:
        menu_sqlite()
        opcao = input("Escolha uma opção (1-9): ").strip()
        if opcao == "1":
            cadastrar_sqlite()
        elif opcao == "2":
            listar_sqlite()
        elif opcao == "3":
            buscar_sqlite()
        elif opcao == "4":
            editar_sqlite()
        elif opcao == "5":
            excluir_sqlite()
        elif opcao == "6":
            cadastrar_servico_sqlite()
        elif opcao == "7":
            listar_servicos_sqlite()
        elif opcao == "8":
            editar_servico_sqlite()
        elif opcao == "9":
            print("\nVolte sempre!")
            break
        else:
            print("Opção inválida!")
 
 
if __name__ == "__main__":
    modo_sqlite()
    print("\nObrigado por usar o sistema da Oficina do Biel. Volte sempre!\n")