from datetime import date
import time
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from model.pedido import Pedido
from model.item import Item
from model.database import Database
from controler.database_controler import DatabaseControler
from controler.pedido_controler import PedidoControler
from controler.relatorio_controler import RelatorioControler
from controler.item_controler import ItemControler
from report.relatorio1 import PDF
from view.janela1 import janela1

# Configuração de cores
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    FUNDO_AZUL = '\033[44m'
    FUNDO_VERDE = '\033[42m'

def limpar_tela():
    """Limpa a tela do console"""
    print("\n" * 50)

def mostrar_cabecalho():
    """Exibe o cabeçalho do sistema"""
    print(f'''
    {Cores.AZUL}{Cores.NEGRITO}
    ╔════════════════════════════════════════════╗
    ║          BEM-VINDO AO PIZZA MAIS           ║
    ║           - Criando Sonhos -               ║
    ║                                           ║
    ║ Estabelecimento: Pizza Ciclano             ║
    ║ "Seus sonhos tem formato e borda"          ║
    ╚════════════════════════════════════════════╝
    {Cores.RESET}''')

def mostrar_menu_principal():
    """Exibe o menu principal"""
    print(f'''
    {Cores.AZUL}{Cores.NEGRITO}MENU PRINCIPAL{Cores.RESET}
    {Cores.VERDE}1. CADASTRAR NOVO PEDIDO{Cores.RESET}
    {Cores.AZUL}2. CONSULTAR PEDIDOS{Cores.RESET}
    {Cores.AMARELO}3. GERAR RELATÓRIO DE VENDAS{Cores.RESET}
    {Cores.VERMELHO}4. GERENCIAR CARDÁPIO{Cores.RESET}
    {Cores.VERMELHO}5. SAIR DO SISTEMA{Cores.RESET}
    ''')

def inserir_item_menu(database_name: str):
    """Interface para adicionar itens ao cardápio"""
    while True:
        limpar_tela()
        print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} ADICIONAR ITEM AO CARDÁPIO {Cores.RESET}\n")
        
        nome = input(f"{Cores.VERDE}Nome do item: {Cores.RESET}").strip()
        if not nome:
            print(f"{Cores.VERMELHO}O nome não pode ser vazio!{Cores.RESET}")
            time.sleep(1)
            continue
            
        try:
            preco = float(input(f"{Cores.VERDE}Preço (ex: 35.50): R$ {Cores.RESET}"))
            if preco <= 0:
                raise ValueError
        except ValueError:
            print(f"{Cores.VERMELHO}Preço inválido!{Cores.RESET}")
            time.sleep(1)
            continue
            
        tipo = input(f"{Cores.VERDE}Tipo (ex: pizza, bebida): {Cores.RESET}").strip()
        if not tipo:
            print(f"{Cores.VERMELHO}O tipo não pode ser vazio!{Cores.RESET}")
            time.sleep(1)
            continue
            
        ingredientes = input(f"{Cores.VERDE}Ingredientes: {Cores.RESET}").strip()
        if not ingredientes:
            print(f"{Cores.VERMELHO}Os ingredientes não podem ser vazios!{Cores.RESET}")
            time.sleep(1)
            continue
            
        # Confirmar dados
        print(f"\n{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
        print(f"{Cores.NEGRITO}CONFIRME OS DADOS:{Cores.RESET}")
        print(f"{Cores.VERDE}Nome: {Cores.CIANO}{nome}{Cores.RESET}")
        print(f"{Cores.VERDE}Preço: {Cores.AMARELO}R${preco:.2f}{Cores.RESET}")
        print(f"{Cores.VERDE}Tipo: {Cores.CIANO}{tipo}{Cores.RESET}")
        print(f"{Cores.VERDE}Ingredientes: {Cores.CIANO}{ingredientes}{Cores.RESET}")
        print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
        
        confirmar = input(f"\n{Cores.VERDE}Confirmar inclusão? (S/N): {Cores.RESET}").lower()
        if confirmar == 's' or confirmar == "sim":
            novo_item = Item(nome, preco, tipo, ingredientes)
            if ItemControler.insert_into_item(database_name, novo_item):
                print(f"\n{Cores.VERDE}✅ Item adicionado com sucesso!{Cores.RESET}")
            else:
                print(f"\n{Cores.VERMELHO}❌ Erro ao adicionar item!{Cores.RESET}")
        
        continuar = input(f"\n{Cores.VERDE}Adicionar outro item? (S/N): {Cores.RESET}").lower()
        if continuar != 's':
            break

def remover_item_menu(database_name: str):
    """Interface para remover itens do cardápio"""
    while True:
        limpar_tela()
        print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} REMOVER ITEM DO CARDÁPIO {Cores.RESET}\n")
        
        itens = ItemControler.mostrar_itens_menu(database_name)
        if not itens:
            print(f"{Cores.AMARELO}Não há itens no cardápio.{Cores.RESET}")
            time.sleep(2)
            break
            
        print(janela1.formatar_cardapio(itens, modo_remocao=True))
        
        try:
            codigo = int(input(f"\n{Cores.VERDE}Digite o CÓDIGO do item a remover (0 para cancelar): {Cores.RESET}"))
            if codigo == 0:
                break
                
            # Verificar se item existe
            if codigo not in [i[0] for i in itens]:
                print(f"{Cores.VERMELHO}❌ Código inválido!{Cores.RESET}")
                time.sleep(1)
                continue
                
            # Confirmar remoção
            item = next((i for i in itens if i[0] == codigo), None)
            print(f"\n{Cores.VERMELHO}Item selecionado:{Cores.RESET}")
            print(f"{Cores.CIANO}Nome: {item[1]}{Cores.RESET}")
            print(f"{Cores.AMARELO}Preço: R${item[2]:.2f}{Cores.RESET}")
            
            confirmar = input(f"\n{Cores.VERMELHO}Confirmar remoção? (S/N): {Cores.RESET}").lower()
            if confirmar == 's' or confirmar == "sim":
                if ItemControler.remover_item(database_name, codigo):
                    print(f"\n{Cores.VERDE}✅ Item removido com sucesso!{Cores.RESET}")
                else:
                    print(f"\n{Cores.VERMELHO}❌ Item está em pedidos ou não existe!{Cores.RESET}")
                time.sleep(2)
                
        except ValueError:
            print(f"{Cores.VERMELHO}❌ Digite apenas números!{Cores.RESET}")
            time.sleep(1)
            
        continuar = input(f"\n{Cores.VERDE}Remover outro item? (S/N): {Cores.RESET}").lower()
        if continuar not in ('s', 'sim'):
            break

