import sqlite3
from sqlite3 import Error
import sys
from pathlib import Path
from datetime import datetime

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

class DatabaseControler:
    @staticmethod
    def conect_database(database_name: str) -> sqlite3.Connection:
        """Estabelece conexão com o banco de dados e cria tabelas se não existirem"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            DatabaseControler.create_table_itens(conn)
            DatabaseControler.create_table_pedidos(conn)
            DatabaseControler.create_table_itens_pedidos(conn)
            DatabaseControler.migrate_database(conn)
            return conn
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            if conn:
                conn.close()
            sys.exit(1)

    @staticmethod
    def create_table_itens(conn: sqlite3.Connection) -> None:
        """Cria tabela de itens do cardápio"""
        sql = """
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            UNIQUE(nome)
        );
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela itens: {e}")
            raise

    @staticmethod
    def create_table_pedidos(conn: sqlite3.Connection) -> None:
        """Cria tabela de pedidos com a estrutura correta"""
        sql = """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            data TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            delivery BOOLEAN NOT NULL DEFAULT 0,
            endereco_entrega TEXT,
            observacoes TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela pedidos: {e}")
            raise

    @staticmethod
    def create_table_itens_pedidos(conn: sqlite3.Connection) -> None:
        """Cria tabela de relacionamento itens-pedidos com constraints adequadas"""
        sql = """
        CREATE TABLE IF NOT EXISTS itens_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            observacoes TEXT,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES itens(id),
            UNIQUE(pedido_id, item_id)
        );
        """
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela itens_pedidos: {e}")
            raise

    @staticmethod
    def migrate_database(conn: sqlite3.Connection) -> None:
        """Atualiza a estrutura do banco de dados de forma robusta"""
        try:
            cursor = conn.cursor()
            
            # Migração para tabela itens
            cursor.execute("PRAGMA table_info(itens)")
            itens_columns = [column[1] for column in cursor.fetchall()]
            
            if 'ativo' not in itens_columns:
                cursor.execute("ALTER TABLE itens ADD COLUMN ativo BOOLEAN DEFAULT 1")
            
            # Migração para tabela pedidos
            cursor.execute("PRAGMA table_info(pedidos)")
            pedidos_columns = [column[1] for column in cursor.fetchall()]
            
            # Verificar e migrar de ValorTotal para total se necessário
            if 'ValorTotal' in pedidos_columns and 'total' not in pedidos_columns:
                cursor.execute("ALTER TABLE pedidos RENAME COLUMN ValorTotal TO total")
            elif 'total' not in pedidos_columns:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN total REAL NOT NULL DEFAULT 0")
            
            # Adicionar outras colunas se necessário
            for column in ['delivery', 'endereco_entrega', 'observacoes', 'data_criacao']:
                if column not in pedidos_columns:
                    if column == 'delivery':
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {column} BOOLEAN NOT NULL DEFAULT 0")
                    elif column == 'data_criacao':
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {column} TEXT DEFAULT CURRENT_TIMESTAMP")
                    else:
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {column} TEXT")
            
            # Migração para tabela itens_pedidos
            cursor.execute("PRAGMA table_info(itens_pedidos)")
            itens_pedidos_columns = [column[1] for column in cursor.fetchall()]
            
            if 'preco_unitario' not in itens_pedidos_columns:
                try:
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # Criar tabela temporária
                    cursor.execute("""
                    CREATE TABLE temp_itens_pedidos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pedido_id INTEGER NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_unitario REAL NOT NULL,
                        observacoes TEXT,
                        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
                        FOREIGN KEY (item_id) REFERENCES itens(id)
                    );
                    """)
                    
                    # Copiar dados existentes com preço unitário
                    cursor.execute("""
                    INSERT INTO temp_itens_pedidos (id, pedido_id, item_id, quantidade, preco_unitario, observacoes)
                    SELECT 
                        ip.id, 
                        ip.pedido_id, 
                        ip.item_id, 
                        ip.quantidade, 
                        COALESCE(ip.preco_unitario, i.preco, 0) as preco_unitario,
                        COALESCE(ip.observacoes, '') as observacoes
                    FROM itens_pedidos ip
                    JOIN itens i ON ip.item_id = i.id;
                    """)
                    
                    # Remover tabela antiga e renomear a nova
                    cursor.execute("DROP TABLE itens_pedidos")
                    cursor.execute("ALTER TABLE temp_itens_pedidos RENAME TO itens_pedidos")
                    
                    # Recriar índices e constraints
                    cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pedido_item 
                    ON itens_pedidos (pedido_id, item_id);
                    """)
                    
                    conn.commit()
                except Error as e:
                    conn.rollback()
                    print(f"Erro durante migração de itens_pedidos: {e}")
                    raise
            
            conn.commit()
            
        except Error as e:
            print(f"Erro durante migração do banco: {e}")
            conn.rollback()
            raise

    @staticmethod
    def get_item_price(conn: sqlite3.Connection, item_id: int) -> float:
        """Obtém o preço de um item do cardápio"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT preco FROM itens WHERE id = ? AND ativo = 1", (item_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            raise ValueError(f"Item ID {item_id} não encontrado ou inativo")
        except Error as e:
            print(f"Erro ao buscar preço do item: {e}")
            raise

    @staticmethod
    def insert_pedido(conn: sqlite3.Connection, cliente: str, itens: list, 
                     delivery: bool = False, endereco: str = None, 
                     observacoes: str = None) -> int:
        """Insere um novo pedido com tratamento robusto de erros"""
        try:
            cursor = conn.cursor()
            
            # Validar e preparar itens
            validated_items = []
            for item in itens:
                if not isinstance(item, dict):
                    raise ValueError("Cada item deve ser um dicionário")
                
                if 'id' not in item or 'quantidade' not in item:
                    raise ValueError("Item deve conter 'id' e 'quantidade'")
                
                preco = item.get('preco')
                if preco is None:
                    preco = DatabaseControler.get_item_price(conn, item['id'])
                
                validated_items.append({
                    'id': item['id'],
                    'quantidade': item['quantidade'],
                    'preco': preco,
                    'observacoes': item.get('observacoes', '')
                })
            
            # Calcular total
            total = sum(item['preco'] * item['quantidade'] for item in validated_items)
            
            # Inserir pedido principal
            cursor.execute(
                """INSERT INTO pedidos 
                (cliente, data, total, status, delivery, endereco_entrega, observacoes) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (cliente, datetime.now().isoformat(), total, 'pendente', 
                 delivery, endereco, observacoes)
            )
            pedido_id = cursor.lastrowid
            
            # Inserir itens do pedido
            for item in validated_items:
                cursor.execute(
                    """INSERT INTO itens_pedidos 
                    (pedido_id, item_id, quantidade, preco_unitario, observacoes) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (pedido_id, item['id'], item['quantidade'], 
                     item['preco'], item['observacoes'])
                )
            
            conn.commit()
            return pedido_id
            
        except Error as e:
            print(f"Erro ao inserir pedido: {e}")
            conn.rollback()
            raise
        except ValueError as e:
            print(f"Erro de validação: {e}")
            conn.rollback()
            raise

    @staticmethod
    def validate_item(conn: sqlite3.Connection, item_id: int) -> bool:
        """Verifica se um item existe e está ativo"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM itens WHERE id = ? AND ativo = 1", (item_id,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Erro ao validar item: {e}")
            raise