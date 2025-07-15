#para pegar a data de hoje
from datetime import date
import time

#Necessário para realizar import em python
import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

#importando os módulos de model
from model.pedido import Pedido

#importando os módulos de controle
from controler.pedidoControler import PedidoControler
from controler.itemControler import ItemControler

#criação da classe janela
class Janela1:
    
    @staticmethod
    def mostrar_janela1(database_name: str) -> None:
        """
        View para o usuário utilizar o software
        
        return None
        """
        
        # SOLUÇÃO Nº 1 (Perfectiva): Melhorando a exibição do menu.
        menu_itens = ItemControler.mostrar_itens_menu(database_name)
        print('\n-------------------- Menu --------------------')
        print(f'{"ID":<5}| {"Nome":<20}| {"Preço":<10}| {"Tipo":<15}')
        print('-' * 55)
        for item in menu_itens:
            print(f'{item[0]:<5}| {item[1]:<20}| R$ {item[2]:<7.2f}| {item[3]:<15}')
        print('-' * 55)

        # Loop principal para controlar o fluxo de cadastro
        while True:
            # SOLUÇÃO Nº 2 (Corretiva): Validação de entrada robusta para 'sim'/'não'
            # Lista de possíveis respostas afirmativas
            respostas_positivas = ['s', 'sim']
            # Lista de possíveis respostas negativas (agora incluindo a versão com acento)
            respostas_negativas = ['n', 'nao', 'não']
            # Trata a entrada do usuário: remove espaços, converte para minúsculas e normaliza (remove acentos)
            # A normalização não é nativa, mas a lógica de verificação cobre isso
            entrada_usuario = str(input('Deseja cadastrar um novo pedido? (s-Sim / n-Não): ')).lower().strip()
            
            # --- Bloco IF: Se o usuário quer cadastrar ---
            if entrada_usuario in respostas_positivas:
                print('----------Cadastrar pedido----------\n')
                
                lista_itens = []
                valor_total = 0
                adicionar = 's'
                pedidos = PedidoControler.search_in_pedidos_all(database_name)
                numero_pedido = len(pedidos) + 1
                
                # Loop para adicionar itens ao pedido
                while adicionar == 's':
                    while True:
                        try:
                            item = int(input('Numero do item: '))
                            quantidade = int(input('Quantidade: '))
                            break # Sai deste loop interno se as duas entradas forem números
                        except ValueError:
                            print("Entrada inválida! Por favor, digite apenas NÚMEROS para o item e a quantidade.")
                    
                    a = ItemControler.valor_item(database_name, item)
                    b = a[0][0] * quantidade
                    valor_total += b
                    
                    for x in range(quantidade):
                        lista_itens.append((numero_pedido, item))
                    
                    # Validação para adicionar mais itens
                    while True:
                        adicionar_input = str(input('Adicionar novo item? (s-Sim, n-Nao): ')).lower().strip()
                        if adicionar_input in respostas_positivas:
                            adicionar = 's'
                            break
                        elif adicionar_input in respostas_negativas:
                            adicionar = 'n'
                            break
                        else:
                            print('Resposta inválida! Digite "s" para Sim ou "n" para Não.')
                
                # Finalização do pedido
                print('\n----------Finalizar pedido----------\n')
                print(f'Numero do pedido: {numero_pedido}')
                delivery = str(input('Delivery (S/N): ')).lower()
                if delivery == 's':
                    delivery = True
                elif delivery == 'n':
                    delivery = False
                else:
                    print('Valor incorreto, recomeçando')
                    continue # Volta para o início do while True principal
                    
                endereco = str(input('Endereco:'))
                while True:
                    try:
                        status_aux = int(input('status: 1-preparo, 2-pronto, 3-entregue: '))
                        if status_aux == 1:
                            status = 'preparo'
                            break
                        elif status_aux == 2:
                            status = 'pronto'
                            break
                        elif status_aux == 3:
                            status = 'entregue'
                            break
                        else:
                            print('Opção inválida! Digite apenas 1, 2 ou 3.')
                    except ValueError:
                        print('Entrada inválida! Digite apenas números (1, 2 ou 3).')
 
                print(f'Valor Final: R${valor_total}')
                data_hoje = date.today()
                data_formatada = data_hoje.strftime('%d/%m/%Y')
                
                pedido = Pedido(status, str(delivery), endereco, data_formatada, float(valor_total))
                PedidoControler.insert_into_pedidos(database_name, pedido)
                for elem in lista_itens:
                    ItemControler.insert_into_itens_pedidos(database_name, elem)
                print("Pedido cadastrado com sucesso!")

            # --- Bloco ELIF: Se o usuário NÃO quer cadastrar ---
            elif entrada_usuario in respostas_negativas:
                print('Voltando ao Menu inicial...')
                time.sleep(1)
                break # Encerra o loop e finaliza a função

            # --- Bloco ELSE: Se a entrada foi inválida ---
            else:
                print('Resposta inválida! Por favor, digite "s" para Sim ou "n" para Não.')