def gerenciar_cardapio(database_name: str):
    """Menu de gerenciamento do cardápio"""
    while True:
        limpar_tela()
        print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} GERENCIAMENTO DO CARDÁPIO {Cores.RESET}\n")
        print(f"{Cores.VERDE}1. Adicionar item{Cores.RESET}")
        print(f"{Cores.VERMELHO}2. Remover item{Cores.RESET}")
        print(f"{Cores.AZUL}3. Voltar{Cores.RESET}")
        
        opcao = input(f"\n{Cores.NEGRITO}Escolha (1-3): {Cores.RESET}").strip()
        
        if opcao == '1':
            inserir_item_menu(database_name)
        elif opcao == '2':
            remover_item_menu(database_name)
        elif opcao == '3':
            break
        else:
            print(f"{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
            time.sleep(1)

def gerar_relatorio(database_name: str):
    """Gera relatório de vendas"""
    limpar_tela()
    print(f"\n{Cores.AMARELO}»»» GERANDO RELATÓRIO «««{Cores.RESET}\n")
    
    timestamp = str(time.time())
    dados = RelatorioControler.preparar_dados_relatorio(database_name)
    sucesso = PDF.gerar_pdf(f'Relatorio{timestamp}.pdf', dados["pedidos"], dados["faturamento_total"])
    
    if sucesso:
        print(f"\n{Cores.VERDE}✅ Relatório gerado: 'Relatorio{timestamp}.pdf'{Cores.RESET}")
    else:
        print(f"\n{Cores.VERMELHO}❌ Falha ao gerar relatório!{Cores.RESET}")
    
    input(f"\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")

# ATUALIZAR FUNÇÕES QUE INSEREM PEDIDOS
def confirmar_pedido(dados_pedido):
    try:
        # Garantir que todos campos obrigatórios estão presentes
        if 'delivery' not in dados_pedido:
            dados_pedido['delivery'] = False
        if 'endereco_entrega' not in dados_pedido:
            dados_pedido['endereco_entrega'] = None
        if 'observacoes' not in dados_pedido:
            dados_pedido['observacoes'] = None
            
        # Inserir pedido
        pedido_id = PedidoControler.inserir_pedido(conn, dados_pedido)
        
        # Inserir itens do pedido com preço unitário
        for item in dados_pedido['itens']:
            item['pedido_id'] = pedido_id
            item['preco_unitario'] = ItemControler.obter_preco_item(conn, item['item_id'])
            PedidoControler.inserir_item_pedido(conn, item)
            
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao confirmar pedido: {e}")
        return False

# CONFIGURAÇÃO INICIAL ATUALIZADA
database = Database('TESTE.db')

# Conexão com tratamento de migração
try:
    conn = DatabaseControler.conect_database(database.name)
    
    # Verificar se a migração foi bem sucedida
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(pedidos)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'delivery' not in columns:
        print("ATENÇÃO: Problema na migração do banco de dados!")
        conn.close()
        sys.exit(1)

except Exception as e:
    print(f"Falha crítica ao inicializar banco de dados: {e}")
    sys.exit(1)


# Loop principal
if __name__ == "__main__":
    while True:
        try:
            limpar_tela()
            mostrar_cabecalho()
            mostrar_menu_principal()
            
            opcao = input(f"\n{Cores.NEGRITO}Escolha uma opção (1-5): {Cores.RESET}").strip()
            
            if opcao == '1':
                limpar_tela()
                janela1.mostrar_janela1(database.name)
                
            elif opcao == '2':  # Opção de consultar pedidos
                limpar_tela()
                janela1.consultar_pedidos(database.name)
                
            elif opcao == '3':
                gerar_relatorio(database.name)
                
            elif opcao == '4':
                gerenciar_cardapio(database.name)
                
            elif opcao == '5':
                confirmar = input(f"{Cores.VERMELHO}Tem certeza que deseja sair? (S/N): {Cores.RESET}").lower()
                if confirmar == 's':
                    print(f"\n{Cores.AZUL}Encerrando sistema...{Cores.RESET}")
                    break
                    
            else:
                print(f"\n{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                time.sleep(1)
                
        except Exception as e:
            print(f"\n{Cores.VERMELHO}Erro: {str(e)}{Cores.RESET}")
            input(f"{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")