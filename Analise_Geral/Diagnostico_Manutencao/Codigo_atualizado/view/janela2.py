from datetime import date
import time
import sys
import sqlite3
import json
import random
from pathlib import Path

# Configuração de imports relativos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Importações do projeto
from model.item import Item
from controler.item_controler import ItemControler
from view.janela1 import janela1, Cores

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================
def limpar_tela():
    """Limpa o conteúdo do terminal"""
    print("\n" * 50)

# ==============================================
# CLASSE PRINCIPAL DA JANELA DE GERENCIAMENTO
# ==============================================
class janela2:
    
    # ==============================================
    # MÉTODOS DE SUPORTE E AJUDA
    # ==============================================
    
    @staticmethod
    def menu_ajuda_suporte(database_name: str):
        """Interface principal para ajuda e suporte"""
        while True:
            limpar_tela()
            print(f'''
    {Cores.FUNDO_AZUL}{Cores.NEGRITO} MENU DE AJUDA E SUPORTE {Cores.RESET}
    
    {Cores.NEGRITO}Opções disponíveis:{Cores.RESET}
    {Cores.VERDE}1. Reportar um problema{Cores.RESET}
    {Cores.CIANO}2. Enviar sugestão de melhoria{Cores.RESET}
    {Cores.AMARELO}3. Verificar atualizações{Cores.RESET}
    {Cores.VERMELHO}4. Voltar ao menu principal{Cores.RESET}
            ''')
            
            opcao = input(f"\n{Cores.NEGRITO}Escolha uma opção (1-4): {Cores.RESET}").strip()
            
            if opcao == '1':
                janela2.enviar_feedback(database_name, tipo="problema")
            elif opcao == '2':
                janela2.enviar_feedback(database_name, tipo="sugestao")
            elif opcao == '3':
                janela2.verificar_atualizacoes()
            elif opcao == '4':
                break
            else:
                print(f"\n{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                time.sleep(1)

    @staticmethod
    def enviar_feedback(database_name: str, tipo: str):
        """
        Coleta e armazena feedback do usuário
        
        Args:
            database_name: Nome do banco de dados em uso
            tipo: Tipo de feedback ('problema' ou 'sugestao')
        """
        limpar_tela()
        print(f'''
    {Cores.FUNDO_AZUL}{Cores.NEGRITO} ENVIAR {tipo.upper()} {Cores.RESET}
    
    {Cores.NEGRITO}Por favor, descreva com detalhes:{Cores.RESET}
    {Cores.AMARELO}• Para problemas: inclua os passos para reproduzir{Cores.RESET}
    {Cores.AMARELO}• Para sugestões: descreva sua ideia{Cores.RESET}
    ''')
        
        # 1. Coletar descrição do feedback
        descricao = input(f"{Cores.CIANO}Descreva aqui:\n{Cores.RESET}").strip()
        if not descricao:
            print(f"\n{Cores.VERMELHO}A descrição não pode estar vazia!{Cores.RESET}")
            time.sleep(1)
            return
        
        # 2. Preparar dados do feedback
        feedback_data = {
            'tipo': tipo,
            'descricao': descricao,
            'data': time.strftime("%Y-%m-%d %H:%M:%S"),
            'sistema': f"Python {sys.version.split()[0]}",
            'database': database_name
        }
        
        try:
            # 3. Salvar feedback em arquivo JSON
            feedback_file = Path('feedback_sistema.json')
            feedbacks = []
            
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            
            feedbacks.append(feedback_data)
            
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, indent=4, ensure_ascii=False)
            
            print(f"\n{Cores.VERDE}✅ {tipo.capitalize()} enviado com sucesso! Obrigado pelo feedback.{Cores.RESET}")
        except Exception as e:
            print(f"\n{Cores.VERMELHO}❌ Erro ao enviar {tipo}: {str(e)}{Cores.RESET}")
        
        input(f"\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")

    @staticmethod
    def verificar_atualizacoes():
        """Simula verificação de atualizações disponíveis"""
        limpar_tela()
        print(f'''
    {Cores.FUNDO_AZUL}{Cores.NEGRITO} VERIFICAR ATUALIZAÇÕES {Cores.RESET}
    
    {Cores.CIANO}Versão atual do sistema: 1.0.0{Cores.RESET}
    {Cores.AMARELO}Verificando atualizações disponíveis...{Cores.RESET}
    ''')
        
        time.sleep(2)  # Simulação de tempo de verificação
        
        # Simulação aleatória de atualização disponível (30% de chance)
        if random.random() < 0.3:
            print(f'''
    {Cores.VERDE}✅ Nova versão disponível: 1.1.0{Cores.RESET}
    {Cores.CIANO}O que há de novo:
    • Correção de bugs críticos
    • Melhorias de desempenho
    • Novas funcionalidades no menu de relatórios{Cores.RESET}
            ''')
        else:
            print(f"\n{Cores.VERDE}✅ Seu sistema está atualizado!{Cores.RESET}")
        
        input(f"\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")

    # ==============================================
    # MÉTODOS DE GERENCIAMENTO DE CARDÁPIO
    # ==============================================
    
    @staticmethod
    def inserir_item_menu(database_name: str):
        """Interface para adicionar novos itens ao cardápio"""
        while True:
            limpar_tela()
            print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} ADICIONAR ITEM AO CARDÁPIO {Cores.RESET}\n")
            
            # 1. Coletar informações do novo item
            nome = input(f"{Cores.VERDE}Nome do item: {Cores.RESET}").strip()
            if not nome:
                print(f"{Cores.VERMELHO}O nome não pode ser vazio!{Cores.RESET}")
                time.sleep(1)
                continue
                
            # 2. Validar preço
            try:
                preco = float(input(f"{Cores.VERDE}Preço (ex: 35.50): R$ {Cores.RESET}"))
                if preco <= 0:
                    raise ValueError
            except ValueError:
                print(f"{Cores.VERMELHO}Preço inválido!{Cores.RESET}")
                time.sleep(1)
                continue
                
            # 3. Coletar tipo e ingredientes
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
                
            # 4. Confirmar dados
            print(f"\n{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
            print(f"{Cores.NEGRITO}CONFIRME OS DADOS:{Cores.RESET}")
            print(f"{Cores.VERDE}Nome: {Cores.CIANO}{nome}{Cores.RESET}")
            print(f"{Cores.VERDE}Preço: {Cores.AMARELO}R${preco:.2f}{Cores.RESET}")
            print(f"{Cores.VERDE}Tipo: {Cores.CIANO}{tipo}{Cores.RESET}")
            print(f"{Cores.VERDE}Ingredientes: {Cores.CIANO}{ingredientes}{Cores.RESET}")
            print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
            
            # 5. Inserir no banco de dados
            confirmar = input(f"\n{Cores.VERDE}Confirmar inclusão? (S/N): {Cores.RESET}").lower()
            if confirmar == 's' or confirmar == "sim":
                novo_item = Item(nome, preco, tipo, ingredientes)
                if ItemControler.insert_into_item(database_name, novo_item):
                    print(f"\n{Cores.VERDE}✅ Item adicionado com sucesso!{Cores.RESET}")
                else:
                    print(f"\n{Cores.VERMELHO}❌ Erro ao adicionar item!{Cores.RESET}")
            
            # 6. Perguntar se deseja adicionar outro item
            continuar = input(f"\n{Cores.VERDE}Adicionar outro item? (S/N): {Cores.RESET}").lower()
            if continuar != 's':
                break

    @staticmethod
    def remover_item_menu(database_name: str):
        """Interface para remover itens do cardápio"""
        while True:
            limpar_tela()
            print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} REMOVER ITEM DO CARDÁPIO {Cores.RESET}\n")
            
            # 1. Buscar itens disponíveis
            itens = ItemControler.mostrar_itens_menu(database_name)
            if not itens:
                print(f"{Cores.AMARELO}Não há itens no cardápio.{Cores.RESET}")
                time.sleep(2)
                break
                
            # 2. Mostrar cardápio formatado
            print(janela1.formatar_cardapio(itens, modo_remocao=True))
            
            try:
                # 3. Selecionar item para remoção
                codigo = int(input(f"\n{Cores.VERDE}Digite o CÓDIGO do item a remover (0 para cancelar): {Cores.RESET}"))
                if codigo == 0:
                    break
                    
                # 4. Validar código do item
                if codigo not in [i[0] for i in itens]:
                    print(f"{Cores.VERMELHO}❌ Código inválido!{Cores.RESET}")
                    time.sleep(1)
                    continue
                    
                # 5. Mostrar detalhes do item selecionado
                item = next((i for i in itens if i[0] == codigo), None)
                print(f"\n{Cores.VERMELHO}Item selecionado:{Cores.RESET}")
                print(f"{Cores.CIANO}Nome: {item[1]}{Cores.RESET}")
                print(f"{Cores.AMARELO}Preço: R${item[2]:.2f}{Cores.RESET}")
                
                # 6. Confirmar remoção
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
                
            # 7. Perguntar se deseja remover outro item
            continuar = input(f"\n{Cores.VERDE}Remover outro item? (S/N): {Cores.RESET}").lower()
            if continuar not in ('s', 'sim'):
                break

    @staticmethod
    def gerenciar_cardapio(database_name: str):
        """Menu principal de gerenciamento do cardápio"""
        while True:
            limpar_tela()
            print(f"\n{Cores.FUNDO_AZUL}{Cores.NEGRITO} GERENCIAMENTO DO CARDÁPIO {Cores.RESET}\n")
            print(f"{Cores.VERDE}1. Adicionar item{Cores.RESET}")
            print(f"{Cores.VERMELHO}2. Remover item{Cores.RESET}")
            print(f"{Cores.AZUL}3. Voltar{Cores.RESET}")
            
            # Processar escolha do usuário
            opcao = input(f"\n{Cores.NEGRITO}Escolha (1-3): {Cores.RESET}").strip()
            
            if opcao == '1':
                janela2.inserir_item_menu(database_name)
            elif opcao == '2':
                janela2.remover_item_menu(database_name)
            elif opcao == '3':
                break
            else:
                print(f"{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                time.sleep(1)