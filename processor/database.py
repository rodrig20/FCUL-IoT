import os
import io
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extensions import connection
import logging


class Database:
    """A static class to manage database interactions, including a thread-safe connection pool"""

    __db_pool = None
    __logger = logging.getLogger("database")
    __logger.setLevel(logging.INFO)

    @classmethod
    def __get_db_pool(cls) -> ThreadedConnectionPool:
        """Initializes and returns the connection pool

        Returns:
            ThreadedConnectionPool: The database connection pool instance
        """
        if cls.__db_pool is None:
            try:
                cls.__db_pool = ThreadedConnectionPool(
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
    def __get_db_connection(cls) -> connection | None:
        """Obtains a connection from the pool

        Returns:
            connection or None: Database connection if successful, None otherwise
        """
        try:
            pool = cls.__get_db_pool()
            return pool.getconn()
        except Exception as e:
            cls.__logger.error(f"Error getting connection from pool: {e}")
            return None

    @classmethod
    def __release_db_connection(cls, conn: connection) -> None:
        """Returns a connection back to the pool

        Args:
            conn: Database connection to return to the pool
        """
        if conn:
            pool = cls.__get_db_pool()
            pool.putconn(conn)

    @classmethod
    def __db_is_empty(cls):
        """Checks if the 'ev_with_stations' table exists and has data

        Returns:
            bool: True if the table doesn't exist or is empty, False otherwise
        """
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

                row = cur.fetchone()

                if not row:
                    return True

                table_exists = row[0]

                if not table_exists:
                    return True

                # Check if table has any rows
                cur.execute("SELECT COUNT(*) FROM ev_with_stations;")
                row = cur.fetchone()

                if not row:
                    return True

                count = row[0]

                return count == 0
        except Exception as e:
            cls.__logger.error(f"Error checking if database is empty: {e}")
            return True  # Assume it's empty if there's an error
        finally:
            cls.__release_db_connection(conn)

    @classmethod
    def init_db(cls) -> None:
        """Initializes the database from a CSV file

        This method checks if the database is empty, and if so, creates the table
        and loads data from the CSV file 'dataset-EV_with_stations.csv'
        """
        # Check if the database table already exists and has data
        if not cls.__db_is_empty():
            cls.__logger.info("DB is not empty")
            return

        cls.__logger.info("DB is empty. Initializing database from CSV...")

        conn = None
        try:
            # Get a connection from the database connection pool
            conn = cls.__get_db_connection()
            if not conn:
                cls.__logger.error("Could not get DB connection for CSV initialization")
                return

            # Execute database operations using the connection
            with conn.cursor() as cur:
                csv_path = "dataset-EV_with_stations.csv"
                table_name = "ev_with_stations"

                cls.__logger.info(f"Initializing database from {csv_path}...")

                # Read and process the CSV header line to determine column names
                with open(csv_path, "r", encoding="utf-8") as f:
                    header_line = f.readline().strip()

                # Split and clean the header columns
                header = [col.strip() for col in header_line.split(";")]

                # Format column names to be valid PostgreSQL identifiers
                column_names = [
                    f'"{col.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_per_").replace("__", "_")}"'
                    for col in header
                ]

                # Define data types for each column (based on CSV analysis)
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

                # Combine column names and types into table definition
                column_definitions = [
                    f"{name} {ctype}" for name, ctype in zip(column_names, column_types)
                ]

                # Create the table with all necessary columns and types
                create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
                cur.execute(create_table_sql)
                cls.__logger.info(f"Table '{table_name}' created")

                # Read the CSV content, skipping the header line
                with open(csv_path, "r", encoding="utf-8") as f:
                    csv_content_str = f.read().splitlines(True)[1:]
                    # Replace commas with periods for decimal numbers
                    processed_content = "".join(csv_content_str).replace(",", ".")

                # Use an in-memory string buffer as if it were a file
                string_io_file = io.StringIO(processed_content)

                # Use the COPY command for high-performance bulk insertion
                cur.execute("SET datestyle = 'DMY';")
                copy_sql = f"COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER ';', HEADER FALSE, NULL '')"
                cur.copy_expert(sql=copy_sql, file=string_io_file)

                # Commit the transaction to save all changes to the database
                conn.commit()
                cls.__logger.info(
                    f"Successfully loaded data from '{csv_path}' into '{table_name}'"
                )

        except Exception as e:
            # Rollback the transaction in case of error to maintain database consistency
            if conn:
                conn.rollback()
            cls.__logger.error(f"Error initializing database from CSV: {e}")
            raise e  # Propagate the error so the application knows initialization failed
        finally:
            # Always return the connection to the pool
            if conn:
                cls.__release_db_connection(conn)

    @classmethod
    def get_all_info(cls) -> list[tuple]:
        """Returns all information from the ev_with_stations table as list of tuples

        Returns:
            list[tuple]: All rows from the ev_with_stations table as a list of tuples,
                   or empty list if there's an error
        """
        # Get a connection from the database connection pool
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch all info")
            return []

        try:
            # Execute a query to fetch all rows from the ev_with_stations table
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ev_with_stations;")
                # Fetch all results from the executed query
                rows = cur.fetchall()

                # Convert rows to list and return
                result = [row for row in rows]

                return result
        except Exception as e:
            cls.__logger.error(f"Error fetching all info from database: {e}")
            return []
        finally:
            # Always return the connection to the pool
            cls.__release_db_connection(conn)

    @classmethod
    def get_headers(cls) -> list:
        """Returns the column names from the ev_with_stations table

        Returns:
            list: Column names from the ev_with_stations table,
                   or empty list if there's an error
        """
        # Get a connection from the database connection pool
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch headers")
            return []

        try:
            # Execute a query to get column information without returning any rows
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ev_with_stations LIMIT 0;")
                # Extract column names from cursor description
                if cur.description:
                    # Extract the name of each column from the description tuple
                    headers = [desc[0] for desc in cur.description]
                else:
                    # If there's no description (shouldn't happen with valid table), return empty list
                    headers = []

                return headers
        except Exception as e:
            cls.__logger.error(f"Error fetching headers from database: {e}")
            return []
        finally:
            # Always return the connection to the pool
            cls.__release_db_connection(conn)


Database.init_db()
