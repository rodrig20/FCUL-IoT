import os
import io
import psycopg2
from psycopg2 import pool
import logging


class Database:
    """
    Uma classe estática para gerir a interação com a base de dados,
    incluindo um pool de conexões thread-safe
    """

    __db_pool = None
    __logger = logging.getLogger("database")
    __logger.setLevel(logging.INFO)

    @classmethod
    def __get_db_pool(cls):
        """
        Inicializa e retorna o connection pool
        Este método é privado para a classe
        """
        if cls.__db_pool is None:
            try:
                cls.__db_pool = pool.ThreadedConnectionPool(
                    1,  # minconn
                    10,  # maxconn
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host="db",
                    port="5432",
                    database=os.getenv("DB_NAME")
                )
                cls.__logger.info("Database connection pool created successfully")
            except psycopg2.OperationalError as e:
                cls.__logger.error(f"Error creating database connection pool: {e}")
                raise
        return cls.__db_pool

    @classmethod
    def __get_db_connection(cls):
        """Obtém uma conexão do pool"""
        try:
            pool = cls.__get_db_pool()
            return pool.getconn()
        except Exception as e:
            cls.__logger.error(f"Error getting connection from pool: {e}")
            return None

    @classmethod
    def __release_db_connection(cls, conn):
        """Devolve uma conexão ao pool"""
        if conn:
            pool = cls.__get_db_pool()
            pool.putconn(conn)

    @classmethod
    def __db_is_empty(cls):
        """Verifica se a tabela 'ev_with_stations' existe e tem dados"""
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error(
                "Could not get DB connection to check if database is empty"
            )
            return True

        try:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'ev_with_stations'
                    );
                """
                )
                table_exists = cur.fetchone()[0]

                if not table_exists:
                    return True

                # Check if table has any rows
                cur.execute("SELECT COUNT(*) FROM ev_with_stations;")
                count = cur.fetchone()[0]
                return count == 0
        except Exception as e:
            cls.__logger.error(f"Error checking if database is empty: {e}")
            return True  # Assume it's empty if there's an error
        finally:
            cls.__release_db_connection(conn)

    @classmethod
    def init_db(cls):
        """Inicializa o banco de dados a partir de um CSV"""
        if not cls.__db_is_empty():
            cls.__logger.info("DB is not empty")
            return
        cls.__logger.info("DB is empty. Initializing database from CSV...")
        conn = None
        try:
            conn = cls.__get_db_connection()
            if not conn:
                cls.__logger.error(
                    "Could not get DB connection for CSV initialization"
                )
                return

            with conn.cursor() as cur:
                csv_path = "dataset-EV_with_stations.csv"
                table_name = "ev_with_stations"

                cls.__logger.info(f"Initializing database from {csv_path}...")

                with open(csv_path, "r", encoding="utf-8") as f:
                    header_line = f.readline().strip()

                header = [col.strip() for col in header_line.split(";")]
                column_names = [
                    f'"{col.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_per_").replace("__", "_")}"'
                    for col in header
                ]

                # Definir os tipos de dados para cada coluna (baseado numa análise do CSV)
                column_types = [
                    "TEXT",
                    "TEXT",
                    "REAL",
                    "TEXT",
                    "TIMESTAMP",
                    "TIMESTAMP",
                    "REAL",
                    "REAL",
                    "REAL",
                    "REAL",
                    "TEXT",
                    "TEXT",
                    "REAL",
                    "REAL",
                    "REAL",
                    "REAL",
                    "INTEGER",
                ]

                column_definitions = [
                    f"{name} {ctype}" for name, ctype in zip(column_names, column_types)
                ]

                create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
                cur.execute(create_table_sql)
                cls.__logger.info(f"Table '{table_name}' created")

                with open(csv_path, "r", encoding="utf-8") as f:
                    csv_content_str = f.read().splitlines(True)[1:]
                    processed_content = "".join(csv_content_str).replace(",", ".")

                # Usar um buffer de string em memória como se fosse um ficheiro
                string_io_file = io.StringIO(processed_content)

                # 4. Usar o comando COPY para uma inserção em massa de alta performance
                cur.execute("SET datestyle = 'DMY';")
                copy_sql = f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER ';', HEADER FALSE, NULL '')"
                cur.copy_expert(sql=copy_sql, file=string_io_file)

                conn.commit()
                cls.__logger.info(
                    f"Successfully loaded data from '{csv_path}' into '{table_name}'"
                )

        except Exception as e:
            if conn:
                conn.rollback()
            cls.__logger.error(f"Error initializing database from CSV: {e}")
            raise e  # Propagar o erro para que a aplicação saiba que a inicialização falhou
        finally:
            if conn:
                cls.__release_db_connection(conn)

    @classmethod
    def get_all_info(cls):
        """
        Retorna todas as informações da tabela ev_with_stations como tupla de tuplas
        """
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch all info")
            return ()

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ev_with_stations;")
                rows = cur.fetchall()

                # Converter as linhas em tuplas e retornar como tupla
                result = tuple(tuple(row) for row in rows)

                return result
        except Exception as e:
            cls.__logger.error(f"Error fetching all info from database: {e}")
            return ()
        finally:
            cls.__release_db_connection(conn)

    @classmethod
    def get_headers(cls):
        """
        Retorna os nomes das colunas da tabela ev_with_stations
        """
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch headers")
            return ()

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ev_with_stations LIMIT 0;")
                headers = tuple([desc[0] for desc in cur.description])

                return headers
        except Exception as e:
            cls.__logger.error(f"Error fetching headers from database: {e}")
            return ()
        finally:
            cls.__release_db_connection(conn)


Database.init_db()
