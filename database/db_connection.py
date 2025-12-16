"""
Database connection and utility functions for PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info("Database connection established")
            return self.conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_connection(self):
        """Get or create database connection"""
        if self.conn is None or self.conn.closed:
            self.connect()
        return self.conn
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
                return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")


# Global database instance
db = DatabaseConnection()

