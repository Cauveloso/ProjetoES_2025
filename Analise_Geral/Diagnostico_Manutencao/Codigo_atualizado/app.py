from datetime import date
import time
import sys
import sqlite3
from pathlib import Path

# Configuração de imports relativos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Importações do projeto
from model.pedido import Pedido
from model.item import Item
from model.database import Database
from controler.database_controler import DatabaseControler
from controler.pedido_controler import PedidoControler
from controler.relatorio_controler import RelatorioControler
from controler.item_controler import ItemControler
from view.janela1 import janela1
from view.janela2 import janela2

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
    FUNDO_VERMELHO = '\033[41m' # Fundo vermelho

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================

def limpar_tela():
    """Limpa o conteúdo do terminal"""
    print("\n" * 50)

def mostrar_cabecalho():
    """Exibe o cabeçalho estilizado do sistema"""
    print(f'''
    {Cores.AZUL}{Cores.NEGRITO}
    ╔════════════════════════════════════════════╗
    ║          BEM-VINDO AO PIZZA MAIS           ║
    ║           - Criando Sonhos -               ║
    ║                                            ║
    ║ Estabelecimento: Pizza Ciclano             ║
    ║ "Seus sonhos tem formato e borda"          ║
    ╚════════════════════════════════════════════╝
    {Cores.RESET}''')

def mostrar_menu_principal():
    """Exibe o menu principal com opções coloridas"""
    print(f'''
    {Cores.AZUL}{Cores.NEGRITO}MENU PRINCIPAL{Cores.RESET}
    {Cores.VERDE}1. CADASTRAR NOVO PEDIDO{Cores.RESET}
    {Cores.AZUL}2. CONSULTAR PEDIDOS{Cores.RESET}
    {Cores.AMARELO}3. GERAR RELATÓRIO DE VENDAS{Cores.RESET}
    {Cores.VERMELHO}4. GERENCIAR CARDÁPIO{Cores.RESET}
    {Cores.CIANO}5. AJUDA/SUPORTE{Cores.RESET}
    {Cores.VERMELHO}6. SAIR DO SISTEMA{Cores.RESET}
    ''')

# ==============================================
# FUNÇÕES DE BANCO DE DADOS
# ==============================================

def inicializar_banco(database_name):
    """
    Verifica e cria a estrutura do banco de dados se necessário
    Garante que todas as tabelas existam com a estrutura correta
    """
    print("🔧 Verificando estrutura do banco de dados...")
    
    conn = sqlite3.connect(database_name)
    try:
        # Criar tabelas básicas
        DatabaseControler.create_table_itens(conn)
        DatabaseControler.create_table_pedidos(conn)
        
        # Verificar tabela de relacionamento
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='itens_pedidos'")
        
        if cursor.fetchone():
            # Se tabela existe, verificar colunas
            cursor.execute("PRAGMA table_info(itens_pedidos)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'pedido_id' not in columns or 'item_id' not in columns:
                print("🔄 Recriando tabela itens_pedidos com estrutura correta...")
                cursor.execute("DROP TABLE IF EXISTS itens_pedidos")
                DatabaseControler.create_table_itens_pedidos(conn)
        else:
            # Se tabela não existe, criar
            DatabaseControler.create_table_itens_pedidos(conn)
        
        conn.commit()
        print("✅ Banco de dados verificado e pronto para uso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

# ==============================================
# FUNÇÕES DE RELATÓRIO
# ==============================================

def gerar_relatorio(database_name: str):
    """Gera um relatório de vendas em formato PDF"""
    limpar_tela()
    print(f"\n{Cores.AMARELO}»»» GERANDO RELATÓRIO «««{Cores.RESET}\n")
    
    try:
        # 1. Coletar dados para o relatório
        dados = RelatorioControler.preparar_dados_relatorio(database_name)
        
        if not dados["pedidos"]:
            print(f"{Cores.VERMELHO}❌ Nenhum pedido válido encontrado para relatório!{Cores.RESET}")
            input(f"\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")
            return
        
        # 2. Gerar nome único para o arquivo
        timestamp = str(time.time()).replace('.', '')[:10]
        nome_arquivo = f'RelatorioVendas_{timestamp}.pdf'
        
        # 3. Criar PDF
        if RelatorioControler.gerar_pdf(nome_arquivo, dados):
            print(f"\n{Cores.VERDE}✅ Relatório gerado com sucesso: '{nome_arquivo}'{Cores.RESET}")
        else:
            print(f"\n{Cores.VERMELHO}❌ Falha ao gerar relatório!{Cores.RESET}")
            
    except Exception as e:
        print(f"\n{Cores.VERMELHO}Erro crítico: {str(e)}{Cores.RESET}")
    
    input(f"\n{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")

# ==============================================
# FUNÇÃO PRINCIPAL
# ==============================================

if __name__ == "__main__":
    # 1. Configuração inicial do banco de dados
    database = Database('TESTE.db')
    inicializar_banco(database.name)
    DatabaseControler.corrigir_totais_pedidos('Teste.db')

    # 2. Verificação adicional da estrutura do banco
    try:
        conn = DatabaseControler.conect_database(database.name)
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

    # ==============================================
    # LOOP PRINCIPAL DO SISTEMA
    # ==============================================
    while True:
        try:
            # 1. Exibir interface
            limpar_tela()
            mostrar_cabecalho()
            mostrar_menu_principal()
            
            # 2. Obter escolha do usuário
            opcao = input(f"\n{Cores.NEGRITO}Escolha uma opção (1-6): {Cores.RESET}").strip()
            
            # 3. Processar opção selecionada
            if opcao == '1':  # Novo pedido
                limpar_tela()
                janela1.mostrar_janela1(database.name)
                
            elif opcao == '2':  # Consultar pedidos
                limpar_tela()
                janela1.consultar_pedidos(database.name)
                
            elif opcao == '3':  # Gerar relatório
                gerar_relatorio(database.name)
                
            elif opcao == '4':  # Gerenciar cardápio
                janela2.gerenciar_cardapio(database.name)
                
            elif opcao == '5':  # Ajuda/Suporte
                janela2.menu_ajuda_suporte(database.name)
                
            elif opcao == '6':  # Sair do sistema
                confirmar = input(f"{Cores.VERMELHO}Tem certeza que deseja sair? (S/N): {Cores.RESET}").lower()
                if confirmar == 's':
                    print(f"\n{Cores.AZUL}Encerrando sistema...{Cores.RESET}")
                    break
                    
            else:  # Opção inválida
                print(f"\n{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                time.sleep(1)
                
        except Exception as e:
            print(f"\n{Cores.VERMELHO}Erro: {str(e)}{Cores.RESET}")
            input(f"{Cores.AZUL}Pressione Enter para continuar...{Cores.RESET}")