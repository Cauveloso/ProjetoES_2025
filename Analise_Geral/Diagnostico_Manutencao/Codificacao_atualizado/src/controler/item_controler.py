from model.item import Item
import sqlite3

class ItemControler:
    @staticmethod
    def mostrar_itens_menu(database_name: str) -> list:
        return Item.mostrar_itens_menu(database_name)
    
    @staticmethod
    def insert_into_item(database_name: str, item: Item) -> bool:
        return Item.insert_into_item(database_name, item)
    
    @staticmethod
    def insert_into_itens_pedidos(database_name: str, data: tuple) -> bool:
        return Item.insert_into_itens_pedidos(database_name, data)
    
    @staticmethod
    def valor_item(database_name: str, item_id: int) -> float:
        result = Item.valor_item(database_name, item_id)
        return result[0][0] if result and result != 'I5' else 0.0
    
    @staticmethod
    def search_item_id(database_name: str, item_id: int) -> tuple:
        return Item.search_item_id(database_name, item_id)
    
    @staticmethod
    def remover_item(database_name: str, item_id: int) -> bool:
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM itens_pedidos WHERE id_item = ?", (item_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def create_item(nome: str, preco: float, tipo: str, descricao: str) -> Item:
        try:
            return Item(nome, preco, tipo, descricao)
        except ValueError:
            return None