from model.item import Item
import sqlite3
from typing import List, Tuple, Optional

class ItemControler:
    """
    Controlador responsável por gerenciar operações relacionadas a itens do cardápio
    e itens associados a pedidos.
    
    Métodos estáticos para:
    - Consulta de itens
    - Inserção/remoção de itens
    - Operações com itens de pedidos
    """

    # ==================== OPERAÇÕES BÁSICAS DE ITENS ====================
    
    @staticmethod
    def create_item(nome: str, preco: float, tipo: str, descricao: str) -> Optional[Item]:
        """
        Cria um novo objeto Item com validação
        
        Args:
            nome: Nome do item
            preco: Preço do item (deve ser positivo)
            tipo: Categoria do item
            descricao: Descrição detalhada
            
        Returns:
            Item: Objeto Item criado ou None em caso de erro
        """
        try:
            return Item(nome, preco, tipo, descricao)
        except ValueError as e:
            print(f"Erro ao criar item: {e}")
            return None

    @staticmethod
    def insert_into_item(database_name: str, item: Item) -> bool:
        """
        Insere um item no banco de dados
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item: Objeto Item a ser inserido
            
        Returns:
            bool: True se inserido com sucesso, False caso contrário
        """
        return Item.insert_into_item(database_name, item)

    @staticmethod
    def remover_item(database_name: str, item_id: int) -> bool:
        """
        Remove um item do cardápio se não estiver em pedidos ativos
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_id: ID do item a ser removido
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Verifica se o item está em algum pedido
            cursor.execute("SELECT COUNT(*) FROM itens_pedidos WHERE item_id = ?", (item_id,))
            if cursor.fetchone()[0] > 0:
                print("Item não pode ser removido pois está em pedidos existentes")
                return False
                
            # Remove o item
            cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Erro ao remover item: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ==================== CONSULTAS DE ITENS ====================
    
    @staticmethod
    def mostrar_itens_menu(database_name: str) -> List[Tuple]:
        """
        Retorna todos os itens ativos do cardápio ordenados por tipo e nome
        
        Args:
            database_name: Nome do arquivo do banco de dados
            
        Returns:
            List[Tuple]: Lista de tuplas com informações dos itens
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, preco, tipo, descricao
                FROM itens
                WHERE ativo = 1
                ORDER BY tipo, nome
            """)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar itens do cardápio: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def search_item_id(database_name: str, item_id: int) -> Optional[Tuple]:
        """
        Busca um item específico pelo ID
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_id: ID do item a ser buscado
            
        Returns:
            Tuple: Tupla com informações do item ou None se não encontrado
        """
        return Item.search_item_id(database_name, item_id)

    @staticmethod
    def obter_preco_item(database_name: str, item_id: int) -> float:
        """
        Obtém o preço de um item do cardápio
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_id: ID do item
            
        Returns:
            float: Preço do item ou 0.0 se não encontrado
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("SELECT preco FROM itens WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            return result[0] if result else 0.0
        except sqlite3.Error as e:
            print(f"Erro ao buscar preço do item: {e}")
            return 0.0
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_item_name(database_name: str, item_id: int) -> str:
        """
        Obtém o nome de um item pelo ID
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_id: ID do item
            
        Returns:
            str: Nome do item ou 'Item Desconhecido' se não encontrado
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM itens WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            return result[0] if result else "Item Desconhecido"
        except sqlite3.Error as e:
            print(f"Erro ao buscar nome do item: {e}")
            return "Item Desconhecido"
        finally:
            if conn:
                conn.close()

    # ==================== OPERAÇÕES COM ITENS DE PEDIDOS ====================
    
    @staticmethod
    def insert_into_itens_pedidos(database_name: str, data: tuple) -> bool:
        """
        Insere um item em um pedido
        
        Args:
            database_name: Nome do arquivo do banco de dados
            data: Tupla com dados do item (pedido_id, item_id, quantidade, preco_unitario, observacoes)
            
        Returns:
            bool: True se inserido com sucesso, False caso contrário
        """
        return Item.insert_into_itens_pedidos(database_name, data)

    @staticmethod
    def search_into_itens_pedidos_id(database_name: str, pedido_id: int) -> List[Tuple]:
        """
        Busca todos os itens de um pedido específico
        
        Args:
            database_name: Nome do arquivo do banco de dados
            pedido_id: ID do pedido
            
        Returns:
            List[Tuple]: Lista de tuplas com informações dos itens do pedido
        """
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ip.id, ip.item_id, ip.quantidade, ip.preco_unitario, ip.observacoes
                FROM itens_pedidos ip
                WHERE ip.pedido_id = ?
            """, (pedido_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao buscar itens do pedido: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def valor_item(database_name: str, item_id: int) -> float:
        """
        Obtém o valor de um item com tratamento de erro
        
        Args:
            database_name: Nome do arquivo do banco de dados
            item_id: ID do item
            
        Returns:
            float: Valor do item ou 0.0 em caso de erro
        """
        result = Item.valor_item(database_name, item_id)
        return result[0][0] if result and result != 'I5' else 0.0