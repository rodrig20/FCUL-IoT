import os
import io
import psycopg2
from psycopg2 import pool
import logging


class Database:
    """
    A static class to manage database interaction,
    including a thread-safe connection pool
    """

    __db_pool = None
    __logger = logging.getLogger("database")
    __logger.setLevel(logging.INFO)

    @classmethod
    def __get_db_pool(cls):
        """
        Initializes and returns the connection pool
        This method is private to the class
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
        """Gets a connection from the pool"""
        try:
            pool = cls.__get_db_pool()
            return pool.getconn()
        except Exception as e:
            cls.__logger.error(f"Error getting connection from pool: {e}")
            return None

    @classmethod
    def __release_db_connection(cls, conn):
        """Returns a connection to the pool"""
        if conn:
            pool = cls.__get_db_pool()
            pool.putconn(conn)

    @classmethod
    def __db_is_empty(cls, table_name):
        """Checks if the specified table exists and has data"""
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error(
                f"Could not get DB connection to check if database table {table_name} is empty"
            )
            return True

        try:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s
                    );
                """, (table_name,)
                )
                table_exists = cur.fetchone()[0]

                if not table_exists:
                    return True

                # Check if table has any rows
                cur.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cur.fetchone()[0]
                return count == 0
        except Exception as e:
            cls.__logger.error(f"Error checking if database table {table_name} is empty: {e}")
            return True  # Assume it's empty if there's an error
        finally:
            cls.__release_db_connection(conn)

    @classmethod
    def init_db(cls):
        """Initializes all database tables"""
        cls.__logger.info("Initializing all database tables...")
        cls.init_ev_with_stations_table()
        cls.init_stations_table()

    @classmethod
    def init_ev_with_stations_table(cls):
        """Initializes the ev_with_stations table from the original CSV"""
        if not cls.__db_is_empty("ev_with_stations"):
            cls.__logger.info("Table ev_with_stations is not empty")
            return
        cls.__logger.info("Table ev_with_stations is empty. Initializing database from CSV...")
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

                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    header_line = f.readline().strip()

                header = [col.strip() for col in header_line.split(";")]
                column_names = [
                    f'"{col.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_per_").replace("__", "_")}"'
                    for col in header
                ]

                # Define data types for each column (based on a CSV analysis)
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

                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    csv_content_str = f.read().splitlines(True)[1:]
                    processed_content = "".join(csv_content_str).replace(",", ".")

                # Use a string buffer in memory as if it were a file
                string_io_file = io.StringIO(processed_content)

                # 4. Use the COPY command for high-performance bulk insertion
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
            raise e  # Propagate the error so the application knows initialization failed
        finally:
            if conn:
                cls.__release_db_connection(conn)

    @classmethod
    def init_stations_table(cls):
        """Initializes the charging stations table from the CSV file EV-Stations_with_ids_coords.csv"""
        if not cls.__db_is_empty("stations"):
            cls.__logger.info("Table stations is not empty")
            return
        cls.__logger.info("Table stations is empty. Initializing stations database from CSV...")
        conn = None
        try:
            conn = cls.__get_db_connection()
            if not conn:
                cls.__logger.error(
                    "Could not get DB connection for stations CSV initialization"
                )
                return

            with conn.cursor() as cur:
                csv_path = "EV-Stations_with_ids_coords.csv"
                table_name = "stations"

                cls.__logger.info(f"Initializing stations database from {csv_path}...")

                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    header_line = f.readline().strip()

                header = [col.strip() for col in header_line.split(";")]
                column_names = [
                    f'"{col.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_per_").replace("__", "_")}"'
                    for col in header
                ]

                column_types = [
                    "TEXT",
                    "TEXT",
                    "TEXT",
                    "TEXT",
                    "REAL",
                    "REAL",
                    "REAL",
                    "INTEGER",
                    "INTEGER",
                    "INTEGER",
                    "TEXT",
                ]

                column_definitions = [
                    f"{name} {ctype}" for name, ctype in zip(column_names, column_types)
                ]

                create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
                cur.execute(create_table_sql)
                cls.__logger.info(f"Table '{table_name}' created")

                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    csv_content_str = f.read().splitlines(True)[1:]
                    processed_content = "".join(csv_content_str).replace(",", ".")

                # Use a string buffer in memory as if it were a file
                string_io_file = io.StringIO(processed_content)

                # 4. Use the COPY command for high-performance bulk insertion
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
            cls.__logger.error(f"Error initializing stations database from CSV: {e}")
            raise e  # Propagate the error so the application knows initialization failed
        finally:
            if conn:
                cls.__release_db_connection(conn)

    @classmethod
    def get_info_by_username(cls, username: str):
        """
        Returns all information from the ev_with_stations table for a specific user
        """
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error(f"Could not get DB connection to fetch info for user {username}")
            return {}

        try:
            with conn.cursor() as cur:
                headers = cls.get_headers()
                cur.execute("SELECT * FROM ev_with_stations WHERE user_id = %s;", (username,))
                rows = cur.fetchall()

                # Filter out the user_id header
                filtered_headers = [header for header in headers if header != 'user_id']

                # Convert rows to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if header != 'user_id':
                            row_dict[header] = row[i]
                    data.append(row_dict)

                return {"headers": filtered_headers, "data": data}
        except Exception as e:
            cls.__logger.error(f"Error fetching info for user {username} from database: {e}")
            return {}
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

    @classmethod
    def get_stations(cls):
        """
        Returns all stations with ID, latitude, and longitude
        """
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch stations")
            return []

        try:
            with conn.cursor() as cur:
                # Execute the query to get Station ID, Latitude, and Longitude
                cur.execute("SELECT \"station_id\", \"latitude\", \"longitude\" FROM stations;")
                rows = cur.fetchall()

                # Convert to list of dictionaries
                stations = []
                for row in rows:
                    station = {
                        "station_id": row[0],
                        "latitude": row[1],
                        "longitude": row[2]
                    }
                    stations.append(station)

                return stations
        except Exception as e:
            cls.__logger.error(f"Error fetching stations from database: {e}")
            return []
        finally:
            cls.__release_db_connection(conn)

    @classmethod
    def get_stations_for_user(cls, username: str):
        """
        Returns all stations with a boolean indicating
        whether the user has already visited that station
        """
        conn = cls.__get_db_connection()
        if not conn:
            cls.__logger.error("Could not get DB connection to fetch stations for user")
            return []

        try:
            with conn.cursor() as cur:
                # Get all stations (without spatial limitation)
                cur.execute("""
                    SELECT
                        s."station_id",
                        s."latitude",
                        s."longitude"
                    FROM stations s
                """)

                rows = cur.fetchall()

                # Convert to list of dictionaries
                stations = []
                for row in rows:
                    station = {
                        "station_id": row[0],
                        "latitude": row[1],
                        "longitude": row[2],
                        "visited": False  # Temporary value, will be updated below
                    }
                    stations.append(station)

                # Now, update the visit status for the relevant stations
                if stations:  # Only if there are stations to check
                    # Get the stations visited by the user
                    station_ids = [station['station_id'] for station in stations]
                    if station_ids:  # Only proceed if there are station IDs
                        placeholders = ','.join(['%s'] * len(station_ids))
                        cur.execute(f"""
                            SELECT DISTINCT e.charging_station_id
                            FROM ev_with_stations e
                            WHERE e.user_id = %s
                            AND e.charging_station_id IN ({placeholders})
                        """, [username] + station_ids)

                        visited_station_ids = [row[0] for row in cur.fetchall()]

                        # Update the visit status for each station
                        for station in stations:
                            if station['station_id'] in visited_station_ids:
                                station['visited'] = True

                cls.__logger.info(f"Fetched {len(stations)} stations for user {username}")
                return stations
        except Exception as e:
            cls.__logger.error(f"Error fetching stations for user {username} from database: {e}")
            return []
        finally:
            cls.__release_db_connection(conn)


Database.init_db()
