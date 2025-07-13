import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Configuração de imports e caminhos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from model.pedido import Pedido

class PedidoControler:
    
    # ==================== OPERAÇÕES BÁSICAS DE PEDIDOS ====================
    
    @staticmethod
    def insert_into_pedidos(database_name: str, pedido_data: dict) -> bool:
        """
        Insere um novo pedido no banco de dados
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_data: Dicionário com os dados do pedido
            
        Returns:
            bool: True se a inserção foi bem-sucedida, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Prepara valores padrão caso não sejam fornecidos
            valores = (
                pedido_data.get('cliente', ''),
                pedido_data.get('telefone', ''),
                pedido_data.get('data', datetime.now().isoformat()),
                pedido_data.get('valor_total', 0),
                pedido_data.get('status', 'pendente'),
                pedido_data.get('delivery', False),
                pedido_data.get('endereco', 'Retirada no local'),
                pedido_data.get('observacoes', '')
            )
            
            cursor.execute("""
                INSERT INTO pedidos 
                (cliente, telefone, data, valor_total, status, delivery, endereco, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, valores)
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao inserir pedido: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    # ==================== CONSULTAS E BUSCAS ====================
    
    @staticmethod
    def search_in_pedidos_all(database_name: str, incluir_entregues: bool = False) -> list:
        """
        Busca todos os pedidos no banco de dados
        
        Args:
            database_name: Nome do arquivo do banco de dados
            incluir_entregues: Se True, inclui pedidos com status 'entregue'
            
        Returns:
            list: Lista de dicionários contendo os pedidos
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Monta a query conforme os parâmetros
            query = "SELECT * FROM pedidos"
            if not incluir_entregues:
                query += " WHERE status != 'entregue'"
            query += " ORDER BY data DESC"
            
            cursor.execute(query)
            
            # Converte os resultados para dicionários
            colunas = [column[0] for column in cursor.description]
            return [dict(zip(colunas, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
            
        finally:
            if conn:
                conn.close()

    @staticmethod
    def search_in_pedidos_id(database_name: str, pedido_id: int, incluir_entregues: bool = True) -> dict:
        """
        Busca um pedido específico pelo ID
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_id: ID do pedido a ser buscado
            incluir_entregues: Se True, inclui pedidos com status 'entregue'
            
        Returns:
            dict: Dicionário com os dados do pedido ou None se não encontrado
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            query = "SELECT * FROM pedidos WHERE id = ?"
            if not incluir_entregues:
                query += " AND status != 'entregue'"
                
            cursor.execute(query, (pedido_id,))
            
            colunas = [column[0] for column in cursor.description]
            resultado = cursor.fetchone()
            return dict(zip(colunas, resultado)) if resultado else None
            
        except Exception as e:
            print(f"Erro ao buscar pedido: {e}")
            return None
            
        finally:
            if conn:
                conn.close()

    # ==================== ATUALIZAÇÃO DE STATUS ====================
    
    @staticmethod
    def update_pedido_status_id(database_name: str, pedido_id: int, status: str) -> bool:
        """
        Atualiza o status de um pedido
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_id: ID do pedido a ser atualizado
            status: Novo status (pode ser número ou string)
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        # Mapeamento de status numérico para string
        mapa_status = {
            1: 'preparando',
            2: 'entregue',
            3: 'cancelado'
        }
        
        # Converte status numérico para string, se necessário
        status = mapa_status.get(status, status)
        
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE pedidos 
                SET status = ?
                WHERE id = ?
            """, (status, pedido_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    # ==================== OPERAÇÕES COM IDs ====================
    
    @staticmethod
    def get_id_all(database_name: str) -> list[int]:
        """
        Obtém todos os IDs de pedidos ordenados do mais recente para o mais antigo
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            list: Lista de IDs de pedidos
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM pedidos ORDER BY id DESC")
            return [row[0] for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar IDs: {e}")
            return []
            
        finally:
            if conn:
                conn.close()

    # ==================== REMOÇÃO DE PEDIDOS ====================
    
    @staticmethod
    def remover_pedido(database_name: str, pedido_id: int) -> bool:
        """
        Remove um pedido específico e seus itens associados
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_id: ID do pedido a ser removido
            
        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Remove primeiro os itens associados ao pedido
            cursor.execute("DELETE FROM itens_pedidos WHERE pedido_id = ?", (pedido_id,))
            # Remove o pedido
            cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Erro ao remover pedido: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    @staticmethod
    def limpar_todos_pedidos(database_name: str) -> bool:
        """
        Remove todos os pedidos e itens de pedidos do banco de dados
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Remove todos os itens de pedidos
            cursor.execute("DELETE FROM itens_pedidos")
            # Remove todos os pedidos
            cursor.execute("DELETE FROM pedidos")
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao limpar pedidos: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    # ==================== OPERAÇÕES COM ITENS DE PEDIDOS ====================
    
    @staticmethod
    def inserir_item_pedido(database_name: str, item_data: dict) -> bool:
        """
        Insere um item em um pedido com validação de estrutura
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_data: Dicionário com os dados do item
            
        Returns:
            bool: True se a inserção foi bem-sucedida, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Verifica se a tabela tem a estrutura correta
            cursor.execute("PRAGMA table_info(itens_pedidos)")
            colunas = [column[1] for column in cursor.fetchall()]
            
            if 'pedido_id' not in colunas:
                raise ValueError("Estrutura da tabela itens_pedidos incorreta")
            
            # Prepara os valores para inserção
            valores = (
                item_data['pedido_id'],
                item_data['item_id'],
                item_data['quantidade'],
                item_data['preco_unitario'],
                item_data.get('observacoes', '')
            )
            
            cursor.execute("""
                INSERT INTO itens_pedidos 
                (pedido_id, item_id, quantidade, preco_unitario, observacoes)
                VALUES (?, ?, ?, ?, ?)
            """, valores)
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao inserir item do pedido: {e}")
            return False
            
        except ValueError as e:
            print(f"Erro de estrutura: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    # ==================== STATUS AVANÇADOS ====================
    
    @staticmethod
    def atualizar_status_pedido(database_name: str, pedido_id: int, novo_status: str) -> bool:
        """
        Atualiza o status de um pedido sem arquivamento
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_id: ID do pedido a ser atualizado
            novo_status: Novo status para o pedido
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE pedidos SET status = ? WHERE id = ?",
                (novo_status.lower(), pedido_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False
            
        finally:
            if conn:
                conn.close()

    @staticmethod
    def listar_pedidos_entregues(database_name: str) -> list:
        """
        Lista todos os pedidos com status 'entregue'
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            list: Lista de dicionários contendo os pedidos entregues
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM pedidos 
                WHERE status = 'entregue'
                ORDER BY data DESC
            """)
            
            colunas = [column[0] for column in cursor.description]
            return [dict(zip(colunas, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Erro ao buscar pedidos entregues: {e}")
            return []
            
        finally:
            if conn:
                conn.close()