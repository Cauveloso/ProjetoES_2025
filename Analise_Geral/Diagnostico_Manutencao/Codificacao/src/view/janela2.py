#Necessário para realizar import em python
import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from controler.pedidoControler import PedidoControler
from controler.itemControler import ItemControler

class Janela2:
    def mostrar_janela2(database_name:str):
        faturamento = 0
        print('------Pesquisar Pedido--------')
        q = int(input('Unico-1\nTodos-2\nAtualizar Estado-3\nDigite: '))
        if q==1:
            while True:
                try:
                    indice = int(input('Índice do pedido: '))
                    break # Se a conversão para int for bem-sucedida, sai do loop
                except ValueError:
                    print("Entrada inválida! Por favor, digite apenas o número do pedido.")

            # Primeiro, verifica se o pedido existe no banco de dados
            informacoes_pedido_list = PedidoControler.search_in_pedidos_id(database_name, indice)
            
            # Se a lista estiver vazia, o pedido não existe
            if not informacoes_pedido_list:
                print(f"\nPedido com o índice {indice} não existe.")
            else:
                resume = ItemControler.search_into_itens_pedidos_id(database_name, indice)
                informacoes_pedido = PedidoControler.search_in_pedidos_id(database_name,indice)[0]
                quantidade_itens = len(resume)
                exibir_tela = ''
                for elem in resume:
                    exibir_tela+=f'Tipo: {elem[2]}| Sabor: {elem[0]}| Descricao: {elem[3]}| R$ {elem[1]}|\n'
                print(f'\nResumo do pedido {indice}: \n {exibir_tela}\nItens: {quantidade_itens}\n\n')
                if len(informacoes_pedido)>0:
                    print(f'Status: {informacoes_pedido[1]}\nDelivery: {informacoes_pedido[2]}\nEndereco: {informacoes_pedido[3]}\nData: {informacoes_pedido[4]}\nR$ {informacoes_pedido[5]}')
            print('Voltando ao menu inicial\n')
            
        elif q==2:
            row = PedidoControler.search_in_pedidos_all(database_name)            
            faturamento = 0
            exibir_tela = ''
            endereco =''
            i=1
            for elem in row:
                endereco_raw = elem.endereco
                if isinstance(endereco_raw, (tuple, list)):
                    endereco_raw = endereco_raw[0]
                faturamento+=elem.valor_total
                endereco = endereco_raw or 'Nao informado'
                exibir_tela+= f'Nº: {i}| Estado: {elem.status}| Delivery: {elem.delivery}| Endereco: {endereco}| Valor: R$ {elem.valor_total} \n'
                i+=1
            print(f'\nPedidos \n\n{exibir_tela}')
            print(f'Faturamento R$ {faturamento}')
        
        elif q==3:
            while True:
                try:
                    indice = int(input('Índice do pedido: '))
                    break # Se a conversão para int for bem-sucedida, sai do loop
                except ValueError:
                    print("Entrada inválida! Por favor, digite apenas o número do pedido.")

            # Primeiro, verifica se o pedido existe no banco de dados
            informacoes_pedido_list = PedidoControler.search_in_pedidos_id(database_name, indice)
            
            # Se a lista estiver vazia, o pedido não existe
            if not informacoes_pedido_list:
                print(f"\nPedido com o índice {indice} não existe.")
            else:
                resume = ItemControler.search_into_itens_pedidos_id(database_name, indice)
                quantidade_itens = len(resume)
                exibir_tela = ''
                if quantidade_itens>0:
                    informacoes_pedido = PedidoControler.search_in_pedidos_id(database_name,indice)[0]

                    for elem in resume:
                        exibir_tela+=f'Tipo: {elem[2]}| Sabor: {elem[0]}| Descricao: {elem[3]}| R$ {elem[1]}|\n'
                    print(f'\nResumo do pedido {indice}: \n {exibir_tela}\nItens: {quantidade_itens}\n')
                    print('Informações do Pedido\n')
                    print(f'Status: {informacoes_pedido[1]}\nDelivery: {informacoes_pedido[2]}\nEndereco: {informacoes_pedido[3]}\nData: {informacoes_pedido[4]}\nR$ {informacoes_pedido[5]}')
                    
                    while True:
                        try:
                            novo_status = int(input('preparo - 1 | pronto - 2 | entregue - 3: '))
                            if novo_status in [1, 2, 3]:
                                result = PedidoControler.update_pedido_status_id(database_name, indice, novo_status)
                                if result:
                                    print(f'Status do Pedido {indice} atualizado com sucesso')
                                else:
                                    print('Erro ao atualizar o status.')
                                break  # Sai do loop após a tentativa de atualização
                            else:
                                print('Opção inválida! Digite apenas 1, 2 ou 3.')
                        except ValueError:
                            print('Entrada inválida! Digite apenas números (1, 2 ou 3).')
                else:
                    print('Indice inválido')    
        else:
            print('Entrada inválida, retornando')
            
       