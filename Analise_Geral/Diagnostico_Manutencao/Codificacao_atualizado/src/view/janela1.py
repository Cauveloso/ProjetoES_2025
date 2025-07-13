from datetime import date
import time
import sys
import os
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from model.pedido import Pedido
from controler.pedido_controler import PedidoControler
from controler.item_controler import ItemControler

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
    """Limpa a tela do console de forma multiplataforma"""
    os.system('cls' if os.name == 'nt' else 'clear')

class janela1:
    
    @staticmethod
    def formatar_cardapio(itens: list, modo_remocao: bool = False) -> str:
        """Formata a exibição do cardápio"""
        cabecalho = f"{Cores.FUNDO_AZUL}{Cores.NEGRITO} {'CÓD':<5} | {'NOME':<20} | {'PREÇO':<10} | {'TIPO':<10} | {'INGREDIENTES'}{Cores.RESET}"
        divisor = f"{Cores.AZUL}{'-'*5}+{'-'*22}+{'-'*12}+{'-'*12}+{'-'*30}{Cores.RESET}"
        linhas = [cabecalho, divisor]
        
        for item in itens:
            cod, nome, preco, tipo, ingredientes = item
            cor_cod = Cores.VERMELHO if modo_remocao else Cores.VERDE
            linha = (f" {cor_cod}{cod:<5}{Cores.RESET} | {Cores.CIANO}{nome:<20}{Cores.RESET} | "
                     f"{Cores.AMARELO}R${preco:<8.2f}{Cores.RESET} | {tipo:<10} | {ingredientes}")
            linhas.append(linha)
        
        return '\n'.join(linhas)
    
    @staticmethod
    def mostrar_janela1(database_name: str) -> None:
        """Interface para cadastro de pedidos"""
        while True:
            limpar_tela()
            itens_menu = ItemControler.mostrar_itens_menu(database_name)
            
            print(f'\n{Cores.FUNDO_VERDE}{Cores.NEGRITO} CARDÁPIO DISPONÍVEL {Cores.RESET}\n')
            print(janela1.formatar_cardapio(itens_menu))
            print('\n')
            
            opcao = input(f'{Cores.VERDE}Deseja cadastrar um novo pedido? (S/N): {Cores.RESET}').lower()
            if opcao not in ('s', 'sim'):
                break
                
            pedido_info = janela1.processar_pedido(database_name, itens_menu)
            if not pedido_info:
                continue
                
            janela1.confirmar_pedido(database_name, *pedido_info)
    
    @staticmethod
    def consultar_pedidos(database_name: str) -> None:
        """Interface para consulta e gerenciamento de pedidos"""
        while True:
            limpar_tela()
            print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} GERENCIAMENTO DE PEDIDOS {Cores.RESET}\n')
            
            pedidos = PedidoControler.search_in_pedidos_all(database_name)
            
            if not pedidos:
                print(f'{Cores.AMARELO}Não há pedidos cadastrados no sistema.{Cores.RESET}')
                input(f'\n{Cores.AZUL}Pressione Enter para voltar...{Cores.RESET}')
                return
                
            print(f'{Cores.VERDE}Total de pedidos encontrados: {len(pedidos)}{Cores.RESET}\n')
            
            for pedido in pedidos:
                if not isinstance(pedido, dict):
                    continue
                    
                print(f'{Cores.CIANO}Pedido ID: {pedido.get("id", "N/A")}{Cores.RESET}')
                print(f'Status: {pedido.get("status", "N/A")}')
                print(f'Data: {pedido.get("data", "N/A")}')
                print(f'Valor Total: R${pedido.get("valor_total", 0):.2f}')
                print(f'{Cores.AZUL}{"-"*30}{Cores.RESET}')
            
            print(f'\n{Cores.NEGRITO}Opções:{Cores.RESET}')
            print(f'{Cores.VERDE}1. Detalhar pedido{Cores.RESET}')
            print(f'{Cores.VERMELHO}2. Remover pedido{Cores.RESET}')
            print(f'{Cores.VERMELHO}3. Remover TODOS os pedidos{Cores.RESET}')
            print(f'{Cores.AZUL}4. Voltar{Cores.RESET}')
            
            opcao = input(f'\n{Cores.NEGRITO}Escolha (1-4): {Cores.RESET}').strip()
            
            if opcao == '1':
                janela1.detalhar_pedido(database_name)
            elif opcao == '2':
                janela1.remover_pedido_individual(database_name, pedidos)
            elif opcao == '3':
                janela1.remover_todos_pedidos(database_name)
            elif opcao == '4':
                break
            else:
                print(f'{Cores.VERMELHO}Opção inválida!{Cores.RESET}')
                time.sleep(1)
    
    @staticmethod
    def detalhar_pedido(database_name: str) -> None:
        """Mostra detalhes completos de um pedido específico"""
        try:
            pedido_id = int(input(f'\n{Cores.VERDE}Digite o ID do pedido: {Cores.RESET}'))
            
            pedido = PedidoControler.search_in_pedidos_id(database_name, pedido_id)
            if not pedido or not isinstance(pedido, dict):
                print(f'{Cores.VERMELHO}Pedido não encontrado!{Cores.RESET}')
                time.sleep(1)
                return
            
            itens = ItemControler.search_into_itens_pedidos_id(database_name, pedido_id)
            
            limpar_tela()
            print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} DETALHES DO PEDIDO Nº {pedido_id} {Cores.RESET}\n')
            print(f'{Cores.NEGRITO}Status:{Cores.RESET} {pedido.get("status", "N/A")}')
            print(f'{Cores.NEGRITO}Tipo:{Cores.RESET} {"Delivery" if pedido.get("delivery") == "True" else "Retirada"}')
            print(f'{Cores.NEGRITO}Endereço:{Cores.RESET} {pedido.get("endereco", "N/A")}')
            print(f'{Cores.NEGRITO}Data:{Cores.RESET} {pedido.get("data", "N/A")}')
            print(f'\n{Cores.NEGRITO}Itens:{Cores.RESET}')
            
            total = 0
            for item in itens:
                print(f' - {item[1]} (R${item[2]:.2f})')
                total += item[2]
            
            print(f'\n{Cores.NEGRITO}Total:{Cores.RESET} {Cores.VERDE}R${total:.2f}{Cores.RESET}')
            input(f'\n{Cores.AZUL}Pressione Enter para voltar...{Cores.RESET}')
            
        except ValueError:
            print(f'{Cores.VERMELHO}ID inválido!{Cores.RESET}')
            time.sleep(1)
    
    @staticmethod
    def remover_pedido_individual(database_name: str, pedidos: list) -> None:
        """Remove um pedido específico"""
        try:
            pedido_id = int(input(f'\n{Cores.VERMELHO}Digite o ID do pedido a remover: {Cores.RESET}'))
            
            if not any(p.get("id") == pedido_id for p in pedidos if isinstance(p, dict)):
                print(f'{Cores.VERMELHO}Pedido não encontrado!{Cores.RESET}')
                time.sleep(1)
                return
                
            confirmar = input(f'{Cores.VERMELHO}Tem certeza? (S/N): {Cores.RESET}').lower()
            if confirmar == 's':
                if PedidoControler.remover_pedido(database_name, pedido_id):
                    print(f'{Cores.VERDE}Pedido {pedido_id} removido!{Cores.RESET}')
                else:
                    print(f'{Cores.VERMELHO}Falha ao remover pedido!{Cores.RESET}')
                time.sleep(1.5)
            
        except ValueError:
            print(f'{Cores.VERMELHO}ID inválido! Digite apenas números.{Cores.RESET}')
            time.sleep(1)
    
    @staticmethod
    def remover_todos_pedidos(database_name: str) -> None:
        """Remove todos os pedidos"""
        confirmar = input(f'{Cores.VERMELHO}Tem CERTEZA ABSOLUTA que deseja remover TODOS os pedidos? (S/N): {Cores.RESET}').lower()
        if confirmar == 's':
            if PedidoControler.limpar_todos_pedidos(database_name):
                print(f'{Cores.VERDE}Todos os pedidos foram removidos!{Cores.RESET}')
            else:
                print(f'{Cores.VERMELHO}Falha ao remover pedidos!{Cores.RESET}')
            time.sleep(1.5)
    
    @staticmethod
    def processar_pedido(database_name: str, itens_menu: list) -> tuple:
        """Processa os itens do pedido"""
        pedidos = PedidoControler.search_in_pedidos_all(database_name)
        numero_pedido = len(pedidos) + 1
        lista_itens = []
        valor_total = 0
        
        while True:
            limpar_tela()
            print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} NOVO PEDIDO - Nº {numero_pedido} {Cores.RESET}\n')
            print(janela1.formatar_cardapio(itens_menu))
            
            try:
                item_id = int(input(f'\n{Cores.NEGRITO}Digite o CÓDIGO do item (ou 0 para finalizar): {Cores.RESET}'))
                if item_id == 0:
                    break
                    
                if item_id not in [i[0] for i in itens_menu]:
                    print(f'{Cores.VERMELHO}❌ Código inválido!{Cores.RESET}')
                    time.sleep(1)
                    continue
                    
                quantidade = int(input(f'{Cores.NEGRITO}Quantidade: {Cores.RESET}'))
                valor_item = next((i[2] for i in itens_menu if i[0] == item_id), 0)
                subtotal = valor_item * quantidade
                valor_total += subtotal
                
                print(f'{Cores.VERDE}Subtotal: R${subtotal:.2f}{Cores.RESET}')
                lista_itens.extend([(numero_pedido, item_id) for _ in range(quantidade)])
                
            except ValueError:
                print(f'{Cores.VERMELHO}❌ Entrada inválida!{Cores.RESET}')
                time.sleep(1)
        
        if not lista_itens:
            return None
            
        # Obter informações de entrega
        delivery = input(f'\n{Cores.NEGRITO}Delivery (S/N): {Cores.RESET}').lower() in ('s', 'sim')
        endereco = input(f'{Cores.NEGRITO}Endereço: {Cores.RESET}') if delivery else 'Retirada no local'
        
        # Status do pedido
        status_opcoes = {1: 'preparo', 2: 'pronto', 3: 'entregue'}
        while True:
            try:
                status = int(input(f'{Cores.NEGRITO}Status (1-Preparo, 2-Pronto, 3-Entregue): {Cores.RESET}'))
                if status in status_opcoes:
                    break
            except ValueError:
                pass
            print(f'{Cores.VERMELHO}Opção inválida!{Cores.RESET}')
        
        return (numero_pedido, status_opcoes[status], delivery, endereco, valor_total, lista_itens)
    
    @staticmethod
    def confirmar_pedido(database_name: str, numero_pedido: int, status: str, 
                        delivery: bool, endereco: str, valor_total: float, lista_itens: list):
        """Confirma e salva o pedido"""
        limpar_tela()
        data_hoje = date.today().strftime('%d/%m/%Y')
        
        print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} RESUMO DO PEDIDO Nº {numero_pedido} {Cores.RESET}\n')
        print(f'{Cores.NEGRITO}Data:{Cores.RESET} {data_hoje}')
        print(f'{Cores.NEGRITO}Status:{Cores.RESET} {status}')
        print(f'{Cores.NEGRITO}Tipo:{Cores.RESET} {"Delivery" if delivery else "Retirada"}')
        print(f'{Cores.NEGRITO}Endereço:{Cores.RESET} {endereco}')
        print(f'{Cores.NEGRITO}Valor Total:{Cores.RESET} {Cores.VERDE}R${valor_total:.2f}{Cores.RESET}')
        
        confirmar = input(f'\n{Cores.VERDE}Confirmar pedido? (S/N): {Cores.RESET}').lower()
        if confirmar in ('s', 'sim'):
            pedido = Pedido(status, str(delivery), endereco, data_hoje, valor_total)
            PedidoControler.insert_into_pedidos(database_name, pedido)
            for item in lista_itens:
                ItemControler.insert_into_itens_pedidos(database_name, item)
            print(f'\n{Cores.VERDE}✅ Pedido {numero_pedido} cadastrado com sucesso!{Cores.RESET}')
        else:
            print(f'\n{Cores.AMARELO}❌ Pedido cancelado!{Cores.RESET}')
        
        input(f'\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}')