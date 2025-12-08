import os
import mariadb
from loguru import logger


def get_db_connection():
    """
    ສ້າງ MariaDB connection ແບບງ່າຍໆ
    
    Returns:
        mariadb.Connection: Database connection object
    """
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_SIT_HOST"),
            user=os.getenv("DB_SIT_USER"),
            password=os.getenv("DB_SIT_PASSWORD"),
            database=os.getenv("DB_SIT_NAME"),
            port=int(os.getenv("DB_SIT_PORT")),
        )
        logger.info("✅ Connected to MariaDB successfully")
        return connection
        
    except mariadb.Error as e:
        logger.error(f"❌ Error connecting to MariaDB: {e}")
        raise


def close_connection(connection):
    """
    ປິດ connection
    
    Args:
        connection: Database connection ທີ່ຕ້ອງການປິດ
    """
    if connection:
        try:
            connection.close()
            logger.info("👋 Connection closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing connection: {e}")
