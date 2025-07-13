import sqlite3
from sqlite3 import Error
import sys
from pathlib import Path
from datetime import datetime

# Configuração de imports e caminhos
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

class DatabaseControler:
    """
    Classe principal para controle do banco de dados que gerencia todas as operações SQLite.
    Utiliza métodos estáticos para operações de banco para evitar gerenciamento de estado.
    """
    
    # ==================== CONEXÃO COM BANCO DE DADOS ====================
    
    @staticmethod
    def conect_database(database_name: str) -> sqlite3.Connection:
        """Estabelece conexão com o banco e garante o esquema adequado"""
        conn = None
        try:
            conn = sqlite3.connect(database_name)
            
            # Garante que todas as tabelas necessárias existam com estrutura correta
            DatabaseControler.create_table_itens(conn)
            DatabaseControler.create_table_pedidos(conn)
            DatabaseControler.create_table_itens_pedidos(conn)
            
            # Executa migrações de dados necessárias
            DatabaseControler.corrigir_tabela_itens_pedidos(conn)
            DatabaseControler.migrate_database(conn)
            
            return conn
        except Error as e:
            print(f"Erro na conexão com o banco: {e}")
            if conn:
                conn.close()
            sys.exit(1)
    
    # ==================== CRIAÇÃO DE TABELAS ====================
    
    @staticmethod
    def create_table_itens(conn: sqlite3.Connection) -> None:
        """Cria tabela de itens do cardápio"""
        sql = """
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            categoria TEXT,
            ativo BOOLEAN DEFAULT 1,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(nome)
        );
        """
        try:
            conn.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela 'itens': {e}")
            raise

    @staticmethod
    def create_table_pedidos(conn: sqlite3.Connection) -> None:
        """Cria tabela de pedidos"""
        sql = """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            telefone TEXT NOT NULL DEFAULT '',
            data TEXT NOT NULL,
            valor_total REAL NOT NULL DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            delivery BOOLEAN NOT NULL DEFAULT 0,
            endereco TEXT DEFAULT 'Retirada no local',
            observacoes TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            conn.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela 'pedidos': {e}")
            raise

    @staticmethod
    def create_table_itens_pedidos(conn: sqlite3.Connection) -> None:
        """Cria tabela de relacionamento itens-pedidos"""
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
            conn.execute(sql)
            conn.commit()
        except Error as e:
            print(f"Erro ao criar tabela 'itens_pedidos': {e}")
            raise

    # ==================== MIGRAÇÕES DE DADOS ====================
    
    @staticmethod
    def corrigir_tabela_itens_pedidos(conn: sqlite3.Connection):
        """Corrige a estrutura da tabela itens_pedidos se necessário"""
        try:
            cursor = conn.cursor()
            
            # Verifica a estrutura atual da tabela
            cursor.execute("PRAGMA table_info(itens_pedidos)")
            colunas = [column[1] for column in cursor.fetchall()]
            
            if 'pedido_id' not in colunas:
                # Cria tabela temporária com estrutura correta
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS itens_pedidos_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pedido_id INTEGER NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_unitario REAL NOT NULL,
                        observacoes TEXT,
                        FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
                        FOREIGN KEY (item_id) REFERENCES itens(id)
                    )
                """)
                
                # Migra dados da estrutura antiga se necessário
                if 'id_pedido' in colunas:
                    cursor.execute("""
                        INSERT INTO itens_pedidos_temp 
                        SELECT id, id_pedido, item_id, quantidade, preco_unitario, observacoes 
                        FROM itens_pedidos
                    """)
                
                # Substitui a tabela antiga
                cursor.execute("DROP TABLE itens_pedidos")
                cursor.execute("ALTER TABLE itens_pedidos_temp RENAME TO itens_pedidos")
                
                # Recria índices
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pedido_item 
                    ON itens_pedidos (pedido_id, item_id)
                """)
                
                conn.commit()
                print("Estrutura da tabela itens_pedidos corrigida com sucesso!")
                
        except Error as e:
            print(f"Erro ao corrigir tabela itens_pedidos: {e}")
            conn.rollback()
            raise

    @staticmethod
    def migrate_database(conn: sqlite3.Connection) -> None:
        """Executa todas as migrações necessárias no banco de dados"""
        try:
            cursor = conn.cursor()
            
            # Migrações para tabela de itens
            cursor.execute("PRAGMA table_info(itens)")
            colunas_itens = [column[1] for column in cursor.fetchall()]
            if 'ativo' not in colunas_itens:
                cursor.execute("ALTER TABLE itens ADD COLUMN ativo BOOLEAN DEFAULT 1")
            
            # Migrações para tabela de pedidos
            cursor.execute("PRAGMA table_info(pedidos)")
            colunas_pedidos = [column[1] for column in cursor.fetchall()]
            
            # Corrige nomes de colunas e adiciona colunas faltantes
            if 'ValorTotal' in colunas_pedidos and 'total' not in colunas_pedidos:
                cursor.execute("ALTER TABLE pedidos RENAME COLUMN ValorTotal TO total")
            elif 'total' not in colunas_pedidos:
                cursor.execute("ALTER TABLE pedidos ADD COLUMN total REAL NOT NULL DEFAULT 0")
            
            # Adiciona outras colunas que podem estar faltando
            for coluna in ['delivery', 'endereco_entrega', 'observacoes', 'data_criacao']:
                if coluna not in colunas_pedidos:
                    if coluna == 'delivery':
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {coluna} BOOLEAN NOT NULL DEFAULT 0")
                    elif coluna == 'data_criacao':
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {coluna} TEXT DEFAULT CURRENT_TIMESTAMP")
                    else:
                        cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {coluna} TEXT")
            
            # Migrações para tabela itens_pedidos
            cursor.execute("PRAGMA table_info(itens_pedidos)")
            colunas_itens_pedidos = [column[1] for column in cursor.fetchall()]
            
            if 'preco_unitario' not in colunas_itens_pedidos:
                try:
                    cursor.execute("BEGIN TRANSACTION")
                    
                    # Cria tabela temporária com coluna de preço
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
                    
                    # Migra dados com preços corretos
                    cursor.execute("""
                    INSERT INTO temp_itens_pedidos 
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
                    
                    # Substitui tabela antiga
                    cursor.execute("DROP TABLE itens_pedidos")
                    cursor.execute("ALTER TABLE temp_itens_pedidos RENAME TO itens_pedidos")
                    
                    # Recria índice
                    cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pedido_item 
                    ON itens_pedidos (pedido_id, item_id);
                    """)
                    
                    conn.commit()
                except Error as e:
                    conn.rollback()
                    print(f"Erro na migração de itens_pedidos: {e}")
                    raise
            
            conn.commit()
            
        except Error as e:
            print(f"Erro na migração do banco: {e}")
            conn.rollback()
            raise

    # ==================== OPERAÇÕES COM PEDIDOS ====================
    
    @staticmethod
    def insert_pedido(conn: sqlite3.Connection, cliente: str, itens: list, 
                    delivery: bool = False, endereco: str = None, 
                    observacoes: str = None) -> int:
        """Insere um novo pedido com cálculo correto do total"""
        try:
            cursor = conn.cursor()
            total = 0.0
            itens_validados = []
            
            # Valida itens e calcula total
            for item in itens:
                if not isinstance(item, dict) or 'id' not in item or 'quantidade' not in item:
                    raise ValueError("Formato de item inválido")
                
                preco = DatabaseControler.get_item_price(conn, item['id'])
                quantidade = item['quantidade']
                
                itens_validados.append({
                    'id': item['id'],
                    'quantidade': quantidade,
                    'preco': preco,
                    'observacoes': item.get('observacoes', '')
                })
                
                total += preco * quantidade
            
            # Insere registro principal do pedido
            cursor.execute(
                """INSERT INTO pedidos 
                (cliente, data, total, status, delivery, endereco, observacoes) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (cliente, datetime.now().isoformat(), total, 'pendente', 
                delivery, endereco, observacoes)
            )
            id_pedido = cursor.lastrowid
            
            # Insere itens do pedido
            for item in itens_validados:
                cursor.execute(
                    """INSERT INTO itens_pedidos 
                    (pedido_id, item_id, quantidade, preco_unitario, observacoes) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (id_pedido, item['id'], item['quantidade'], 
                    item['preco'], item['observacoes'])
                )
            
            conn.commit()
            return id_pedido
            
        except Error as e:
            print(f"Erro ao inserir pedido: {e}")
            conn.rollback()
            raise

    # ==================== OPERAÇÕES COM ITENS ====================
    
    @staticmethod
    def get_item_price(conn: sqlite3.Connection, item_id: int) -> float:
        """Obtém o preço atual de um item do cardápio"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT preco FROM itens WHERE id = ? AND ativo = 1", (item_id,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]
            raise ValueError(f"Item ID {item_id} não encontrado ou inativo")
        except Error as e:
            print(f"Erro ao buscar preço do item: {e}")
            raise

    @staticmethod
    def validate_item(conn: sqlite3.Connection, item_id: int) -> bool:
        """Verifica se um item existe e está ativo"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM itens WHERE id = ? AND ativo = 1", (item_id,))
            return cursor.fetchone() is not None
        except Error as e:
            print(f"Erro na validação do item: {e}")
            raise
    
    # ==================== INTEGRIDADE DO BANCO ====================
    
    @staticmethod
    def diagnosticar_pedidos(database_name: str):
        """Diagnostica problemas de integridade nos dados dos pedidos"""
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Encontra pedidos com total zero
            cursor.execute("SELECT id, total FROM pedidos WHERE total = 0")
            zeros = cursor.fetchall()
            print(f"Pedidos com total zero: {zeros}")
            
            # Mostra itens desses pedidos
            for id_pedido, _ in zeros:
                cursor.execute("""
                    SELECT ip.item_id, ip.quantidade, ip.preco_unitario, i.nome, i.preco
                    FROM itens_pedidos ip
                    JOIN itens i ON ip.item_id = i.id
                    WHERE ip.pedido_id = ?
                """, (id_pedido,))
                itens = cursor.fetchall()
                print(f"Itens do pedido {id_pedido}:")
                for item in itens:
                    print(item)
            
            # Encontra discrepâncias no cálculo do total
            cursor.execute("""
                SELECT p.id, p.total, SUM(ip.quantidade * ip.preco_unitario) as calculado
                FROM pedidos p
                JOIN itens_pedidos ip ON p.id = ip.pedido_id
                GROUP BY p.id
                HAVING p.total != calculado
            """)
            discrepâncias = cursor.fetchall()
            print(f"Discrepâncias encontradas: {discrepâncias}")
            
        except Error as e:
            print(f"Erro no diagnóstico: {e}")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def corrigir_totais_pedidos(database_name: str):
        """Corrige totais dos pedidos baseado nos itens"""
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Encontra pedidos com totais incorretos
            cursor.execute("""
                SELECT p.id, p.total, SUM(ip.quantidade * ip.preco_unitario) as total_correto
                FROM pedidos p
                JOIN itens_pedidos ip ON p.id = ip.pedido_id
                GROUP BY p.id
                HAVING p.total != total_correto
            """)
            
            discrepâncias = cursor.fetchall()
            
            # Atualiza totais incorretos
            for id_pedido, total_atual, total_correto in discrepâncias:
                print(f"Corrigindo pedido {id_pedido}: de {total_atual} para {total_correto}")
                cursor.execute(
                    "UPDATE pedidos SET total = ? WHERE id = ?",
                    (total_correto, id_pedido)
                )
            
            conn.commit()
            print(f"Pedidos corrigidos: {len(discrepâncias)}")
            
        except Error as e:
            print(f"Erro na correção de totais: {e}")
            conn.rollback()
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def atualizar_estrutura_banco(database_name: str):
        """Atualiza estrutura do banco para novos valores de status"""
        try:
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            
            # Verifica se atualização é necessária
            cursor.execute("PRAGMA table_info(pedidos)")
            colunas = [column[1] for column in cursor.fetchall()]
            if 'status' not in colunas:
                return  # Já atualizado

            # Cria nova tabela com constraints adequadas
            cursor.execute("""
            CREATE TABLE pedidos_nova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('preparando', 'pronto', 'entregue')),
                delivery BOOLEAN NOT NULL DEFAULT 0,
                endereco TEXT,
                valor_total REAL NOT NULL DEFAULT 0
            )
            """)

            # Migra dados com conversão de status
            cursor.execute("""
            INSERT INTO pedidos_nova 
            SELECT id, cliente, data, 
                CASE 
                    WHEN status = 'pendente' THEN 'preparando'
                    ELSE status
                END,
                delivery, endereco, valor_total
            FROM pedidos
            """)

            # Substitui tabela antiga
            cursor.execute("DROP TABLE pedidos")
            cursor.execute("ALTER TABLE pedidos_nova RENAME TO pedidos")
            conn.commit()
            print("✅ Estrutura da tabela de pedidos atualizada com sucesso!")
        except Exception as e:
            print(f"❌ Erro na atualização da estrutura: {e}")
            conn.rollback()
        finally:
            if conn:
                conn.close()