import sqlite3
from datetime import datetime
class Pedido:
    def __init__(self, cliente: str, telefone: str, status: str, delivery: str, 
                 endereco: str, data: str, total: float):
        self.cliente = cliente
        self.telefone = telefone
        self.status = status
        self.delivery = delivery
        self.endereco = endereco
        self.data = data
        self.total = total

    @staticmethod
    def insert_into_pedidos(database_name: str, pedido_data: dict) -> bool:
        """Insere um novo pedido no banco de dados"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pedidos 
                (cliente, telefone, data, total, status, delivery, endereco_entrega, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pedido_data.get('cliente', ''),
                pedido_data.get('telefone', ''),
                pedido_data.get('data', datetime.now().isoformat()),
                pedido_data.get('total', 0),
                pedido_data.get('status', 'pendente'),
                pedido_data.get('delivery', False),
                pedido_data.get('endereco_entrega', None),
                pedido_data.get('observacoes', '')
            ))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao inserir pedido: {e}")
            return False
        finally:
            if conn:
                conn.close()