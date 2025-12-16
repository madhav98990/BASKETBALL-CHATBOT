"""
Database Setup Script
Run this to initialize and seed the PostgreSQL database
Note: If using Docker, the database will be automatically initialized.
This script is useful for manual setup or re-seeding data.
"""
import psycopg2
import os
import time
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be ready"""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database='postgres',
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                connect_timeout=2
            )
            conn.close()
            return True
        except Exception:
            if i < max_retries - 1:
                logger.info(f"Waiting for database... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                return False
    return False

def setup_database():
    """Setup database schema and seed data"""
    try:
        # Wait for database to be ready (useful for Docker)
        logger.info("Checking database connection...")
        if not wait_for_db():
            logger.error("Database is not available. Make sure PostgreSQL is running.")
            logger.info("If using Docker, run: docker-compose up -d")
            raise ConnectionError("Database connection failed")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',  # Connect to default database first
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        logger.info("Creating database if it doesn't exist...")
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            logger.info(f"Database {DB_CONFIG['database']} created")
        else:
            logger.info(f"Database {DB_CONFIG['database']} already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to the new database and run schema
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Read and execute schema
        logger.info("Running schema...")
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        
        conn.commit()
        logger.info("Schema executed successfully")
        
        # Read and execute seed data
        logger.info("Seeding data...")
        with open('database/seed_data.sql', 'r') as f:
            seed_sql = f.read()
            # Split by semicolons and execute each statement
            statements = seed_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        logger.warning(f"Error executing statement: {e}")
                        continue
        
        conn.commit()
        logger.info("Data seeded successfully")
        
        cursor.close()
        conn.close()
        
        logger.info("Database setup complete!")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise


if __name__ == "__main__":
    setup_database()

