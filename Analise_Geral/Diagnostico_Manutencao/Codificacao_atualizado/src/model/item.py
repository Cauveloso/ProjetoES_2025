from model.database import Database
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

class Item:
    def __init__(self, nome: str, preco: float, tipo: str, descricao: str) -> None:
        self.nome = nome
        self.preco = preco
        self.tipo = tipo
        self.descricao = descricao
    
    @staticmethod
    def mostrar_itens_menu(database_name: str) -> object:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, nome, preco, tipo, descricao FROM itens;')
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return 'I1'
    
    @staticmethod
    def insert_into_item(database_name: str, data: object) -> bool:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO itens (nome, preco, tipo, descricao) 
                    VALUES (?,?,?,?);
                ''', (data.nome, data.preco, data.tipo, data.descricao))
                conn.commit()
                return True
        except Exception as e:
            print(e)
            return 'I2'
    
    @staticmethod
    def insert_into_itens_pedidos(database_name: str, data: list) -> bool:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO itens_pedidos (id_pedido, id_item) 
                    VALUES (?,?);
                ''', (data[0], data[1]))
                conn.commit()
                return True
        except Exception as e:
            print(e)
            return 'I3'
    
    @staticmethod
    def search_into_itens_pedidos_id(database_name: str, indice: int) -> object:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT i.nome, i.preco, i.tipo, i.descricao
                    FROM pedidos p
                    JOIN itens_pedidos ip ON ip.id_pedido = p.id
                    JOIN itens i ON ip.id_item = i.id
                    WHERE p.id = {indice};
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return 'I4'
        
    @staticmethod
    def valor_item(database_name: str, indice: int) -> object:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT preco FROM itens WHERE id = {indice};')
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return 'I5'
    
    @staticmethod
    def search_item_id(database_name: str, indice: int) -> object:
        try:
            with Database.conect_database(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT nome, tipo, descricao, preco 
                    FROM itens WHERE id = {indice};
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return 'I6'