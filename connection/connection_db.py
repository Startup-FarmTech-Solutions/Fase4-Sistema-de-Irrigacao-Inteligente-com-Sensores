import os
import oracledb
import json
from pandas import DataFrame
from dotenv import load_dotenv

load_dotenv()

oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_CLIENT_LIB_DIR"))

class ConnectionDB:
    def __init__(self, can_write=False):
        self.can_write = can_write
        self.connections = {}  # Dicionário para armazenar as conexões
        self.cursors = {}  # Dicionário para armazenar os cursores

    def connect_to_oracle(self, conn_name="ATV_FIAP", dsn=None, schema=None):
        """
        Conecta ao banco de dados Oracle.

        Args:
            conn_name (str, optional): Nome para identificar a conexão. Padrão é "default".
            dsn (str, optional): String de conexão. Se None, tenta construir a partir de .env.
            schema (str, optional): Nome do schema a ser usado nesta conexão.
        Returns:
            cursor: Cursor da conexão estabelecida ou None em caso de erro.
        """
        try:
            if conn_name not in self.connections:
                connection = oracledb.connect(
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASS"),
                    dsn=dsn or os.getenv("DB_DSN"),
                )
                self.connections[conn_name] = connection
                self.cursors[conn_name] = connection.cursor()
                print(f"Conexão '{conn_name}' estabelecida com sucesso!")
            else:
                print(f"Conexão '{conn_name}' já existe, reutilizando.")

            if schema:
                try:
                    self.cursors[conn_name].execute(
                        f"ALTER SESSION SET CURRENT_SCHEMA={schema}"
                    )
                    print(f"Schema da conexão '{conn_name}' alterado para '{schema}'.")
                except oracledb.DatabaseError as e:
                    print(f"Erro ao alterar o schema da conexão '{conn_name}': {e}")
            return self.cursors[conn_name]

        except oracledb.DatabaseError as e:
            print(f"Erro ao conectar '{conn_name}': {e}")
            return None

    def close(self, conn_name="ATV_FIAP"):
        """
        Fecha a conexão e o cursor especificados.

        Args:
            conn_name (str, optional): Nome da conexão a ser fechada. Padrão é "default".
        """
        if conn_name in self.cursors:
            self.cursors[conn_name].close()
            del self.cursors[conn_name]
        if conn_name in self.connections:
            self.connections[conn_name].close()
            del self.connections[conn_name]
            print(f"Conexão '{conn_name}' fechada.")

    def close_all(self):
        """Fecha todas as conexões e cursores."""
        for conn_name in list(self.connections.keys()):
            self.close(conn_name)

    def is_connected(self, conn_name="ATV_FIAP"):
        """
        Verifica se a conexão especificada está ativa.

        Args:
            conn_name (str, optional): Nome da conexão a ser verificada. Padrão é "default".

        Returns:
            bool: True se a conexão estiver ativa, False caso contrário.
        """
        if conn_name not in self.connections:
            return False
        try:
            self.connections[conn_name].ping()
            return True
        except oracledb.Error:
            return False

    def get_cursor(self, conn_name="ATV_FIAP"):
        """
        Retorna o cursor associado à conexão especificada.

        Args:
            conn_name (str, optional): Nome da conexão para obter o cursor. Padrão é "default".

        Returns:
            cursor: O cursor da conexão ou None se a conexão não existir.
        """
        return self.cursors.get(conn_name)

    def fetch_all(self, query: str, conn_name="ATV_FIAP") -> list:
        """Executa uma query e retorna todos os resultados como uma lista."""
        cursor = self.get_cursor(conn_name)
        if cursor:
            cursor.execute(query)
            return cursor.fetchall()
        return []

    def fetch_dataframe(self, query: str, conn_name="default") -> DataFrame:
        cursor = self.get_cursor(conn_name)
        if cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0].lower() for col in cursor.description]
            return DataFrame(rows, columns=columns)
        return DataFrame()

    def fetch_json(self, query: str, conn_name="ATV_FIAP") -> str:
        """Executa uma query e retorna os resultados como uma string JSON."""
        cursor = self.get_cursor(conn_name)
        if cursor:
            cursor.execute(query)
            columns = [col[0].lower() for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return json.dumps(rows, default=str)
        return ""

    def write(self, query: str, conn_name="ATV_FIAP"):
        """Executa uma query de escrita (INSERT, UPDATE, DELETE)."""
        if not self.can_write:
            raise Exception("Esta conexão está em modo somente leitura.")
        cursor = self.get_cursor(conn_name)
        if cursor:
            cursor.execute(query)
            self.commit(conn_name)  # Chama o método commit para confirmar a transação

    def execute_ddl(self, query: str, conn_name="ATV_FIAP"):
        """Executa uma query DDL (CREATE, DROP, ALTER)."""
        cursor = self.get_cursor(conn_name)
        if cursor:
            cursor.execute(query)
            self.commit(conn_name)  # Chama o método commit para confirmar a transação

    def commit(self, conn_name="ATV_FIAP"):
        """
        Confirma a transação atual no banco de dados.

        Args:
            conn_name (str, optional): Nome da conexão a ser confirmada.  Padrão é "ATV_FIAP".
        """
        if conn_name not in self.connections:
            raise Exception(f"Conexão '{conn_name}' não encontrada.")  # Lança exceção se a conexão não existir
        try:
            self.connections[conn_name].commit()
            # print(f"Transação da conexão '{conn_name}' confirmada.")
        except oracledb.Error as e:
            print(f"Erro ao confirmar a transação da conexão '{conn_name}': {e}")
            raise  # Re-lança a exceção para tratamento adicional, se necessário

    def rollback(self, conn_name="ATV_FIAP"):
        """
        Desfaz a transação atual no banco de dados.
        """
        if conn_name not in self.connections:
            raise Exception(f"Conexão '{conn_name}' não encontrada.")
        try:
            self.connections[conn_name].rollback()
            print(f"Transação '{conn_name}' desfeita no banco de dados.")
        except oracledb.Error as e:
            print(f"Erro ao desfazer a transação '{conn_name}': {e}")
            raise

def main():
    db = ConnectionDB(can_write=True)

    conn_name = "ATV_FIAP"
    db.connect_to_oracle(conn_name=conn_name)

    if db.is_connected(conn_name=conn_name):
        print("✅ Conexão com o banco de dados Oracle bem-sucedida!")

        try:
            cursor = db.get_cursor(conn_name)
            cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
            schema_atual = cursor.fetchone()[0]
            print(f"O schema atual da conexão '{conn_name}' é: {schema_atual}")

            # Suas consultas de dados aqui
            df_sensores = db.fetch_dataframe("SELECT * FROM sensor", conn_name=conn_name)
            print("Dados dos Sensores:\n", df_sensores)

            df_areas = db.fetch_dataframe("SELECT * FROM area_plantio", conn_name=conn_name)
            print("Dados das Áreas de Plantio:\n", df_areas)

        except oracledb.Error as e:
            print(f"Erro ao executar operações: {e}")
        finally:
            db.close_all()
            print("Todas as conexões foram fechadas")
    else:
        print("❌ Falha na conexão com o banco de dados.")

if __name__ == '__main__':
    main()
