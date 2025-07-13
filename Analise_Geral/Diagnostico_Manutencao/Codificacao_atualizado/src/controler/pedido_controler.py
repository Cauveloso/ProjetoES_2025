import sqlite3
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from model.pedido import Pedido

class PedidoControler:
    
    @staticmethod
    def insert_into_pedidos(database_name: str, data: object) -> bool:
        """Adiciona um novo pedido ao banco de dados"""
        try:
            return Pedido.insert_into_pedidos(database_name, data)
        except Exception as e:
            print(f"Erro ao inserir pedido: {e}")
            return False
    
    @staticmethod
    def search_in_pedidos_all(database_name: str) -> list[dict]:
        """Recupera todos os pedidos"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, data, cliente, telefone, endereco, valor_total, status
                FROM pedidos
                ORDER BY id DESC
            """)
            columns = ['id', 'data', 'cliente', 'telefone', 'endereco', 'valor_total', 'status']
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao buscar pedidos: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def search_in_pedidos_id(database_name: str, pedido_id: int) -> dict:
        """Busca um pedido específico"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, data, cliente, telefone, endereco, valor_total, status
                FROM pedidos 
                WHERE id = ?
            """, (pedido_id,))
            columns = ['id', 'data', 'cliente', 'telefone', 'endereco', 'valor_total', 'status']
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        except sqlite3.Error as e:
            print(f"Erro ao buscar pedido: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_pedido_status_id(database_name: str, pedido_id: int, status: str) -> bool:
        """Atualiza status de um pedido"""
        status_map = {
            1: 'preparando',
            2: 'entregue',
            3: 'cancelado'
        }
        status = status_map.get(status, status)
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
    
    @staticmethod
    def get_id_all(database_name: str) -> list[int]:
        """Retorna lista com todos os IDs de pedidos"""
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

    @staticmethod
    def remover_pedido(database_name: str, pedido_id: int) -> bool:
        """Remove um pedido específico"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM itens_pedidos WHERE id_pedido = ?", (pedido_id,))
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
        """Remove todos os pedidos"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM itens_pedidos")
            cursor.execute("DELETE FROM pedidos")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao limpar pedidos: {e}")
            return False
        finally:
            if conn:
                conn.close()