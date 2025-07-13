from datetime import datetime
import time
import sys
import os
from pathlib import Path

# Configuração de imports relativos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Importações do projeto
from model.pedido import Pedido
from controler.pedido_controler import PedidoControler
from controler.item_controler import ItemControler
from controler.database_controler import DatabaseControler

# ==============================================
# CONFIGURAÇÃO DE CORES PARA O TERMINAL
# ==============================================
class Cores:
    """Armazena códigos de cores ANSI para formatação de terminal"""
    VERDE = '\033[92m'      # Mensagens de sucesso
    AMARELO = '\033[93m'    # Avisos/relatórios
    VERMELHO = '\033[91m'   # Erros/destaques importantes
    AZUL = '\033[94m'       # Títulos/menus
    CIANO = '\033[96m'      # Informações secundárias
    RESET = '\033[0m'       # Resetar formatação
    NEGRITO = '\033[1m'     # Texto em negrito
    FUNDO_AZUL = '\033[44m' # Fundo azul
    FUNDO_VERDE = '\033[42m'# Fundo verde

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================
def limpar_tela():
    """Limpa o conteúdo do terminal de forma multiplataforma"""
    os.system('cls' if os.name == 'nt' else 'clear')

# ==============================================
# CLASSE PRINCIPAL DA JANELA DE PEDIDOS
# ==============================================
class janela1:
    
    @staticmethod
    def formatar_cardapio(itens: list, modo_remocao: bool = False) -> str:
        """
        Formata a exibição do cardápio com cores e alinhamento
        
        Args:
            itens: Lista de itens do cardápio
            modo_remocao: Se True, destaca códigos em vermelho
            
        Returns:
            String formatada com o cardápio
        """
        # Cabeçalho da tabela
        cabecalho = (f"{Cores.FUNDO_AZUL}{Cores.NEGRITO} {'CÓD':<5} | {'NOME':<20} | "
                    f"{'PREÇO':<10} | {'TIPO':<10} | {'INGREDIENTES'}{Cores.RESET}")
        
        # Linha divisória
        divisor = f"{Cores.AZUL}{'-'*5}+{'-'*22}+{'-'*12}+{'-'*12}+{'-'*30}{Cores.RESET}"
        
        linhas = [cabecalho, divisor]
        
        # Adiciona cada item formatado
        for item in itens:
            cod, nome, preco, tipo, ingredientes = item
            cor_cod = Cores.VERMELHO if modo_remocao else Cores.VERDE
            linha = (f" {cor_cod}{cod:<5}{Cores.RESET} | {Cores.CIANO}{nome:<20}{Cores.RESET} | "
                    f"{Cores.AMARELO}R${preco:<8.2f}{Cores.RESET} | {tipo:<10} | {ingredientes}")
            linhas.append(linha)
        
        return '\n'.join(linhas)
    
    # ==============================================
    # MÉTODOS PRINCIPAIS DE INTERFACE
    # ==============================================
    
    @staticmethod
    def mostrar_janela1(database_name: str) -> None:
        """Interface principal para cadastro de novos pedidos"""
        while True:
            limpar_tela()
            
            # 1. Mostrar cardápio disponível
            itens_menu = ItemControler.mostrar_itens_menu(database_name)
            print(f'\n{Cores.FUNDO_VERDE}{Cores.NEGRITO} CARDÁPIO DISPONÍVEL {Cores.RESET}\n')
            print(janela1.formatar_cardapio(itens_menu))
            print('\n')
            
            # 2. Perguntar se deseja cadastrar novo pedido
            opcao = input(f'{Cores.VERDE}Deseja cadastrar um novo pedido? (S/N): {Cores.RESET}').lower()
            if opcao not in ('s', 'sim'):
                break
                
            # 3. Processar novo pedido
            pedido_info = janela1.processar_pedido(database_name, itens_menu)
            if not pedido_info:
                continue
                
            # 4. Confirmar e salvar pedido
            janela1.confirmar_pedido(database_name, *pedido_info)

    @staticmethod
    def consultar_pedidos(database_name: str) -> None:
        """Interface para consulta e gerenciamento de pedidos"""
        while True:
            limpar_tela()
            print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} GERENCIAMENTO DE PEDIDOS {Cores.RESET}\n')
            
            # 1. Buscar todos os pedidos
            pedidos = PedidoControler.search_in_pedidos_all(database_name)
            
            # 2. Verificar se existem pedidos
            if not pedidos:
                print(f'{Cores.AMARELO}Não há pedidos cadastrados no sistema.{Cores.RESET}')
                input(f'\n{Cores.AZUL}Pressione Enter para voltar...{Cores.RESET}')
                return
                
            # 3. Mostrar resumo dos pedidos
            print(f'{Cores.VERDE}Total de pedidos encontrados: {len(pedidos)}{Cores.RESET}\n')
            
            for pedido in pedidos:
                if not isinstance(pedido, dict):
                    continue
                    
                valor_total = pedido.get('total') or pedido.get('valor_total') or 0.0
                
                print(f'{Cores.CIANO}Pedido ID: {pedido.get("id", "N/A")}{Cores.RESET}')
                print(f'Status: {pedido.get("status", "N/A")}')
                print(f'Data: {pedido.get("data", "N/A")}')
                print(f'Total: {Cores.VERDE}R${float(valor_total):.2f}{Cores.RESET}')
                print(f'{Cores.AZUL}{"-"*30}{Cores.RESET}')
            
            # 4. Mostrar opções de gerenciamento
            print(f'\n{Cores.NEGRITO}Opções:{Cores.RESET}')
            print(f'{Cores.VERDE}1. Detalhar pedido{Cores.RESET}')
            print(f'{Cores.VERMELHO}2. Remover pedido{Cores.RESET}')
            print(f'{Cores.VERMELHO}3. Remover TODOS os pedidos{Cores.RESET}')
            print(f'{Cores.AZUL}4. Voltar{Cores.RESET}')
            print(f'{Cores.AMARELO}9. Diagnóstico (para desenvolvedores){Cores.RESET}')
            
            # 5. Processar escolha do usuário
            opcao = input(f'\n{Cores.NEGRITO}Escolha (1-4): {Cores.RESET}').strip()
            
            if opcao == '1':
                janela1.detalhar_pedido(database_name)
            elif opcao == '2':
                janela1.remover_pedido_individual(database_name, pedidos)
            elif opcao == '3':
                janela1.remover_todos_pedidos(database_name)
            elif opcao == '4':
                break
            elif opcao == '9':
                DatabaseControler.diagnosticar_pedidos(database_name)
                input("Pressione Enter para continuar...")
            else:
                print(f'{Cores.VERMELHO}Opção inválida!{Cores.RESET}')
                time.sleep(1)

    # ==============================================
    # MÉTODOS DE DETALHAMENTO DE PEDIDOS
    # ==============================================
    
    @staticmethod
    def detalhar_pedido(database_name: str) -> None:
        """Mostra detalhes completos de um pedido específico"""
        try:
            # 1. Obter ID do pedido
            pedido_id = int(input(f'\n{Cores.VERDE}Digite o ID do pedido: {Cores.RESET}'))
            
            # 2. Buscar pedido no banco de dados
            pedido = PedidoControler.search_in_pedidos_id(database_name, pedido_id, incluir_entregues=True)
            
            if not pedido or not isinstance(pedido, dict):
                print(f'{Cores.VERMELHO}Pedido não encontrado!{Cores.RESET}')
                time.sleep(1)
                return
            
            # 3. Buscar itens do pedido
            itens = ItemControler.search_into_itens_pedidos_id(database_name, pedido_id)
            
            while True:
                limpar_tela()
                print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} DETALHES DO PEDIDO Nº {pedido_id} {Cores.RESET}\n')
                
                # 4. Mostrar informações básicas do pedido
                print(f'{Cores.NEGRITO}Status atual:{Cores.RESET} {Cores.CIANO}{pedido.get("status", "N/A").upper()}{Cores.RESET}')
                print(f'{Cores.NEGRITO}Cliente:{Cores.RESET} {pedido.get("cliente", "N/A")}')
                print(f'{Cores.NEGRITO}Tipo:{Cores.RESET} {"Delivery" if pedido.get("delivery") else "Retirada"}')
                print(f'{Cores.NEGRITO}Endereço:{Cores.RESET} {pedido.get("endereco_entrega", "N/A")}')
                print(f'{Cores.NEGRITO}Data:{Cores.RESET} {pedido.get("data", "N/A")}')
                print(f'\n{Cores.NEGRITO}Itens:{Cores.RESET}')
                
                # 5. Calcular e mostrar itens com totais
                total = 0
                for item in itens:
                    try:
                        nome_item = ItemControler.get_item_name(database_name, item[1])
                        print(f' - {nome_item} x{item[2]} (R${item[3]:.2f} cada) = R${item[2] * item[3]:.2f}')
                        total += item[2] * item[3]
                    except Exception:
                        print(f' - Item ID {item[1]} (erro ao carregar detalhes)')
                        continue
                
                print(f'\n{Cores.NEGRITO}Total do Pedido:{Cores.RESET} {Cores.VERDE}R${total:.2f}{Cores.RESET}')
                
                # 6. Mostrar opções de status
                print(f'\n{Cores.NEGRITO}OPÇÕES:{Cores.RESET}')
                print(f'{Cores.AMARELO}1. Marcar como PRONTO{Cores.RESET}')
                print(f'{Cores.VERDE}2. Marcar como ENTREGUE{Cores.RESET}')
                print(f'{Cores.VERMELHO}3. Voltar{Cores.RESET}')
                
                # 7. Processar escolha do usuário
                opcao = input(f'\n{Cores.NEGRITO}Escolha uma opção (1-3): {Cores.RESET}').strip()
                
                if opcao == '1':
                    novo_status = "pronto"
                elif opcao == '2':
                    novo_status = "entregue"
                elif opcao == '3':
                    break
                else:
                    print(f'{Cores.VERMELHO}Opção inválida!{Cores.RESET}')
                    time.sleep(1)
                    continue
                
                # 8. Atualizar status se necessário
                if PedidoControler.atualizar_status_pedido(database_name, pedido_id, novo_status):
                    print(f'\n{Cores.VERDE}✅ Status alterado para {novo_status.upper()}!{Cores.RESET}')
                    pedido['status'] = novo_status
                    time.sleep(1)
                else:
                    print(f'\n{Cores.VERMELHO}❌ Falha ao atualizar status!{Cores.RESET}')
                    time.sleep(1)
                    
        except ValueError:
            print(f'{Cores.VERMELHO}ID inválido!{Cores.RESET}')
            time.sleep(1)

    # ==============================================
    # MÉTODOS DE REMOÇÃO DE PEDIDOS
    # ==============================================
    
    @staticmethod
    def remover_pedido_individual(database_name: str, pedidos: list) -> None:
        """Remove um pedido específico após confirmação"""
        try:
            # 1. Obter ID do pedido a remover
            pedido_id = int(input(f'\n{Cores.VERMELHO}Digite o ID do pedido a remover: {Cores.RESET}'))
            
            # 2. Verificar se pedido existe
            if not any(p.get("id") == pedido_id for p in pedidos if isinstance(p, dict)):
                print(f'{Cores.VERMELHO}Pedido não encontrado!{Cores.RESET}')
                time.sleep(1)
                return
                
            # 3. Confirmar remoção
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
        """Remove todos os pedidos após confirmação explícita"""
        # 1. Confirmar remoção total
        confirmar = input(f'{Cores.VERMELHO}Tem CERTEZA ABSOLUTA que deseja remover TODOS os pedidos? (S/N): {Cores.RESET}').lower()
        if confirmar == 's':
            # 2. Executar remoção
            if PedidoControler.limpar_todos_pedidos(database_name):
                print(f'{Cores.VERDE}Todos os pedidos foram removidos!{Cores.RESET}')
            else:
                print(f'{Cores.VERMELHO}Falha ao remover pedidos!{Cores.RESET}')
            time.sleep(1.5)

    # ==============================================
    # MÉTODOS DE PROCESSAMENTO DE PEDIDOS
    # ==============================================
    
    @staticmethod
    def processar_pedido(database_name: str, itens_menu: list) -> tuple:
        """
        Coleta informações para um novo pedido
        
        Args:
            database_name: Nome do banco de dados
            itens_menu: Lista de itens disponíveis
            
        Returns:
            Tupla com todas as informações do pedido ou None se cancelado
        """
        itens_pedido = []
        valor_total = 0.0
        
        while True:
            limpar_tela()
            print(f'\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} NOVO PEDIDO {Cores.RESET}\n')
            print(janela1.formatar_cardapio(itens_menu))
            
            try:
                # 1. Selecionar item pelo código
                item_id = int(input(f'\n{Cores.NEGRITO}Digite o CÓDIGO do item (ou 0 para finalizar): {Cores.RESET}'))
                if item_id == 0:
                    break
                    
                # 2. Validar código do item
                item_info = next((i for i in itens_menu if i[0] == item_id), None)
                if not item_info:
                    print(f'{Cores.VERMELHO}❌ Código inválido!{Cores.RESET}')
                    time.sleep(1)
                    continue
                    
                # 3. Obter quantidade
                quantidade = int(input(f'{Cores.NEGRITO}Quantidade: {Cores.RESET}'))
                if quantidade <= 0:
                    print(f'{Cores.VERMELHO}❌ Quantidade deve ser maior que zero!{Cores.RESET}')
                    time.sleep(1)
                    continue
                    
                # 4. Calcular subtotal
                preco_unitario = item_info[2]
                subtotal = preco_unitario * quantidade
                valor_total += subtotal
                
                print(f'{Cores.VERDE}Subtotal: R${subtotal:.2f}{Cores.RESET}')
                print(f'{Cores.VERDE}Total acumulado: R${valor_total:.2f}{Cores.RESET}')
                
                # 5. Armazenar item do pedido
                itens_pedido.append({
                    'item_id': item_id,
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                    'observacoes': input(f'{Cores.NEGRITO}Observações (opcional): {Cores.RESET}').strip()
                })
                
            except ValueError:
                print(f'{Cores.VERMELHO}❌ Entrada inválida! Digite apenas números.{Cores.RESET}')
                time.sleep(1)
        
        # 6. Verificar se há itens no pedido
        if not itens_pedido:
            return None
            
        # 7. Coletar informações do cliente
        cliente = input(f'\n{Cores.NEGRITO}Nome do cliente: {Cores.RESET}').strip()
        while not cliente:
            print(f'{Cores.VERMELHO}O nome do cliente é obrigatório!{Cores.RESET}')
            cliente = input(f'{Cores.NEGRITO}Nome do cliente: {Cores.RESET}').strip()
        
        telefone = input(f'\n{Cores.NEGRITO}Telefone: {Cores.RESET}').strip()
        while not telefone:
            print(f'{Cores.VERMELHO}O telefone é obrigatório!{Cores.RESET}')
            telefone = input(f'{Cores.NEGRITO}Telefone: {Cores.RESET}').strip()
        
        # 8. Definir tipo de entrega
        delivery = input(f'{Cores.NEGRITO}Delivery (S/N): {Cores.RESET}').lower() in ('s', 'sim')
        endereco = input(f'{Cores.NEGRITO}Endereço: {Cores.RESET}').strip() if delivery else 'Retirada no local'
        
        # 9. Definir status inicial
        status_opcoes = {
            1: 'preparando',
            2: 'pronto',
            3: 'entregue'
        }
        
        while True:
            try:
                print(f'\n{Cores.NEGRITO}Status do pedido:{Cores.RESET}')
                print(f'1. Preparando\n2. Pronto\n3. Entregue')
                status = int(input(f'{Cores.NEGRITO}Escolha o status (1-3): {Cores.RESET}'))
                if status in status_opcoes:
                    status = status_opcoes[status]
                    break
                else:
                    print(f'{Cores.VERMELHO}Opção inválida! Escolha entre 1 e 3.{Cores.RESET}')
            except ValueError:
                print(f'{Cores.VERMELHO}Digite apenas números!{Cores.RESET}')
        
        # 10. Arredondar valor total
        valor_total = round(valor_total, 2)
        
        return (cliente, telefone, status, delivery, endereco, valor_total, itens_pedido)

    @staticmethod
    def confirmar_pedido(database_name: str, cliente: str, telefone: str, status: str, 
                        delivery: bool, endereco: str, valor_total: float, itens_pedido: list):
        """Salva o pedido no banco de dados com tratamento de erros"""
        try:
            # 1. Preparar dados do pedido principal
            pedido_data = {
                'cliente': cliente,
                'telefone': telefone,
                'data': datetime.now().isoformat(),
                'valor_total': valor_total,
                'status': status,
                'delivery': 1 if delivery else 0,
                'endereco': endereco,
                'observacoes': ''
            }
            
            # 2. Inserir pedido principal
            if not PedidoControler.insert_into_pedidos(database_name, pedido_data):
                raise Exception("Falha ao inserir pedido principal")
            
            # 3. Obter ID do novo pedido
            pedidos = PedidoControler.get_id_all(database_name)
            if not pedidos:
                raise Exception("Não foi possível obter ID do novo pedido")
            
            pedido_id = pedidos[0]
            
            # 4. Inserir itens do pedido
            for item in itens_pedido:
                item_data = {
                    'pedido_id': pedido_id,
                    'item_id': item['item_id'],
                    'quantidade': item['quantidade'],
                    'preco_unitario': item['preco_unitario'],
                    'observacoes': item.get('observacoes', '')
                }
                
                if not PedidoControler.inserir_item_pedido(database_name, item_data):
                    raise Exception(f"Falha ao inserir item {item['item_id']}")
            
            # 5. Confirmar sucesso
            print(f'\n{Cores.VERDE}✅ Pedido {pedido_id} registrado com sucesso!{Cores.RESET}')
            return True
            
        except Exception as e:
            print(f'\n{Cores.VERMELHO}❌ Erro ao confirmar pedido: {str(e)}{Cores.RESET}')
            return False
        finally:
            input(f'\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}')