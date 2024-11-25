import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path

def migrate_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    # Get database URLs
    sqlite_path = Path(__file__).parent / "jobs.sqlite"
    postgres_url = os.getenv('DATABASE_URL')

    if not postgres_url:
        raise ValueError("DATABASE_URL environment variable not set")

    if not sqlite_path.exists():
        print("No SQLite database found to migrate")
        return

    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    pg_conn = psycopg2.connect(postgres_url)
    pg_conn.autocommit = False

    try:
        # Migrate each table
        tables = [
            'jobs',
            'candidates',
            'applications',
            'analysis_results',
            'job_matches',
            'screening_reports',
            'recommendations'
        ]

        for table in tables:
            print(f"Migrating {table}...")
            
            # Get data from SQLite
            sqlite_cur = sqlite_conn.cursor()
            sqlite_cur.execute(f"SELECT * FROM {table}")
            rows = sqlite_cur.fetchall()
            
            if not rows:
                print(f"No data in {table} to migrate")
                continue

            # Get column names
            columns = [description[0] for description in sqlite_cur.description]
            
            # Prepare PostgreSQL insert
            pg_cur = pg_conn.cursor()
            placeholders = ','.join(['%s'] * len(columns))
            column_names = ','.join(columns)
            
            # Insert data
            for row in rows:
                query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                pg_cur.execute(query, tuple(row))

        # Commit all changes
        pg_conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        pg_conn.rollback()
        print(f"Error during migration: {str(e)}")
        raise

    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_to_postgres()
